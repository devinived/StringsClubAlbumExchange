import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import typing
import asyncio
from datetime import datetime
import dbManager as db
import openorclosed as OOC
load_dotenv()
TOKEN = os.getenv("TOKEN")

EXCHANGE_INFO = 1235343710753914880
bot = commands.Bot(intents = discord.Intents.default(), command_prefix="ae!")

def hasperms(userid):
    users = [273219749926666244, 98610465042595840, 286246724270555136] #devin, jared, ulti
    if userid in users:
        return True
    else:
        return False

def validExchangeDate(date):
    exchanges = db.getExchanges()

    flag = 0
    for ex in exchanges:
        if date.lower() == ex.lower():
            flag += 1

    if flag > 0:
        return True
    else:
        return False

@bot.event
async def on_ready():
    print(f"Synced {len(await bot.tree.sync())} commands globally")

    await bot.change_presence(status = discord.Status.do_not_disturb, activity=discord.CustomActivity(name="Join the next album exchange!"))

@bot.tree.command(description="View my commands")
async def help(interaction:discord.Interaction):
    helpEmbed:discord.Embed = discord.Embed(title="Album Exchange Commands", color=discord.Color.from_str("#b03f33"))
    helpEmbed.add_field(name="/setup_exchange [timeframe]", value = "Exchange Admin Use Only: Creates a new Album Exchange with the specified time frame")
    helpEmbed.add_field(name="/join_exchange [which_exchange]", value = "Enters you into the selected album exchange. Get your ears ready to discover some new music and review it!")
    helpEmbed.add_field(name="/end_exchange [which_exchange]", value = "Exchange Admin Use Only: Ends a specified Album Exchange")
    helpEmbed.add_field(name="/create_assignments [which_exchange]", value = "Randomly selects an album for everyone who is participating in the exchange.")
    helpEmbed.add_field(name="/user_joined_exchange [which_exchange] (user)", value = "Check if a user is entered into the Album Exchange")
    helpEmbed.add_field(name="/set_submission_window [status]", value="Toggles whether submissions are being taken")
    await interaction.response.send_message(embed=helpEmbed)

@bot.tree.command(description = "Sets up an Album Exchange")
@app_commands.describe(timeframe = "The dates that the exchange occurs (ex: May 1 - May 8)", announce="Send the setup message? (set to false for testing)")
async def setup_exchange(interaction:discord.Interaction, timeframe:str, announce:bool=True):
    if not hasperms(interaction.user.id):
        interaction.response.send_message("You can't do that.")
        return
    #ensures the time frame gets entered into the database as lowercase.
    timeframe = timeframe.lower()
    confirmation:discord.Embed = discord.Embed(title="Exchange Started!", color=discord.Color.green())
    confirmation.add_field(name="Started by", value = f"{interaction.user.mention}")
    confirmation.add_field(name="Time Frame", value = f"{timeframe}")
    await interaction.response.send_message(embed=confirmation)
    db.make_table(date=timeframe)
    if announce:

        channel=bot.get_channel(EXCHANGE_INFO)
        await channel.send(f"# A New Album Exchange Has Started!\n<@&1239388427280056320>\nTime Frame: `{timeframe}`",allowed_mentions=discord.AllowedMentions(roles=True, everyone=False))
    OOC.add_one(timeframe,status=True)

@bot.tree.command(description = "Join the album exchange! listed is the end date of the current exchange. Join that one!")
@app_commands.describe(which_exchange = "The Album Exchange to take part in.", album_url = "The spotify link to your album of choice.", album_name="format: Album Name - Artist")
async def join_exchange(interaction:discord.Interaction, which_exchange:str, album_url:str,album_name:str):
    if OOC.getStatus(which_exchange) == False:
        await interaction.response.send_message("The submission window is now closed. Please try to enter the next exchange.", ephemeral = True)
        return
    if not "https://open.spotify.com/album" in album_url:
        await interaction.response.send_message("That doesn't seem to be a valid Spotify Album URL. Double-check please.",ephemeral=True)
        return 
    if not validExchangeDate(which_exchange):
        await interaction.response.send_message("That's not a valid album exchange, please choose from the list", ephemeral = True)
        return
    if db.userJoined(which_exchange, interaction.user.id):
        await interaction.response.send_message("You've already joined the Album Exchange!")
        return
    channel=bot.get_channel(EXCHANGE_INFO)
    await channel.send(f"{interaction.user.mention} has entered the `{which_exchange}` album exchange!")
    await interaction.response.send_message(f"You've joined this exchange: remember, it's more fun if your entry is secret, that's why only you can see this message!\nJust as a reminder, you've entered ||{album_name}|| into the exchange.", ephemeral=True)
    db.joinExchange(date=which_exchange,user_id=interaction.user.id, entry_url=album_url, entry_name=album_name)


