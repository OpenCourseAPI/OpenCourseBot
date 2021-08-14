const { Command } = require('discord-akairo')

class ReloadCommand extends Command {
    constructor() {
        super('reload-js', {
            aliases: ['reload-js', 'rjs'],
            description: {
                hidden: true,
                text: 'Reload a command handler',
                usage: '<command>',
            },
            args: [
                {
                    id: 'command',
                    type: 'string',
                    default: 'all',
                },
            ],
            ownerOnly: true,
            category: 'owner',
        })
    }

    exec(message, args) {
        if (args.command == 'all') {
            this.handler.reloadAll()
            return message.channel.send(
                `Reloaded ${
                    Array.from(this.handler.modules).length
                } command(s)!`
            )
        }

        try {
            this.handler.reload(args.command)
            return message.util.send(`Reloaded command ${args.command}!`)
        } catch {
            try {
                const category = this.handler.categories
                    .map((c) => c)
                    .filter((c) => c == args.command)[0]
                category.reloadAll()

                return message.util.send(
                    `Reloaded category ${args.command}!\nReloaded ${
                        Array.from(category).length
                    } command(s)!`
                )
            } catch (e) {
                return message.util.send(
                    `"${args.command}" is not a valid category/command ID!`
                )
            }
        }
    }
}

module.exports = ReloadCommand
