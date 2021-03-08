from os import getenv
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Bot(commands.Bot):
    def before_invoke(self, ctx):
        print(
            f'[command] "{ctx.author}" invoked "{ctx.command.name}" with "{ctx.message.content}"'
        )


client = Bot(command_prefix=getenv("BOT_PREFIX", "?"))

extensions = [
    "commands.admin",
    "commands.assist",
    "commands.server",
    "commands.scrape",
    "commands.stats",
    "commands.gradescrape",
    "commands.grade",
]

if __name__ == "__main__":
    client.remove_command("help")
    for extension in extensions:
        client.load_extension(extension)
    client.run(getenv("BOT_TOKEN"))
