function getUsage(command, trailing) {
    const prefix = command.handler.prefix
    const name = command.id
    const usage = trailing || command.description.usage

    return `${prefix}${name} ${usage}`
}

module.exports = getUsage
