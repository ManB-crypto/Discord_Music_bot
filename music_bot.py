import discord
from discord.ext import commands, tasks
import youtube_dl

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='!')
queue = []
status = [' ManB bot ']
@client.event
async def on_ready():
    print('bot is good to go')



@client.command(name= 'ping', help = 'Show discord not internet connection')
async def ping(ctx):
    await ctx.send( f'show internet ping : {round(client.latency * 1000)}')

@client.command(name= 'credit', help = 'Show credits')
async def credit(ctx):
    await ctx.send( '**ManB made it!!**')
    await ctx.send( '**Thanks to RKCoding for the tutorial**')


@client.command(name='play', help='This command plays music')
async def play(ctx,url):
    global queue
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        queue[0].pop
    await ctx.send('**Playing:** {}'.format(player.title))

@client.command(name='pause', help='This command pause music')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.pause()


@client.command(name='resume', help='This command pause music')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.resume()
@client.command(name='queue', help='add song to queue')
async def queue_song(ctx, url):
    global queue
    queue.append(url)
    await ctx.send(f'`{url}`added to queqe')

@client.command(name='remove', help='remove song to queue')
async def rm(ctx,number):
    global queue
    queue[int(number)].pop
    await ctx.send('The song is remove')

@client.command(name = 'join',help= 'Display join option')
async  def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("No on is in a voice channel")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@client.command(name='leave', help='diconnect the bot from voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@client.command(name='stop', help='This command stops the music and makes the bot leave the voice channel')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()



client.run('Token')
