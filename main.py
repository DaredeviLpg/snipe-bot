#
#
#  DONT TAKE ALL CREDITS OR YOU ARE MONKE SKID
#
#

from flask import Flask, render_template, redirect, request
import threading

app = Flask('app', template_folder="website", static_folder="website")

def keep_alive():
  app.run(host='0.0.0.0', port=8080)

threading.Thread(target=keep_alive).start()

import os, json, datetime
try:
  import discord
except:
  os.system("pip install discord")
  import discord
from discord.ext import commands

conf = json.load(open("config.json", "r"))

try:
  token = conf["token"].replace('{{ environ }}', os.environ['token'])
except:
  token = conf["token"]
prefix = conf["prefix"]
status = conf["status"]
support_server = conf["support_server"]

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all(), help_command=None)

id = 0

@app.route('/')
def wb():
  return render_template("index.html", value=[support_server, f"https://discord.com/oauth2/authorize?client_id={id}&scope=bot&permissions=8"])

@app.route('/review', methods=["POST"])
def review():
  review = request.json["review"]
  with open('website/reviews.txt', 'a') as f:
    f.write(f"[{str(datetime.datetime.utcnow()).split('.')[0].replace('-', '/')} UTC] -- {review}\n\n")
  return '{"ok":"ok"}'

@app.errorhandler(404)
def page_not_found(e):
  return redirect("https://Snipe-bot.smallflopperman.repl.co")

bot.sniped_messages = {}
bot.editsniped_messages = {}

def main():
  try:
    bot.run(token)
  except Exception as e:
    error = str(e)
    if "improper token" in error:
      os.system("clear" if os.name != "nt" else "cls")
      print("invalid bot token.")
    else:
      os.system("clear" if os.name != "nt" else "cls")
      print("Enable all intents.")

