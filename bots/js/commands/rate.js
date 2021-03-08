const { Command } = require('discord-akairo')
const Discord = require('discord.js')
const fetch = require('node-fetch')

const getUsage = require('../utils/getUsage')

function getRMPUrl(campus, q) {
    let schoolName, schoolId

    switch (campus) {
        case 'fh':
            schoolName = 'Foothill+College'
            schoolId = 1581
            break
        case 'da':
            schoolName = 'De+Anza+College'
            schoolId = 1967
            break
        default:
            throw new Error('Unknown Campus')
    }

    const params = new URLSearchParams([
        ['solrformat', 'true'],
        ['rows', '20'],
        ['wt', 'json'],
        ['q', q],
        [
            'qf',
            'teacherfirstname_t^2000+teacherlastname_t^2000+teacherfullname_t^2000+teacherfullname_autosuggest',
        ],
        ['bf', 'pow(total_number_of_ratings_i,2.1)'],
        ['sort', 'score+desc'],
        ['defType', 'edismax'],
        ['siteName', 'rmp'],
        ['group', 'off'],
        ['group.field', 'content_type_s'],
        ['group.limit', '20'],
        ['fq', `schoolname_t:"${schoolName}"`],
        ['fq', `schoolid_s:${schoolId}`],
    ])

    return `https://solr-aws-elb-production.ratemyprofessors.com/solr/rmp/select/?${params
        .toString()
        .replace(/%2B/g, '+')}`
}

async function getProf(campus, q) {
    const response = await fetch(getRMPUrl(campus, q))

    if (response.ok) {
        const docs = (await response.json())['response']['docs']
        return [docs.length > 0 ? docs[0] : null, docs.slice(1)]
    } else {
        console.error(response)
    }
}

function numToStars(sn, reverse = false) {
    const s = []
    let n = (sn && Math.round(parseFloat(sn) * 4) / 4) || 0

    if (reverse) n = 5 - n

    while (true) {
        if (n > 0) {
            if (n >= 1) {
                s.push(':full_moon:')
            } else if (n == 0.75) {
                s.push(
                    !reverse ? ':waning_gibbous_moon:' : ':waxing_gibbous_moon:'
                )
            } else if (n == 0.5) {
                s.push(
                    !reverse ? ':last_quarter_moon:' : ':first_quarter_moon:'
                )
            } else if (n == 0.25) {
                s.push(
                    !reverse
                        ? ':waning_crescent_moon:'
                        : ':waxing_crescent_moon:'
                )
            }
            n--
        } else if (s.length < 5) {
            s.push(':new_moon:')
        }
        if (n <= 0 && s.length == 5) {
            break
        }
    }

    return (reverse ? s.reverse() : s).join(' ')
}

class RateCommand extends Command {
    constructor() {
        super('rate', {
            aliases: ['rate'],
            description: {
                text: 'Search RMP for a professor at a campus.',
                usage: '<campus> <instructor>',
            },
            args: [
                {
                    id: 'campus',
                },
                {
                    id: 'professor',
                    match: 'rest',
                },
                {
                    id: 'full',
                    match: 'flag',
                    flag: '--full',
                },
                {
                    id: 'embed',
                    match: 'flag',
                    flag: '--embed',
                },
            ],
        })
    }

    exec(message, args) {
        if (!args.campus) {
            message.util.send('Usage: `' + getUsage(this) + '`')
            return
        }

        args.campus = args.campus.toLowerCase()

        if (!['fh', 'da'].includes(args.campus)) {
            message.util.send(
                'Campus not found! Available campuses are `fh` and `da`.'
            )
            return
        }

        if (!args.professor) {
            message.util.reply('No professor specified!')
            return
        }

        this.rateProf(message, args)
    }

    async rateProf(message, args) {
        const [prof, others] = await getProf(args.campus, args.professor)
        const full = args.full

        if (!prof) {
            await message.util.reply('No professor found!')
            return
        }

        const id = prof['pk_id']
        const name = prof['teacherfullname_s']
        const dept = prof['teacherdepartment_s']
        const school = prof['schoolname_s']
        const rating = prof['averageratingscore_rf'] || 0
        const easy = prof['averageeasyscore_rf'] || 0
        const numRatings = prof['total_number_of_ratings_i'] || 0

        const embed = new Discord.MessageEmbed()

        const link = `https://www.ratemyprofessors.com/ShowRatings.jsp?tid=${id}`
        const header = `Found professor **${name}** in the **${dept}** department at **${school}**.`
        const alsoFound =
            others.length &&
            `*Also found:* ${others
                .map(
                    (prof) =>
                        `${prof['teacherfullname_s']} (${
                            prof['averageratingscore_rf'] || '?'
                        })`
                )
                .join(', ')}`

        const middleText = numRatings
            ? `Overall Quality: **${rating}** / 5
${numToStars(rating)}

Level of Difficulty: **${easy}** / 5
${numToStars(easy, true)}

Based on **${numRatings}** ratings.`
            : `**No ratings!**`

        const text = `${header}

${middleText}

Go to ${link} for more information.

${alsoFound || ''}
`

        if (full) {
            embed
                .setTitle(name)
                .setURL(link)
                .setDescription(`Here's who I found:`)
                .setColor('#00ff00')

            for (const [attribute, value] of Object.entries(prof)) {
                if (attribute && value) {
                    const excludeList = [
                        'pk_id',
                        'teacherfirstname_t',
                        'teacherlastname_t',
                        'schoolid_s',
                        'tag_id_s_mv',
                        'status_i',
                        'visible_i',
                        'id',
                    ]
                    if (!excludeList.includes(attribute)) {
                        embed.addField(attribute, value, true)
                    }
                }
            }
        } else {
            embed
                .setTitle(name)
                .setURL(link)
                .setDescription(
                    `${header}\n\n Go to [RMP](${link}) for more information.\n\n`
                )
                // .setColor('#00ff00')
                .addFields(
                    {
                        name: 'Overall Rating',
                        value: `${numToStars(rating)} **${rating}** / 5`,
                    },
                    {
                        name: 'Level of Difficulty',
                        value: `${numToStars(easy, true)} **${easy}** / 5`,
                    },
                    {
                        name: `Based on ${numRatings} ratings`,
                        value: `Go to [RMP](${link}) for more information.`,
                    }
                )
                .setFooter(`${alsoFound}`)
        }

        if (full) {
            await message.util.send(header, embed)
        } else {
            if (args.embed) {
                await message.util.send('', embed)
            } else {
                await message.util.send(text)
            }
        }
    }
}

module.exports = RateCommand
