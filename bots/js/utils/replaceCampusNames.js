const replacements = {
    foothill: 'fh',
    'de-anza': 'da',
    'de anza': 'da',
    deanza: 'da',
}

const replaceCampusNames = (name) => replacements[name] || name

module.exports = replaceCampusNames
