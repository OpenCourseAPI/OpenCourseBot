from os import getenv

# import discord
from discord.ext import commands

# TODO: do this in a better way
BOT_OWNERS = [int(x) for x in getenv("BOT_OWNERS", "").split(",")]


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ctx.author.id in BOT_OWNERS

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[bot] We have logged in as {self.bot.user}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        raise error

    @commands.command(aliases=["r"])
    async def reload(self, ctx, ext_name: str = ""):
        if not ext_name:
            await ctx.send("No extension name specified")
            return

        try:
            self.bot.reload_extension(f"commands.{ext_name}")
            await ctx.send("Reloaded!")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send("Extension not loaded")


def setup(bot):
    bot.add_cog(Admin(bot))
