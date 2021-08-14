from os import getenv
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv()

bot = Bot(command_prefix=getenv("BOT_PREFIX", "?"))
extensions = [
    "commands.admin",
    "commands.assist",
    "commands.server",
    "commands.scrape",
    "commands.stats",
    "commands.gradescrape",
    "commands.grade",
]

@bot.before_invoke
async def before_invoke(ctx):
    print(
        f'[cmd] {ctx.author} invoked "{ctx.command.name}" with "{ctx.message.content}"'
    )

if __name__ == "__main__":
    bot.remove_command("help")
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(getenv("BOT_TOKEN"))
