const { Command } = require('discord-akairo')
const Discord = require('discord.js')
const Pagination = require('discord-paginationembed')
const fetch = require('node-fetch')

const { API_URL } = require('../config')
const getUsage = require('../utils/getUsage')
const replaceCampusNames = require('../utils/replaceCampusNames')

// const days = ['M', 'T', 'W', 'Th', 'F', 'S', 'U']
const days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
const Z = '​'
const API_ERROR_MSG =
    "API error: maybe what you asked for doesn't exist or there's something wrong in your command?"
const API_404_ERROR_MSG =
    'that was not found! Make sure you typed the command correctly.'

function sortDays(dayStr) {
    // return dayStr != 'TBA' ? days.map((d) => new RegExp(`${d}($|[A-Z])`).test(dayStr) ? d : '-').join('') : `TBA    `
    return dayStr != 'TBA'
        ? days
              .map((d) =>
                  new RegExp(`${d}($|[A-Z])`).test(dayStr.replace('Th', 'R'))
                      ? d
                      : '-'
              )
              .join('')
        : `TBA    `
}

function addTermYear(url, params) {
    let query = []

    if (params.year) query.push(`year=${params.year}`)
    if (params.term) query.push(`term=${params.term}`)

    return query.length ? url + '?' + query.join('&') : url
}

class FindCommand extends Command {
    constructor() {
        super('find', {
            aliases: ['find', 'dept', 'course'],
            description: {
                text: 'Find departments, courses, and classes at a campus.',
                usage:
                    '<campus> [<department>] [<course>] [--term fall] [--year 2020]',
                examples: [
                    { name: 'List departments at Foothill', cmd: 'fh' },
                    { name: 'List courses in the "CS" dept', cmd: 'fh CS' },
                    {
                        name: 'List info & classes for "CS 2A"',
                        cmd: 'fh CS 2A',
                    },
                ],
            },
            args: [
                {
                    id: 'campus',
                    type: 'string',
                },
                {
                    id: 'dept',
                    type: 'string',
                },
                {
                    id: 'course',
                    type: 'string',
                },
                // {
                //   id: 'classes',
                //   match: 'flag',
                //   flag: '--classes',
                // },
                {
                    id: 'year',
                    match: 'option',
                    flag: '--year',
                },
                {
                    id: 'term',
                    match: 'option',
                    flag: '--term',
                },
            ],
        })
    }

    exec(message, args) {
        args.campus &&
            (args.campus = replaceCampusNames(args.campus.toLowerCase()))
        args.dept && (args.dept = args.dept.toUpperCase())
        args.course && (args.course = args.course.toUpperCase())

        args.term && (args.term = args.term.toLowerCase())

        if (!args.term && !args.year) {
            args.term = 'fall'
            args.year = 2021
        }

        const handleError = (err) => {
            console.error(err)
            return message.util.reply(`An error occurred in the bot!`)
        }

        if (args.campus && args.dept && args.course) {
            this.sendCourse(message, args).catch(handleError)
        } else if (args.campus && args.dept) {
            this.sendDept(message, args).catch(handleError)
        } else if (args.campus) {
            this.sendCampus(message, args).catch(handleError)
        } else {
            message.util.send('Usage: `' + getUsage(this) + '`')
        }
    }

