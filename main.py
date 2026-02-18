from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is alive!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


import discord
import asyncio
import os

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

client = discord.Client(intents=intents)

REMINDER_TIME = 240
GRACE_TIME = 120
WARNING_CHANNEL = "accountability"
AFK_CHANNEL_NAME = "AFK"

ALLOWED_CHANNELS = ["Study Room 1", "Study Room 2", "Study Room 3"]

tracked_users = {}


@client.event
async def on_ready():
    print(f"✅ Bot online as {client.user}")


@client.event
async def on_voice_state_update(member, before, after):

    try:
        if after.channel and after.channel.name in ALLOWED_CHANNELS:

            tracked_users[member.id] = False

            async def monitor():
                try:
                    await asyncio.sleep(REMINDER_TIME)

                    if tracked_users.get(member.id) == False:

                        channel = discord.utils.get(member.guild.text_channels,
                                                    name=WARNING_CHANNEL)

                        if channel:
                            await channel.send(
                                f"⏳ {member.mention} turn on **camera OR screenshare** within 2 minutes or you will be moved."
                            )
                        else:
                            print("⚠️ Warning channel not found")

                        await asyncio.sleep(GRACE_TIME)

                        if tracked_users.get(member.id) == False:

                            afk = discord.utils.get(
                                member.guild.voice_channels,
                                name=AFK_CHANNEL_NAME)

                            if afk and member.voice:
                                await member.move_to(afk)
                            else:
                                print("⚠️ AFK channel not found or user left")

                except Exception as e:
                    print("Monitor error:", e)

            asyncio.create_task(monitor())

        if after.self_video or after.self_stream:
            tracked_users[member.id] = True

        if before.channel and not after.channel:
            tracked_users.pop(member.id, None)

    except Exception as e:
        print("Voice event error:", e)


keep_alive()
client.run(os.getenv("TOKEN"))
