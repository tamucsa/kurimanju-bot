import os
import discord
from discord.ext import commands
from discord.utils import find
import re

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.typing = False
intents.presences = False
intents.reactions = True

client = commands.Bot(command_prefix='&',
    help_command=commands.MinimalHelpCommand(),
    activity=discord.Game(name="&help"),
    intents=intents)

class MyNewHelp(commands.MinimalHelpCommand):
  async def send_pages(self):
    destination = self.get_destination()
    for page in self.paginator.pages:
      emby = discord.Embed(description=page)
      await destination.send(embed=emby)

client.help_command = MyNewHelp()

#overall help command
async def send_bot_help(self, mapping):
    embed = discord.Embed(title="Help", color=discord.Color.blurple())
    for cog, commands in mapping.items():
      filtered = await self.filter_commands(commands, sort=True)
      command_signatures = [self.get_command_signature(c) for c in filtered]
      if command_signatures:
        cog_name = getattr(cog, "qualified_name", "No Category")
        embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
    channel = self.get_destination()
    await channel.send(embed=embed)
    
#help for a certain command
async def send_command_help(self, command):
    embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.random())
    if command.help:
      embed.description = command.help
    if alias := command.aliases:
      embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

    channel = self.get_destination()
    await channel.send(embed=embed)
    
#helper function to add commands to embed
async def send_help_embed(self, title, description, commands):
    embed = discord.Embed(title=title, description=description or "No help found...")
    if filtered_commands := await self.filter_commands(commands):
      for command in filtered_commands:
        embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...")
    await self.get_destination().send(embed=embed)
    
async def send_group_help(self, group):
    title = self.get_command_signature(group)
    await self.send_help_embed(title, group.help, group.commands)

async def send_cog_help(self, cog):
    title = cog.qualified_name or "No"
    await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())
    
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.tree.sync()
  
#member joins server
@client.event
async def on_member_join(member):
    welcome_channel = client.get_channel(1051917990096019478)
    print(f"{member} has joined!")
    await welcome_channel.send(
        f"Hello {member.mention}, welcome to the server! Thank you for joining!")
  
#member leaves server
@client.event
async def on_member_remove(member):
    welcome_channel = client.get_channel(1051917990096019478)
    print(f"{member} has left!")
    await welcome_channel.send(
        f" We will miss you {member.mention}... :broken_heart:")
  
@client.event
async def on_message(message):
    #message contains alcohol -> well well well...
    if re.search(r"(?i)( |^)alcohol( |$)", message.content):
        await message.channel.send('well well well...')
        
@client.hybrid_command()
async def profile(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    userAvatar = member.avatar
    embed = discord.Embed()
    embed.set_image(url=userAvatar)
    await ctx.send(embed=embed)
    
client.run(TOKEN)