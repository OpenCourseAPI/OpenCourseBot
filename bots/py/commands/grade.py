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
    usage_str = f'**Usage:** \n`1. {ctx.prefix}grade professor for subject [course]`\n`2. {ctx.prefix}grade professor for everything`'

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
        await ctx.message.reply("No results!")
        return

    pages = generatePages(data)

    embed = pages[0].getEmbed()

    try:
        msg = await ctx.channel.send(content=ctx.message.author.mention, embed=embed)
    except discord.errors.HTTPException:
        await ctx.message.reply("Too many results! Please search for a more specific term.")
        return

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
    should_show_all = subject == 'everything'

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
                and (should_show_all or subject.upper() == instructor_data["subject"])
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
            msg += f'**For Professor {getProfessorString(instructor)}\n**'

            for classData in classList:
                msg += f"`{getTermString(classData['quarter'])}` "

                msg += f"`{getSubjectString(classData['subject'])}` "

                msg += f"`{getClassNumberString(classData['number'])}` "

                for letter in letters:
                    msg += f"`{getGradeString(classData[letter], letter)}` "

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



def getProfessorString(instructor):
    return " ".join(instructor.split(",")[::-1])


def getGradeString(num, letter):
    """
    Get the formatted string with the distribution and the letter.
    """

    # detect if num is empty string
    try:
        num = int(num)
    except ValueError:
        num = 0

    return f" {num} {letter}" if num < 10 else f"{num} {letter}"


def getTermString(term):
    """
    Get the formatted string with a certain number of blanks at the end.
    >>> getTermString('Spring')
    'Spring'
    >>> getTermString('Fall')
    'Fall  '
    """
    return term + (6 - len(term)) * " "


def getSubjectString(subject):
    """
    Get the formatted string with a certain number of blanks.
    >>> getSubjectString("CS")
    '  CS'
    >>> getSubjectString("CHEM")
    'CHEM'
    """
    return (4 - len(subject)) * " " + subject


def getClassNumberString(classNumber):
    """
    Get the formatted string filtered out 'F00..' in class code.
    >>> getClassCodeString("F001AH")
    ' 1AH'
    >>> getClassCodeString("F0010")
    '  10'
    >>> getClassCodeString("F248A")
    '248A'
    """

    # first generate the list of number 1 to 9 for later use.
    one_to_nine = [str(i) for i in range(1, 10)]
    num = 0

    # loop through classCode to find the first number in it
    for i in range(len(classNumber)):
        if classNumber[i] in one_to_nine:
            num = i
            break

    # get the target substring based on the num that we just got
    target = classNumber[num:]
    return (4 - len(target)) * " " + target


def setup(client):
    client.add_command(grade)