    async sendCampus(message, { campus, ...rest }) {
        const [resDepts] = await this.fetchAll([`/${campus}/depts`], rest)

        if (!resDepts.ok) {
            return this.handleApiError(resDepts, message)
        }

        const depts = await resDepts.json()
        const padAmount = Math.max(...depts.map((dept) => dept.id.length))

        const embed = new Pagination.FieldsEmbed()
            // A must: an array to paginate, can be an array of any type
            .setArray(depts)
            // Set users who can only interact with the instance. Default: `[]` (everyone can interact).
            // If there is only 1 user, you may omit the Array literal.
            .setAuthorizedUsers([message.author.id])
            // A must: sets the channel where to send the embed
            // .setChannel(message.channel)
            .setChannel(message.util)
            // Elements to show per page. Default: 10 elements per page
            .setElementsPerPage(15)
            // Have a page indicator (shown on message content). Default: false
            .setPageIndicator('footer')
            // Format based on the array, in this case we're formatting the page based on each object's `word` property
            .formatField(
                'Departments',
                (dept) =>
                    `\`${Z} ${dept.id.padEnd(padAmount, ' ')} ${Z}\` ${
                        dept.name
                    }`
            )

        embed.embed
            .setTitle(`${campus.toUpperCase()}`)
            .setDescription(
                `Check at ${addTermYear(
                    `https://opencourse.dev/explore/${campus}`,
                    rest
                )}`
            )
            .setFooter(
                'To be replaced',
                'https://avatars0.githubusercontent.com/u/40309595?s=200&v=4'
            )

        embed.build()
    }

    async sendDept(message, { campus, dept, ...rest }) {
        const [resInfo, resCourses] = await this.fetchAll(
            [`/${campus}/depts/${dept}`, `/${campus}/depts/${dept}/courses`],
            rest
        )

        if (!resInfo.ok || !resCourses.ok) {
            return this.handleApiError(
                [resInfo, resCourses].find((res) => !res.ok),
                message
            )
        }

        const deptInfo = await resInfo.json()
        const deptCourses = await resCourses.json()

        const padAmount = Math.max(
            ...deptCourses.map(
                (course) => `${course.dept} ${course.course}`.length
            )
        )
        const embed = new Pagination.FieldsEmbed()
            // A must: an array to paginate, can be an array of any type
            .setArray(deptCourses)
            // Set users who can only interact with the instance. Default: `[]` (everyone can interact).
            // If there is only 1 user, you may omit the Array literal.
            .setAuthorizedUsers([message.author.id])
            // A must: sets the channel where to send the embed
            // .setChannel(message.channel)
            .setChannel(message.util)
            // Elements to show per page. Default: 10 elements per page
            .setElementsPerPage(15)
            // Have a page indicator (shown on message content). Default: false
            .setPageIndicator('footer')
            // Format based on the array, in this case we're formatting the page based on each object's `word` property
            .formatField(
                'Courses',
                (course) =>
                    `\`${Z} ${`${course.dept} ${course.course}`.padEnd(
                        padAmount,
                        ' '
                    )} ${Z}\` ${course.title}`
            )

        embed.embed
            .setTitle(`${deptInfo.id}: ${deptInfo.name}`)
            .setDescription(
                `Courses offered this quarter: ${deptCourses
                    .map((course) => `${course.course}`)
                    .join(', ')}

Check at ${addTermYear(
                    `https://opencourse.dev/explore/${campus}/dept/${dept}`,
                    rest
                )}`
            )
            .setFooter(
                'To be replaced',
                'https://avatars0.githubusercontent.com/u/40309595?s=200&v=4'
            )

        embed.build()
    }

    async sendCourse(message, { campus, dept, course, ...rest }) {
        const includeClasses = true
        const responses = await this.fetchAll(
            [
                `/${campus}/depts/${dept}/courses/${course}`,
                includeClasses &&
                    `/${campus}/depts/${dept}/courses/${course}/classes`,
            ].filter((x) => x),
            rest
        )

        if (responses.some((res) => !res.ok)) {
            return this.handleApiError(
                responses.find((res) => !res.ok),
                message
            )
        }

        const data = await responses[0].json()
        const classData = includeClasses ? await responses[1].json() : []

        const renderClass = (cls) => {
            let times = cls.times
                ? cls.times.map((t, index) => {
                      let ret = ''
                      let instructors = t.instructor
                          .map((i) =>
                              typeof i === 'string'
                                  ? i
                                  : i.display_name || i.full_name
                          )
                          .join(', ')

                      if (
                          t.days === 'TBA' &&
                          t.start_time === 'TBA' &&
                          t.end_time === 'TBA'
                      ) {
                          ret = '`' + Z + ' async ' + Z + '` ' + instructors
                      } else {
                          ret =
                              '`' +
                              sortDays(t.days) +
                              '` ` ' +
                              t.start_time +
                              ' - ' +
                              t.end_time +
                              ' ` ' +
                              instructors
                      }

                      return index === 0
                          ? ret
                          : '`' +
                                Z +
                                '  ^  ' +
                                Z +
                                '` `' +
                                Z +
                                '        ' +
                                Z +
                                '` ' +
                                ret
                  })
                : []

            // return "```\n" +  "`" + Z + cls.CRN.toString().padStart(5, '0') + Z + "` `" + Z + cls.section.padStart(3, ' ') + Z + "` " + times.join('\n') + "\n```"
            // return "`" + Z + cls.CRN.toString().padStart(5, '0') + Z + "` `" + Z + cls.section.padStart(3, ' ') + Z + "` " + times.join('\n')
            const seats =
                cls.seats != undefined
                    ? '`' +
                      cls.seats.toString().padStart(2, ' ') +
                      ' seats' +
                      Z +
                      '` '
                    : ''
            return (
                '`' +
                Z +
                cls.CRN.toString().padStart(5, '0') +
                Z +
                '` ' +
                Z +
                seats +
                times.join('\n')
            )
        }

        const embeds = []
        let curPageContent = ''

        classData.map(renderClass).forEach((str, index, arr) => {
            curPageContent += str + '\n'
            if (curPageContent.length >= 800 || index === arr.length - 1) {
                embeds.push(
                    new Discord.MessageEmbed().addField(
                        'Classes',
                        curPageContent
                    )
                )
                curPageContent = ''
            }
        })

        new Pagination.Embeds()
            .setArray(embeds)
            .setAuthorizedUsers([message.author.id])
            .setChannel(message.util)
            // .setChannel(message.channel)
            .setPageIndicator('footer')
            // Methods below are for customising all embeds
            .setTitle(
                `**${data.dept} ${data.course}**: ${data.title} ${
                    classData && classData[0]
                        ? `(${classData[0].units} units)`
                        : ''
                }`
            )
            .setDescription(
                `Classes this term: **${
                    data.classes ? data.classes.length : '?'
                }**

Check at ${addTermYear(
                    `https://opencourse.dev/explore/${campus}/dept/${dept}/course/${course}`,
                    rest
                )}`
            )
            .setFooter(
                'To be replaced',
                'https://avatars0.githubusercontent.com/u/40309595?s=200&v=4'
            )
            .build()

        // const strings = classData.map(renderClass)

        // let max = 0;
        // let len = 0;

        // for (const str of strings) {
        //   len += str.length
        //   if (len < 800) {
        //     max++
        //   } else {
        //     break
        //   }
        // }

        // const embed = new Pagination.FieldsEmbed()
        //   // A must: an array to paginate, can be an array of any type
        //   // .setArray(classData)
        //   .setArray(strings)
        //   // Set users who can only interact with the instance. Default: `[]` (everyone can interact).
        //   // If there is only 1 user, you may omit the Array literal.
        //   .setAuthorizedUsers([message.author.id])
        //   // A must: sets the channel where to send the embed
        //   .setChannel(message.channel)
        //   // Elements to show per page. Default: 10 elements per page
        //   // .setElementsPerPage(10)
        //   .setElementsPerPage(max)
        //   // Have a page indicator (shown on message content). Default: false
        //   .setPageIndicator('footer')
        //   // Format based on the array, in this case we're formatting the page based on each object's `word` property
        //   // .formatField('Classes', renderClass)
        //   .formatField('Classes', x => x)

        //       embed.embed
        //         .setTitle(`**${data.dept} ${data.course}**: ${data.title}`)
        //         .setDescription(
        // `Classes this term: **${data.classes ? data.classes.length : '?'}**

        // Check at https://opencourse.dev/explore/${campus}/dept/${dept}/course/${course}`
        //         )
        //         .setFooter('To be replaced', 'https://avatars0.githubusercontent.com/u/40309595?s=200&v=4')

        // embed.build()
    }

    async handleApiError(response, message) {
        if (response.status === 404) {
            return message.util.reply(API_404_ERROR_MSG)
        } else {
            console.log(response)
            return message.util.reply(API_ERROR_MSG)
        }
    }

    async fetchAll(stuffToFetch, args) {
        let query = []

        if (args.term) query.push(`quarter=${args.term}`)
        if (args.year) query.push(`year=${args.year}`)

        query = query.join('&')

        return Promise.all(
            stuffToFetch.map((url) =>
                fetch(`${API_URL}${url}${query ? `?${query}` : ''}`)
            )
        )
    }
}

module.exports = FindCommand