@bot.event
async def on_ready():
  os.system("clear" if os.name == "posix" else "cls")
  print(bot.user)
  print(discord.__version__)
  print(f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=8")
  print("--------------")
  await bot.change_presence(activity=discord.Game(name=status.replace("{{ servercount }}", str(len(bot.guilds)))))
  global id
  id = bot.user.id

@bot.event
async def on_message_delete(message):
  if message.author.id == bot.user.id:
    return
  key = str(message.guild.id)
  if len(message.embeds) == 0:
    msg = message.content if message.content != '' else "Empty message"
  else:
    fields = '\n'.join([f"**{x.name}**\n{x.value}" for x in message.embeds[0].fields])
    msg = message.content + '\n' + f"**{message.embeds[0].title}**\n{message.embeds[0].description}\n{fields}"
  deleted_in = '#' + message.channel.name
  if len(message.attachments) != 0:
    if key not in list(bot.sniped_messages.keys()):
      bot.sniped_messages[key] = []
    bot.sniped_messages[key].append(
          {
            "author" : str(message.author), 
            "author_icon" : str(message.author.avatar_url), 
            "attachments" : [f"{message.attachments[x].filename}: [Download]({message.attachments[x].url})" for x in range(len(message.attachments))],
            "content" : msg,
            "footer" : f"Deleted in: {deleted_in}",
            "img" : str(message.attachments[0].url), 
            "timestamp" : message.created_at
          }
        )
    g = True
  else:
    if key not in list(bot.sniped_messages.keys()):
      bot.sniped_messages[key] = []
    bot.sniped_messages[key].append(
          {
            "author" : str(message.author), 
            "author_icon" : str(message.author.avatar_url), 
            "content" : msg,
            "footer" : f"Deleted in: {deleted_in}", 
            "timestamp" : message.created_at
          }
        )
    g=False
  with open("database/logchannels.json", "r") as f:
    channels = json.load(f)
  try:
    channel = bot.get_channel(channels[str(message.guild.id)])
  except:
    return
  try:
    if g is True:
      embed = discord.Embed(color=123456, description='\n'.join([f"{message.attachments[x].filename}: [Download]({message.attachments[x].url})" for x in range(len(message.attachments))])+'\n'+message.content).set_author(name=str(message.author), icon_url=str(message.author.avatar_url)).set_image(url=message.attachments[0].url).set_footer(text=f"Deleted in {deleted_in}")
    else:
      embed = discord.Embed(color=123456, description=message.content).set_author(name=str(message.author), icon_url=str(message.author.avatar_url)).set_footer(text=f"Deleted in {deleted_in}")
    await channel.send(embed=embed)
  except:
    pass

@bot.command()
async def help(ctx):
  fields = [
    {
      "name":f"**{prefix}snipe** `[index]`", 
      "value":"Snipes the latest message deleted, you can snipe earlier messages deleted with the index argument."
    }, 
    {
      "name":f"**{prefix}editsnipe** `[index]`", 
      "value":f"Editsniped the latest message edited, you can editsnipe earlier messages edited with the index argument."
    }, 
    {
    "name":f"**{prefix}logchannel** `<channel>`", 
    "value":"Sets the delete/edit logs channel to the mentioned channel."
    }, 
    {
      "name":"**links**", 
      "value":f'**[Website](https://Snipe-bot.smallflopperman.repl.co)**'
    }
  ]
  embed = discord.Embed(title="Snipe bot commands", color=123456)
  for x in fields:
    embed.add_field(name=x['name'], value=x['value'])
  embed.set_footer(text="© DaredeviL menZ") # dont remove this or monke skid
  await ctx.send(embed=embed)

@bot.command()
async def snipe(ctx, snipe_index='1'):
  if snipe_index.isnumeric() is False:
    snipe_index=1
  else:
    snipe_index=int(snipe_index)
  key = str(ctx.guild.id)
  try:
    sniped = list(reversed(bot.sniped_messages[key]))
  except KeyError:
    await ctx.send('Theres nothing to snipe!')
    return
  index = snipe_index - 1
  try:
    embed_data = sniped[index]
  except IndexError:
    if index != 0:
      await ctx.send('No message to snipe that far back.')
    return
  if "img" in list(embed_data.keys()):
    embed = discord.Embed(description='\n'.join(embed_data["attachments"])+"\n"+embed_data["content"], color=123456, timestamp=embed_data['timestamp']).set_author(name=embed_data["author"], icon_url=embed_data["author_icon"]).set_footer(text=embed_data["footer"]+f" | Index {snipe_index}/{len(sniped)}").set_image(url=embed_data["img"])
  else:
    embed = discord.Embed(description=embed_data["content"], color=123456, timestamp=embed_data['timestamp']).set_author(name=embed_data["author"], icon_url=embed_data["author_icon"]).set_footer(text=embed_data["footer"]+f" | Index {snipe_index}/{len(sniped)}")
  await ctx.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
  if before.content == after.content:
    return
  if before.author.id == bot.user.id:
    return
  key = str(before.guild.id)
  bfr = before.content if before.content != '' else "Empty message"
  aftr = after.content if after.content != '' else "Empty message"
  edited_in = '#' + after.channel.name
  if key not in list(bot.editsniped_messages.keys()):
    bot.editsniped_messages[key] = []
  bot.editsniped_messages[key].append(
    {
      "before": {
        "author" : str(before.author), 
        "author_icon" : str(before.author.avatar_url), 
        "content" : bfr,
        "footer" : f"edited in: {edited_in}", 
        "timestamp" : before.created_at
      },
      "after": {
        "author" : str(after.author), 
        "author_icon" : str(after.author.avatar_url), 
        "content" : aftr,
        "footer" : f"edited in: {edited_in}", 
        "timestamp" : after.created_at
      }
    }
  )
  with open("database/logchannels.json", "r") as f:
    channels = json.load(f)
  try:
    channel = bot.get_channel(channels[str(before.guild.id)])
  except:
    return
  try:
    embed = discord.Embed(color=123456)
    fields = [
      {
        "name": "**Before**",
        "value": bfr
      }, 
      {
        "name": "**after**", 
        "value": aftr
      }
    ]
    for x in fields:
      embed.add_field(name=x["name"], value=x["value"])
    embed.set_footer(text=f"Edited in: {edited_in}")
    embed.set_author(name=str(after.author), icon_url=str(after.author.avatar_url))
    await channel.send(embed=embed)
  except:
    pass

@bot.command()
async def editsnipe(ctx, snipe_index='1'):
  if snipe_index.isnumeric() is False:
    snipe_index=1
  else:
    snipe_index=int(snipe_index)
  key = str(ctx.guild.id)
  try:
    sniped = list(reversed(bot.editsniped_messages[key]))
  except KeyError:
    await ctx.send('Theres nothing to editsnipe!')
    return
  index = snipe_index - 1
  try:
    embed_data = sniped[index]
  except IndexError:
    if index != 0:
      await ctx.send('No message to editsnipe that far back.')
    return
  fields = [
    {
      "name": "**Before**",
      "value": embed_data["before"]["content"][:1024]
    }, 
    {
      "name": "**after**", 
      "value": embed_data["after"]["content"][:1024]
    }
  ]
  embed = discord.Embed(color=123456, timestamp=embed_data["after"]["timestamp"])
  embed.set_footer(text=embed_data["after"]["footer"]+f" | Index {snipe_index}/{len(sniped)}"
  )
  for x in fields:
    embed.add_field(name=x['name'], value=x['value'])
  await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def logchannel(ctx, channel:discord.channel.TextChannel=None):
  if channel is None:
    channel=ctx.channel
  with open("database/logchannels.json", "r") as f:
    channels = json.load(f)
  try:
    ls = channels[str(ctx.guils.id)]
    if ls == channel.id:
      await ctx.send(f"the log channel has been set to <#{channel.id}>")
      return
  except:
    pass
  channels[str(ctx.guild.id)] = channel.id
  with open("database/logchannels.json", "w") as f:
    json.dump(channels, f, indent=2)
  await ctx.send(f"the delete logs channel has been set to <#{channel.id}>!")

@logchannel.error
async def logchannel_error(ctx, error):
  print(error)
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("You are missing permissions to use this command(manage server).")
  if isinstance(error, commands.ChannelNotFound):
    await ctx.send("channel not found.")

if __name__ == '__main__':
  main()
