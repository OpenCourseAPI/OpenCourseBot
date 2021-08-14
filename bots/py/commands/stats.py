import discord
import json
from os import getenv

from discord.ext import commands

from college import College
from major import Major
from emojis import emojis
from selection import select

thumbnail = "https://universityofcalifornia.edu/sites/default/files/ucal-fb-image.png"
uc_stats_webpage = "https://www.universityofcalifornia.edu/infocenter/transfers-major"
webpage_url = getenv(
    "WEBPAGE_URL", f"https://{getenv('REPL_SLUG')}.{getenv('REPL_OWNER')}.repl.co"
)


class UCStats(commands.Cog):
    @commands.command()
    async def ucstats(self, ctx, *, msg=""):
        mylist = msg.split(" for ")
        usage_str = f"Usage: `{ctx.prefix}{ctx.invoked_with} <UC> for <major>`\nExample: `{ctx.prefix}{ctx.invoked_with} ucd for bio`"

        if len(mylist) != 2:
            await ctx.channel.send(usage_str)
            return

        college = mylist[0]
        major = mylist[1]

        if not (college and major):
            await ctx.channel.send(usage_str)
            return

        # Generate the home college options.
        college_options = findUC(college)

        final_college, description = await select(ctx, college_options, "Target")

        if not final_college:
            description = f'{emojis["ban"]} `Target` Not Found!'

        embed = discord.Embed(
            title="UC Transfer Stats",
            description=description,
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(url=thumbnail)
        msg = await ctx.channel.send(content=ctx.message.author.mention, embed=embed)

        if not final_college:
            return

        code = getCode(final_college)

        with open("data/allData.json") as f:
            allData = json.load(f)

        majors = allData[code]
        major_options = findMajor(major, majors)
        if not major_options:
            embed.description += "\n" + f'{emojis["ban"]} `Major ` Not Found!'
            await msg.edit(embed=embed)
            return

        try:
            final_major, description3 = await select(ctx, major_options, "Major")
        except TypeError:
            await msg.delete()
            return

        embed.description += "\n" + description3
        await msg.edit(embed=embed)

        for major in majors:
            if majors[major]["Major"].title() == final_major.name.title():
                final_major = majors[major]["Major"].title()
                break

        data = allData[code][final_major.lower()]

        count = 0
        for i in data:
            if i and data[i] and count:
                name = i
                value = data[i].title()
                embed.add_field(name=name, value=value, inline=True)
            else:
                count += 1

        embed.title = f"{final_major} at {final_college.code}: "
        embed.description += (
            f"\n{emojis['flag']} `Links ` **[Go to the official UC Transfer Stats page]({uc_stats_webpage})** or **[our webpage]({webpage_url})**"
        )

        await msg.edit(embed=embed)


def findUC(target):
    if not target:
        return [], 0

    options = []
    with open("data/allUCs.json") as f:
        institutions = json.load(f)

    for institution in institutions:

        code = institution["code"].split()[0]
        name = institution["name"]

        # Check if the users enter the code of the school first.
        if target.lower() == code.lower():
            targetCollege = College(institution["id"], name, code)
            return [targetCollege]

        # Found the option that is exactly the same as the target.
        if target.lower() == name.lower():
            targetCollege = College(institution["id"], name, code)
            return [targetCollege]

        # Found the option that contains the target.
        if target.lower() in name.lower() or target.lower() in code.lower():
            options.append(College(institution["id"], name, code))

    return options


def findMajor(target, majors):
    # Check if there is no target.
    if not target:
        return []

    options = []
    words = target.lower().split()

    # Loop through allInstitution to find potential institution.
    for major in majors:
        label = majors[major]["Major"].lower()

        if all([word in label for word in words]):
            options.append(Major(majors[major]["Major"].title()))

    return options


def getCode(college):
    with open("data/allUCs.json") as f:
        allInstitutions = json.load(f)

    for institution in allInstitutions:
        if institution["name"].lower() == college.name.lower():
            return institution["code"].split()[0]


def setup(client):
    client.add_cog(UCStats(client))
