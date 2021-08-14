# OpenCourseBot

This is a handy discord bot for college-related functionality such as information about classes, professors, and general statistics.

## Features

-   Search **college class data** such as subjects, courses, classes, and seats (powered by [OpenCourseAPI](https://github.com/OpenCourseAPI/OpenCourseAPI))
-   Search **professors**, including ratings
-   Search **class grade distributions**
-   Search **[ASSIST](https://assist.org) transfer reports**
-   Search **[UC Transfer Statistics](https://www.universityofcalifornia.edu/infocenter/transfers-major)**

## Development

The commands and features of the bot are split accross two separate bots, which run on Python 3+ and Node.js respectively.

### Setup

#### Node.js

Install [`Node.js v12+`](https://nodejs.org/) and [`npm`](https://www.npmjs.com/get-npm), and then install packages with:

```sh
npm install
```

#### Python

Install [`Python 3.7+`](https://www.python.org/) and [`poetry`](https://python-poetry.org/docs/#installation), and then install packages with:

```sh
poetry install
```

### Configuration

Create a file called `.env` with the following content:

```env
BOT_TOKEN=<discord bot token>
BOT_OWNERS=<comma separated Discord user IDs>
BOT_PREFIX=<command prefix>
```

### Start

Run the following command to start both bots:

```sh
poetry shell
npm start
```

### Lint

Use the following commands to lint the code:

#### Node.js

```sh
npm run lint # only check
npm run lint:fix # check and fix
```

#### Python

```sh
poetry shell
black ./bots/py # check and fix errors
```

## Contribute

All contributions are welcome! Feel free to get started by opening an issue or pull request.

### Core Team

-   [**Madhav Varshney**](https://github.com/madhavarshney)
-   [**David Tso**](https://github.com/davidtso1219)

## License

[MIT License](LICENSE)
