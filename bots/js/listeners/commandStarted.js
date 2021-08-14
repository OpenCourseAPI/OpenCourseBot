const { Listener } = require('discord-akairo')

class CommandStartedListener extends Listener {
    constructor() {
        super('commandStarted', {
            emitter: 'commandHandler',
            event: 'commandStarted',
        })
    }

    exec(message, command) {
        console.log(
            `[cmd] ${message.author.tag} invoked "${command.id}" with "${message.content}"`
        )
    }
}

module.exports = CommandStartedListener
