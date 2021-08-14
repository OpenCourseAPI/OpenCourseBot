import json
import requests
from discord.ext import commands
from bs4 import BeautifulSoup

years = ["2015-2016", "2016-2017", "2017-2018", "2018-2019", "2019-2020"]


@commands.command()
async def gradescrape(ctx):
    await ctx.send("Scraping grade distributions...")

    all_data = {}

    for year in years:
        url = "https://transfercamp.com/foothill-college-grade-distribution-" + year

        # Let's GET the HTML page
        res = requests.get(url)
        # Throw an error and stop the script if the status code is not 200 OK
        res.raise_for_status()

        # Make a soup from our HTML string
        soup = BeautifulSoup(res.text, "html.parser")

        # Find all the 'tr' tags that contain instructor data
        rows = soup.select("tbody tr")

        # Table headers, used for convenience
        table_headers = [
            "year",
            "quarter",
            "professor",
            "subject",
            "number",
            "course ID",
            "A",
            "B",
            "C",
            "D",
            "F",
            "W",
        ]

        data_of_a_year = []

        for row in rows:

            column = row.find_all("td")

            text_data = [td.get_text().strip() for td in column]

            instructor_data = dict(zip(table_headers, text_data))

            instructor_data["subject"] = instructor_data["subject"].replace(" ", "")

            data_of_a_year.append(instructor_data)

        all_data[year] = data_of_a_year
        print(year)

    with open("data/grades.json", "w") as outfile:
        json.dump(all_data, outfile)

    await ctx.send("Finished scraping grade distributions!")


def setup(client):
    client.add_command(gradescrape)
