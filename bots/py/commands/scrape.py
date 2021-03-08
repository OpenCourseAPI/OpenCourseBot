import re
import csv
import json
import asyncio
import aiohttp

from discord.ext import commands

from bs4 import BeautifulSoup

ROOT_URL = "https://visualizedata.ucop.edu/t/Public/views/TransferbyCCM/Bymajorname?:embed=y&:showVizHome=no&:host_url=https%3A%2F%2Fvisualizedata.ucop.edu%2F&:embed_code_version=3&:tabs=yes&:toolbar=yes&:showAppBanner=false&:display_spinner=no&:loadOrderID=0"


async def create_session(session):
    async with session.get(ROOT_URL) as response:
        if response.status != 200:
            raise RuntimeError

        html = await response.text()

    soup = BeautifulSoup(html, "html5lib")
    tsConfigContainer = soup.find("textarea", {"id": "tsConfigContainer"})
    tsConfigData = json.loads(tsConfigContainer.get_text())
    sessionId = tsConfigData["sessionid"]

    return sessionId


async def bootstrap_session(session, sessionId):
    form_data = aiohttp.FormData(
        {
            "worksheetPortSize": '{"w":1000,"h":800}',
            "dashboardPortSize": '{"w":1000,"h":800}',
            "clientDimension": '{"w":690,"h":789}',
            "renderMapsClientSide": "true",
            "isBrowserRendering": "true",
            "browserRenderingThreshold": "100",
            "formatDataValueLocally": "false",
            "clientNum": "",
            "navType": "Reload",
            "navSrc": "Top",
            "devicePixelRatio": "2",
            "clientRenderPixelLimit": "25000000",
            "allowAutogenWorksheetPhoneLayouts": "true",
            "sheet_id": "By%20Major%20Name",
            "showParams": '{"checkpoint":false,"refresh":false,"refreshUnmodified":false}',
            "stickySessionKey": '{"featureFlags":"{}","isAuthoring":false,"isOfflineMode":false,"lastUpdatedAt":1600530856409,"workbookId":123}',
            "filterTileSize": "200",
            "locale": "en_US",
            "language": "en",
            "verboseMode": "false",
            ":session_feature_flags": "{}",
            "keychain_version": "1",
        }
    )

    async with session.post(
        f"https://visualizedata.ucop.edu/vizql/t/Public/w/TransferbyCCM/v/ByMajorName/bootstrapSession/sessions/{sessionId}",
        data=form_data,
    ) as response:
        if response.status != 200:
            raise RuntimeError

        data = await response.text()
        chunks = re.split(r"[0-9]+;\{", data)
        first_data = json.loads("{" + chunks[1])

        optionsStr = first_data["worldUpdate"]["applicationPresModel"][
            "workbookPresModel"
        ]["dashboardPresModel"]["zones"]["20"]["presModelHolder"]["visual"][
            "filtersJson"
        ]
        options = json.loads(optionsStr)[0]["table"]["tuples"]

        return options


async def generate_tempfile(session, sessionId, sheetdocId):
    with aiohttp.MultipartWriter("form-data") as mp:
        data = {
            "sheetdocId": sheetdocId,
            "useTabs": "true",
            "sendNotifications": "true",
        }

        for key, value in data.items():
            part = mp.append(value)
            part.set_content_disposition("form-data", name=key)

        async with session.post(
            f"https://visualizedata.ucop.edu/vizql/t/Public/w/TransferbyCCM/v/ByMajorName/sessions/{sessionId}/commands/tabsrv/export-crosstab-to-csvserver",
            data=mp,
        ) as response:
            if response.status != 200:
                print(response)
                print(await response.text())
                raise RuntimeError

            data = await response.json(content_type=None)
            tempfileKey = data["vqlCmdResponse"]["layoutStatus"][
                "applicationPresModel"
            ]["presentationLayerNotification"][0]["presModelHolder"][
                "genFileDownloadPresModel"
            ][
                "tempfileKey"
            ]

            return tempfileKey


async def switch_campus(session, sessionId, idx):
    with aiohttp.MultipartWriter("form-data") as mp:
        data = {
            "visualIdPresModel": '{"worksheet":"Major Table","dashboard":"By Major Name"}',
            "globalFieldName": "[federated.1xtee380yrajk410jnsfd1fsy47h].[none:CMP_LOC_LOC1_SHRT_DESC:nk]",
            "membershipTarget": "filter",
            "filterIndices": f"[{idx}]",
            "filterUpdateType": "filter-replace",
        }

        for key, value in data.items():
            part = mp.append(value)
            part.set_content_disposition("form-data", name=key)

            async with session.post(
                f"https://visualizedata.ucop.edu/vizql/t/Public/w/TransferbyCCM/v/ByMajorName/sessions/{sessionId}/commands/tabdoc/categorical-filter-by-index",
                data=mp,
            ) as response:
                if response.status != 200:
                    raise RuntimeError


async def do_scrape():

    allData = {}

    async with aiohttp.ClientSession() as session:
        sessionId = await create_session(session)

        options = await bootstrap_session(session, sessionId)

        for i, cmp_data in enumerate(options):
            name = cmp_data["t"][0]["v"]
            print(f"Scraping {name}")

            await switch_campus(session, sessionId, i)

            print("switched campus")

            tempfileKey = await generate_tempfile(
                session, sessionId, "{2193A602-EAF6-4CF7-B7CF-B9BB4F163F60}"
            )

            print("generated temporary download link")

            async with session.get(
                f"https://visualizedata.ucop.edu/vizql/t/Public/w/TransferbyCCM/v/ByMajorName/tempfile/sessions/{sessionId}/?key={tempfileKey}&keepfile=yes&attachment=yes"
            ) as response:
                if response.status != 200:
                    raise RuntimeError

                print("downloaded csv file")

                data = await response.text()
                with open(f"data/{name}-data.csv", "w") as file:
                    file.write(data)

            allData[name] = getData(find_file_path(name))

            await asyncio.sleep(2)

    with open("data/allData.json", "w") as file:
        json.dump(allData, file)


async def do_scrape_ucs():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://assist.org/api/institutions") as response:
            if response.status != 200:
                raise RuntimeError

            data = await response.json()
            filtered_ucs = [
                {
                    "id": campus["id"],
                    "code": campus["code"].strip(),
                    "name": campus["names"][0]["name"].strip(),
                }
                for campus in data
                if campus["code"].startswith("UC")
            ]

            print(filtered_ucs)

            with open("data/allUCs.json", "w") as file:
                json.dump(filtered_ucs, file)


@commands.command()
async def scrape(ctx):
    await ctx.channel.send("Scraping started")
    await do_scrape()
    await ctx.channel.send("Scraping finished")


@commands.command()
async def scrape_ucs(ctx):
    await do_scrape_ucs()
    await ctx.channel.send("Scraped UCs")


def setup(bot):
    bot.add_command(scrape)
    bot.add_command(scrape_ucs)


find_file_path = lambda name: f"data/{name}-data.csv"


def getData(file_path):
    data = {}

    with open(file_path) as file:
        reader = csv.reader(file, delimiter="\t")
        count = 0

        for row in reader:
            if not count:
                count += 1
                header = [col.replace("Major name", "Major") for col in row]

            else:
                major = {}
                for i in range(len(header)):
                    major[header[i]] = row[i]

                data[row[2].lower()] = major

    return data