@bot.tree.command(description="This will end the specified exchange, and archive it.")
@app_commands.describe(which_exchange = "Which exchange to end?", announce="Send the setup message? (set to false for testing)")
async def end_exchange(interaction:discord.Interaction,which_exchange:str, announce:bool=True):
    if not hasperms(interaction.user.id):
        interaction.response.send_message("You can't do that.")
        return
    
    if not validExchangeDate(which_exchange):
        await interaction.response.send_message("That's not a valid album exchange, please choose from the list")
        return
    try:
        db.archive(which_exchange)
        if announce:
            await interaction.response.send_message("Album Exchange Ended.")
            channel=bot.get_channel(EXCHANGE_INFO)
            await channel.send(f"# Exchange Ended!\nThe `{which_exchange}` Album Exchange has concluded. Thanks for participating!",allowed_mentions=None)
        else:
            await interaction.response.send_message("Album Exchange Ended.")

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

@bot.tree.command(description="Get a list of all albums + their names")
async def all_albums(interaction:discord.Interaction, which_exchange:str, embed:bool=None):
    if not hasperms(interaction.user.id):
        interaction.response.send_message("You can't do that.")
        return
    
    if not validExchangeDate(which_exchange):
        await interaction.response.send_message("That's not a valid album exchange, please choose from the list")
        return
    
    message = ""
    for album in db.show_all(which_exchange):
        if not embed:
            message += f"{album[2]} | <{album[1]}>\n"
        else:
            message += f"{album[2]} | {album[1]}"

    await interaction.response.send_message(message)


@bot.tree.command(description="Check if a given user has entered this week's Album Exchange")
async def user_joined_exchange(interaction:discord.Interaction, which_exchange:str,user:discord.User=None):
    if not validExchangeDate(which_exchange):
        await interaction.response.send_message("That's not a valid album exchange, please choose from the list")
        return
    
    if user==None:
        user=interaction.user
    joined = db.userJoined(which_exchange,user.id)

    if joined:
        await interaction.response.send_message(f"{user.mention} has joined the exchange!", allowed_mentions=None)
    else:
        if user == interaction.user:
            await interaction.response.send_message(f"{user.mention} has **not** joined the exchange. You should try it out! Use </join_exchange:1235053603534803057> to join!", allowed_mentions=None)

        else:
            await interaction.response.send_message(f"{user.mention} has **not** joined the exchange. Encourage them to join with the </join_exchange:1235053603534803057> command!", allowed_mentions=None)

@bot.tree.command(description = "Creates the random assignments for the Album Exchange")
@app_commands.describe(which_exchange="The Album Exchange to make assignments for", which_channel = "The channel to send the assignments. If none specified, defaults to current channel.", forum_url ="The URL for the forum post where this exchange is happening.")
async def create_assignments(interaction:discord.Interaction, which_exchange:str, forum_url:str, which_channel:discord.TextChannel = None):
    if not hasperms(interaction.user.id):
        await interaction.response.send_message("You can't do that.")
        return
    if not forum_url.startswith("https://discord.com/channels/"):
        await interaction.response.send_message("That's not a valid forum URL", ephemeral = True)
        return
    await interaction.response.defer(thinking=True)
    if which_channel:
        channel = which_channel.id
    else:
        channel = interaction.channel.id
    message = f"# __Album Exchange Assignments:__\nBelow are the assignments for the `{which_exchange}` album exchange.\n"

    shuffled = db.shuffle(which_exchange)
    if shuffled == None:
        await interaction.followup.send(content = "Needs more entries before we can create assignments.")
        return
    for user in shuffled:
        #adds the user mention, the album name, and then the link
        message += f"<@{user[0]}>\n**{user[2]}**\n<{user[1]}>\n\n"
    message += f"Don't forget: this exchange is scheduled for `{which_exchange}`:bangbang: Please try to have your review submitted by the deadline in {forum_url}"
    channel = bot.get_channel(channel)
    message = await channel.send(content=message,allowed_mentions=None)
    await interaction.followup.send(content = f"Assignments created: {message.jump_url}")

