'''Make sure to invite your Bot with all perms it needs and application commands'''

# Imports

import discord_webhook                                      # pip install discord-webhook #
from discord_webhook import DiscordWebhook, DiscordEmbed

import nextcord                                             # pip install nextcord #
from nextcord import Intents, Interaction
from nextcord.ext import commands

import json



# Defining "client" #
# Make sure to enable Intents on https://discord.com/developers/applications/APLICATION_ID/bot #

intents = nextcord.Intents.default()
intents.message_content = True
intents.presences = True

client = commands.Bot(
    case_insensitive=True,
    intents=nextcord.Intents.all()
)
client.remove_command("help")


# Get everything from config.json #

question_choices = []                              # Getting the Questions #
with open("questions.json", "r") as f:
    data = json.load(f)
for question in data:
    question_choices.append(question)

with open("config.json", "r") as f:                # Getting everything else needed #
    config = json.load(f)
    bot_token = str(config["bot_token"])
    webhook_url = str(config["webhook_url"])
    feature_request_channel_id = config["feature_request_channel_id"]
    guild_id = config["guild_id"]


# on_ready Event #

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(
        status = nextcord.Status.idle,
        activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="questions")
    )


@client.event
async def on_message(message):
    channel = client.get_channel(feature_request_channel_id)
    if message.channel == channel:
        await message.add_reaction("👍")
        await message.add_reaction("👎")
    else:
        return


@client.slash_command(name = "help", description = "Q&A", guild_ids = [guild_id])
async def _help(interaction : Interaction, question : str = nextcord.SlashOption(choices = question_choices)):
    with open ("questions.json", "r") as f:
        data = json.load(f)
    embed = nextcord.Embed(
        title = str(question),
        color = nextcord.Color.from_rgb(241, 196, 15)
    )
    embed.description = f"{str(data[question])}"
    return await interaction.response.send_message(embed = embed)


# Feature Requests # 

class FeatureRequestModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Feature Request")

        self.description = nextcord.ui.TextInput(
            label="Request",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Tell us about your Feature Request!",
            required=True,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        content = str(self.description.value).replace("@", "(a)")       # Removes "@" from self.description so Users can not ping people with the Webhook"
        try:
            webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True, content = f"**Feature Request: **{content}", username=f"{interaction.user}", avatar_url = interaction.user.avatar.url)
        except:
            webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True, content = f"**Feature Request: **{content}", username=f"{interaction.user}", avatar_url = "https://niclas.wants-to.party/discord-avatar.png")
        response = webhook.execute()

@client.slash_command(name = "request", description = "Feel free to tell us your requests!", guild_ids = [guild_id])
async def featurerequest(interaction : Interaction):
    modal = FeatureRequestModal()
    await interaction.response.send_modal(modal)


# Lets start the Bot ! #

client.run(bot_token)
