import requests
import asyncio
import discord

from discord.ext import commands

from college import College
from major import Major
from emojis import emojis, numeric_emojis, num_emojis
from page import Page
from utils import pad_z
from selection import select

url = "https://assist.org/api/institutions"
allInstitutions = requests.get(url).json()


class Assist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def assist(
        self, ctx, home_college: str = "", target_college: str = "", *, major: str = ""
    ):
        """
        First, find the possible options that the user might refer to, and help them choose.
        Second, do the same thing to the possible target colleges and the possible majors.
        And send the agreement they are looking for.
        """

        # Check if arg is empty.
        if not (home_college and target_college and major):
            await ctx.channel.send(
                f'Usage: `{ctx.prefix}assist "Home College" "Target College" "Target Major"`'
            )
            return

        # Generate the home college options.
        home_options = findColleges(home_college)

        # Show them the options and make them choose.
        final_home_college, description = await select(
            ctx, home_options, "Home College"
        )

        if final_home_college:
            sending_id = final_home_college.id

        else:
            description = f'{emojis["ban"]} `Home  ` Not Found!'

        embed = discord.Embed(title="Assist Report", description=description)

        msg = await ctx.channel.send(embed=embed)

        if not final_home_college:
            return

        # Get the sending_id of users' final home college.
        if not sending_id:
            _, sending_id = findColleges(final_home_college.name.split("**")[0][:-1])

        # Generate the target college options and the receiving_id.
        target_options = findColleges(target_college)

        # Show them the options and make them choose.
        try:
            final_target_college, description2 = await select(
                ctx, target_options, "Target College"
            )
        except TypeError:
            await msg.delete()
            return

        if not final_target_college:
            embed.description += "\n" + f'{emojis["ban"]} `Target` Not Found!'
            await msg.edit(embed=embed)
            return
        else:
            print(description2)
            embed.description += "\n" + description2
            await msg.edit(embed=embed)

        receiving_id = final_target_college.id

        # Get the receiving_id of users' final home college.
        if not receiving_id:
            _, receiving_id = findColleges(final_target_college.split("**")[0][:-1])

        #
        agreement = latestAgreement(sending_id, receiving_id)

        #
        if not agreement:
            await ctx.channel.send(
                f"Sorry, there is no agreement between {final_home_college.name} and {final_target_college.name}"
            )
            return

        url = (
            f"https://assist.org/api/agreements?receivingInstitutionId={receiving_id}"
            f"&sendingInstitutionId={sending_id}&academicYearId={agreement}&categoryCode=major"
        )
        reports = requests.get(url).json()["reports"]
        key = 0

        major_options = findMajor(major, reports)

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

        for major in reports:
            if major["label"] == final_major.name:
                key = major["key"]

        if key:
            embed.description += f"\n{emojis['flag']} `Report` **Your report is at**"
            embed.description += f"\n**https://assist.org/transfer/report/{key}**"
        else:
            embed.description += "\nSorry, I didn't find your agreement..."

        await msg.edit(embed=embed)


def findColleges(target, institutions=allInstitutions):
    """
    Find the option that is exactly the same as users' targets or the options that contain users' targets.
    """

    # Check if there is not target.
    if not target:
        return [], 0

    options = []

    # Loop through allInstitution to find potential institution.
    for institution in institutions:

        code = institution["code"].split()[0]
        names = institution["names"]

        # Check if the users enter the code of the school first.
        if target.lower() == code.lower():
            targetCollege = College(institution["id"], names[0]["name"], code)
            return [targetCollege]

        # Loop through the names of the institution.
        for name in names:

            # Found the option that is exactly the same as the target.
            if target.lower() == name["name"].lower():
                targetCollege = College(institution["id"], name["name"], code)
                return [targetCollege]

            # Found the option that contains the target.
            if target.lower() in name["name"].lower() or target.lower() in code.lower():
                options.append(College(institution["id"], name["name"], code))

    return options


def findMajor(target, majors):
    """
    Find the option that is exactly the same as users' targets or the options that contain users' targets.
    """

    # Check if there is no target.
    if not target:
        return []

    options = []
    words = target.lower().split()

    # Loop through allInstitution to find potential institution.
    for major in majors:
        label = major["label"].lower()

        if all([word in label for word in words]):
            options.append(Major(major["label"]))

    return options


def latestAgreement(sending_id, receiving_id):
    """"""

    url = f"https://assist.org/api/institutions/{sending_id}/agreements"

    intuitions = requests.get(url).json()

    for intuition in intuitions:

        if intuition["institutionParentId"] == receiving_id:
            years = intuition["receivingYearIds"][::-1]

            for year in years:

                url = f"https://assist.org/api/agreements/categories?receivingInstitutionId={receiving_id}&sendingInstitutionId={sending_id}&academicYearId={year}"

                category = requests.get(url).json()

                if category[0]["hasReports"]:
                    return year

    return 0


def setup(client):
    client.add_cog(Assist(client))
