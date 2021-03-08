import requests
import asyncio
import discord

from discord.ext import commands

from emojis import emojis, numeric_emojis, num_emojis
from page import Page
from utils import pad_z


async def select(ctx, options, kind):
    """
    The function to show users the possible options and make them select their home colleges,
    target colleges, or intended majors.
    """

    # Check if there is no option.
    if not len(options):

        if kind == "Target College":
            description = (
                f"There is no agreement of your home college and your target college."
            )
        else:
            description = f"{kind} Not Found!"

        return [], description

    # If there is only one option, it is the one we are looking for.
    elif len(options) == 1:

        kind = kind.split()[0]
        kind += " " * (6 - len(kind))

        description = f'{emojis["check"]} `{pad_z(kind)}` {options[0].name}'

        return options[0], description

    else:
        title = f"Choose from these {len(options)} options for your {kind}:"

        # Tell users what options they have.
        pages = generatePages(title, options, kind)

        embed = pages[0].getEmbed()

        msg = await ctx.channel.send(embed=embed)
        await showReactions(msg, pages[0])

        # Check function for the wait_for function later.
        def check(reaction, user):
            emoji = str(reaction.emoji)
            return (
                (emoji in num_emojis or emoji in emojis.values())
                and user == ctx.author
                and reaction.message.id == msg.id
                and user.id != ctx.bot.user.id
            )

        # Get the message from users.
        curr = pages[0]

        try:

            while True:

                reaction, user = await ctx.bot.wait_for(
                    "reaction_add", timeout=20.0, check=check
                )

                if str(reaction.emoji) in num_emojis:
                    break

                if str(reaction.emoji) == emojis["next"]:
                    curr = curr.next

                elif str(reaction.emoji) == emojis["back"]:
                    curr = curr.prev

                elif str(reaction.emoji) == emojis["exit"]:
                    await msg.delete()
                    return

                await msg.edit(embed=curr.getEmbed())
                await showReactions(msg, curr)

        except asyncio.TimeoutError:
            await ctx.channel.send(":no_entry: **Prompt closed due to inactivity.**")
            await msg.delete()
            return

        else:
            kind = kind.split()[0]
            kind += " " * (6 - len(kind))
            description = f'{emojis["check"]} `{pad_z(kind)}` {options[num_emojis[reaction.emoji] + 5 * (curr.page_num - 1) - 1].name}'
            await msg.delete()
            return (
                options[num_emojis[reaction.emoji] + 5 * (curr.page_num - 1) - 1],
                description,
            )


async def showReactions(msg, page):
    await msg.clear_reactions()

    if page.hasPrev():
        await msg.add_reaction(emojis["back"])

    for emoji in list(numeric_emojis.values())[0 : page.count]:
        await msg.add_reaction(emoji)

    if page.hasNext():
        await msg.add_reaction(emojis["next"])

    await msg.add_reaction(emojis["exit"])


def generatePages(title, options, kind):
    pages = []

    # Group options into bunches of 5
    num_per_page = 5
    grouped_options = [
        options[n : n + num_per_page] for n in range(0, len(options), num_per_page)
    ]

    for page_index, items in enumerate(grouped_options):
        msg = ""

        for opt_index, option in enumerate(items):
            msg += f"`{opt_index + 1}` {option.name} "

            if kind == "Home College" or kind == "Target College":
                msg += f"**{option.code}**"

            msg += "\n\n"

        page = Page(
            title,
            msg,
            count=opt_index + 1,
            page_num=page_index + 1,
            total_pages=len(grouped_options),
        )

        if pages:
            page.prev = pages[-1]
            pages[-1].next = page

        pages.append(page)

    return pages