@bot.tree.command()
@app_commands.choices(status=[app_commands.Choice(name="Open", value=1),app_commands.Choice(name="Closed", value=0)])
async def set_submission_window(interaction:discord.Interaction, which_exchange:str, status:app_commands.Choice[int]):
    if not hasperms(interaction.user.id):
        interaction.response.send_message("You can't do that.")
        return

    OOC.setStatus(date=which_exchange, status = status.value)
    if status.value:
        status = "Open"
    else:
        status = "Closed"
    await interaction.response.send_message(f"Submission Window: {status}")
"""The following are the autocompletes for their respective commands, which just fill in the active exchanges"""
@join_exchange.autocomplete("which_exchange")
async def join_autocomplete(
        interaction:discord.Interaction,
        current: str)->typing.List[app_commands.Choice[str]]:
    
    data = []
    if len(db.getExchanges()) == 0:
        data.append(app_commands.Choice(name="No active exchanges :(", value = "No active"))
    else:
        for ex in db.getExchanges():
            data.append(app_commands.Choice(name=ex, value=ex))
    return data

@create_assignments.autocomplete("which_exchange")
async def create_autocomplete(
        interaction:discord.Interaction,
        current: str)->typing.List[app_commands.Choice[str]]:
    
    data = []
    if len(db.getExchanges()) == 0:
        data.append(app_commands.Choice(name="No exchange to create assignments for.", value = "No active"))
    else:
        for ex in db.getExchanges():
            data.append(app_commands.Choice(name=ex, value=ex))
    return data
@user_joined_exchange.autocomplete("which_exchange")
async def user_joined_autocomplete(
        interaction:discord.Interaction,
        current: str)->typing.List[app_commands.Choice[str]]:
    
    data = []
    if len(db.getExchanges()) == 0:
        data.append(app_commands.Choice(name="No exchange to create assignments for.", value = "No active"))
    else:
        for ex in db.getExchanges():
            data.append(app_commands.Choice(name=ex, value=ex))
    return data

@end_exchange.autocomplete("which_exchange")
async def end_autocomplete(
        interaction:discord.Interaction,
        current: str)->typing.List[app_commands.Choice[str]]:
    
    data = []
    if len(db.getExchanges()) == 0:
        data.append(app_commands.Choice(name="No exchanges to end", value = "No active"))
    else:
        for ex in db.getExchanges():
            data.append(app_commands.Choice(name=ex, value=ex))
    return data
@all_albums.autocomplete("which_exchange")
async def allAlbums_autocomplete(
        interaction:discord.Interaction,
        current: str)->typing.List[app_commands.Choice[str]]:
    
    data = []
    if len(db.getExchanges()) == 0:
        data.append(app_commands.Choice(name="No active exchanges :(", value = "No active"))
    else:
        for ex in db.getExchanges():
            data.append(app_commands.Choice(name=ex, value=ex))
    return data

@set_submission_window.autocomplete("which_exchange")
async def submission_autocomplete(
        interaction:discord.Interaction,
        current: str)->typing.List[app_commands.Choice[str]]:
    
    data = []
    if len(db.getExchanges()) == 0:
        data.append(app_commands.Choice(name="No active exchanges :(", value = "No active"))
    else:
        for ex in db.getExchanges():
            data.append(app_commands.Choice(name=ex, value=ex))
    return data

bot.run(TOKEN)

