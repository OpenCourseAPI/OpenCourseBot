require('dotenv').config()

const BotClient = require('./client')

function startBot() {
    const { IGNORE_SSL } = require('./config')

    if (IGNORE_SSL) {
        process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0
    }

    process.on('unhandledRejection', (reason, promise) => {
        console.log('Unhandled Promise Rejection!')
        console.error(reason)
    })

    const client = new BotClient()

    client.login(process.env.BOT_TOKEN)
}

if (require.main === module) {
    startBot()
}

module.exports = startBot
