import json
import discord
import asyncio
from discord.ext import commands
from emojis import emojis, numeric_emojis, num_emojis
from page import Page

years = ["2015-2016", "2016-2017", "2017-2018", "2018-2019", "2019-2020"]


@commands.command()
async def grade(ctx, *, msg: str = " "):

    prof_and_class = msg.split(" for ")
    usage_str = '**Usage:** \n`1. ?grade "Professor" for "Subject" "(Class Code)"`\n`2. ?grade "Professor" for everything`'

    if len(prof_and_class) != 2:
        await ctx.channel.send(usage_str)
        return

    target_prof = prof_and_class[0].split()
    the_class = prof_and_class[1].split()
    depart = the_class[0]

    if len(the_class) > 2:
        await ctx.channel.send(usage_str)
        return

    elif len(the_class) == 2:
        classCode = the_class[1]

    else:
        classCode = ""

    data = getProfessorData(target_prof, depart, classCode)

    if ifEmpty(data):
        await ctx.channel.send(content=ctx.message.author.mention + " No Result!")
        return

    pages = generatePages(data)

    embed = pages[0].getEmbed()
    msg = await ctx.channel.send(content=ctx.message.author.mention, embed=embed)
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
        await msg.clear_reactions()
        return


def getProfessorData(target_prof, subject, classCode):

    with open("data/grades.json") as f:
        jsonData = json.load(f)

    interested = ["quarter", "subject", "number", "A", "B", "C", "D", "F", "W"]
    allData = {}

    for year, instructors in jsonData.items():

        found = []
        data_of_this_year = {}

        for instructor_data in instructors:

            instructor_name = instructor_data["professor"]
            flag = True

            for target_prof_name in target_prof:

                if target_prof_name.lower() not in instructor_name.lower():
                    flag = False
                    break

            if (
                flag
                and subject.upper() == instructor_data["subject"]
                and (classCode.upper() in instructor_data["number"] or not classCode)
            ):

                if instructor_name not in found:
                    found.append(instructor_name)
                    data_of_this_year[instructor_name] = []

                new_data = {}
                for i in interested:
                    new_data[i] = instructor_data[i]

                data_of_this_year[instructor_name].append(new_data)

        allData[year] = data_of_this_year

    return allData


def generatePages(data):
    pages = []
    letters = ["A", "B", "C", "D", "F", "W"]

    for year in years[::-1]:

        instructors = data[year]

        title = f"In {year}"
        msg = ""

        for instructor in instructors.keys():

            classList = instructors[instructor]
            msg += f'**For Professor {" ".join(instructor.split(",")[::-1])}\n**'

            for classData in classList:
                msg += f"`{classData['quarter']}" + " " * (
                    len("spring") - len(classData["quarter"])
                )

                classNumber = classData["number"][-4:].replace("0", " ")
                classNumber = classNumber.replace("F", " ")

                if len(classNumber) < 4:
                    classNumber = " " * (4 - len(classNumber)) + classNumber

                msg += f"` `{classNumber}` "

                for letter in letters:
                    try:
                        num = int(classData[letter])
                    except ValueError:
                        num = 0

                    if num < 10:
                        msg += f"`  {num} {letter}` "
                    else:
                        msg += f"` {num} {letter}` "

                msg += "\n"

            msg += "\n\n"

        msg += f"Check this: https://transfercamp.com/foothill-college-grade-distribution-{year}"
        page = Page(title, msg, 0, len(pages) + 1)

        if pages:
            page.prev = pages[-1]
            pages[-1].next = page

        pages.append(page)

    return pages


def ifEmpty(data):
    empty = True

    for year in data:
        if data[year]:
            empty = False

    return empty


async def showReactions(msg, page):
    await msg.clear_reactions()

    if page.hasPrev():
        await msg.add_reaction(emojis["back"])

    for emoji in list(numeric_emojis.values())[0 : page.count]:
        await msg.add_reaction(emoji)

    if page.hasNext():
        await msg.add_reaction(emojis["next"])

    await msg.add_reaction(emojis["exit"])


def setup(client):
    client.add_command(grade)
