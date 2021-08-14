const { Command } = require('discord-akairo')
const Discord = require('discord.js')

const getUsage = require('../utils/getUsage')

const EXTERNAL_COMMANDS = [
    {
        id: 'assist',
        aliases: ['assist'],
        description: {
            text: 'Find an ASSIST transfer report.',
            usage: '"home college" "target college" "target major"',
            examples: [
                { name: '', cmd: 'foothill ucb comp' },
                { name: '', cmd: '"De Anza" ucb "Compter Science"' },
            ],
        },
    },
    {
        id: 'ucstats',
        aliases: ['ucstats'],
        description: {
            text: 'Search UC Transfer Stats',
            usage: 'ucx for target major',
            examples: [
                { name: '', cmd: 'ucb for bio' },
                { name: '', cmd: 'ucla for comp sci' },
            ],
        },
    },
    {
        id: 'grade',
        aliases: ['grade'],
        description: {
            text: 'Search grade distributions at Foothill College.',
            usage: 'professor for subject [course]',
            examples: [
                { name: '', cmd: 'allison herman for everything' },
                { name: '', cmd: 'cascarano for phys 4a' },
            ],
        },
    },
]

class HelpCommand extends Command {
    constructor() {
        super('help', {
            aliases: ['help'],
            description: {
                text: 'Show this help text.',
                usage: '<command>',
            },
            args: [
                {
                    id: 'command',
                },
            ],
        })
    }

    exec(message, args) {
        const embed = new Discord.MessageEmbed()
            .setTitle('OpenCourseBot')
            .setDescription('Available commands:')
            .setFooter('Hope you enjoy!')

        const addCommandToHelp = (command) => {
            if (command.description.hidden) return

            let description = command.description.text || 'No description'

            description +=
                '\n' +
                (command.description.examples || [])
                    .map(
                        (ex) =>
                            `- \`${getUsage(command, ex.cmd)}\`${
                                ex.name ? ': ' + ex.name : ''
                            }`
                    )
                    .join('\n')

            embed.addField(getUsage(command), description)
        }

        for (const [category, commands] of this.handler.categories) {
            for (const [name, command] of commands) {
                addCommandToHelp(command)
            }
        }

        EXTERNAL_COMMANDS.map((command) =>
            addCommandToHelp({
                ...command,
                handler: this.handler,
            })
        )

        message.channel.send(embed)
    }
}

module.exports = HelpCommand
