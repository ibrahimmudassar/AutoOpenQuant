import json
from datetime import datetime  # For time
from pprint import pprint

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables
# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists


def no_entry_mitigator(x):
    if len(x) == 0:
        return False
    return True


def embed_to_discord(data):

    # create embed object for webhook
    embed = DiscordEmbed(
        title=data["CompanyName"],
        description=data["Position"],
        color="ff00ff",
    )
    embed.add_embed_field(
        name="Link to Application",
        value=data["ApplicationUrl"],
        inline=False,
    )

    embed.add_embed_field(
        name="Location",
        value=data["Location"],
        inline=False,
    )

    # set thumbnail
    embed.set_thumbnail(url=data["CompanyLogo"])

    # set footer
    embed.set_footer(text="By Ibrahim Mudassar")

    # set timestamp
    # embed.set_timestamp(datetime.fromisoformat(data["article:published_time"]))

    # add embed object to webhook(s)
    # Webhooks to send to
    for webhook_url in env.list("WEBHOOKS"):
        webhook = DiscordWebhook(url=webhook_url)
        webhook.add_embed(embed)
        webhook.execute()


re = httpx.get("https://openquant.co/?level=Entry%20Level")
soup = BeautifulSoup(re.content, "html.parser")
re = json.loads(soup.find("script", id="__NEXT_DATA__").get_text())["props"][
    "pageProps"
]['data']
pprint(re)
df = pd.read_csv("data.csv")

unposted = []
for i in re:
    if i["ID"] not in list(df["ID"]):
        unposted.append(i)

for i in unposted:
    embed_to_discord(i)

if len(pd.json_normalize(re)) > 0:
    pd.json_normalize(re).to_csv("data.csv", index=False)
