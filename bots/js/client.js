const path = require('path')
const {
    AkairoClient,
    CommandHandler,
    ListenerHandler,
} = require('discord-akairo')

class BotClient extends AkairoClient {
    constructor() {
        super(
            {
                ownerID: process.env.BOT_OWNERS.split(','),
            },
            {
                disableMentions: 'everyone',
            }
        )

        this.commandHandler = new CommandHandler(this, {
            directory: path.resolve(__dirname, 'commands'),
            prefix: process.env.BOT_PREFIX || '?',
            handleEdits: true,
            commandUtil: true,
        })

        this.listenerHandler = new ListenerHandler(this, {
            directory: path.resolve(__dirname, 'listeners'),
        })

        this.listenerHandler.setEmitters({
            commandHandler: this.commandHandler,
        })
        this.commandHandler.useListenerHandler(this.listenerHandler)

        this.commandHandler.loadAll()
        this.listenerHandler.loadAll()
    }
}

module.exports = BotClient
