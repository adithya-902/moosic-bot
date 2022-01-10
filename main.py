import discord
import asyncio
from discord.ext import commands
import sys
from discord import FFmpegPCMAudio 
import youtube_dl
import os
import pafy

client = commands.Bot(command_prefix = '?')

song_queue = {}

@client.event
async def on_ready():
    print("Ready for deployment")
    print("-----------------------")

async def check_queue(ctx):
        if len(song_queue[ctx.guild.id]) > 0:
            await play_song(ctx, song_queue[ctx.guild.id][0])
            song_queue[ctx.guild.id].pop(0)


async def search_song(amount, song, get_url=False):
    info = await client.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({'format' : 'bestaudio/best','quiet' : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key='YoutubeSearch'))
    if len(info['entries']) == 0: return None

    return [entry['webpage_url'] for entry in info['entries']] if get_url else info

async def play_song(ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: client.loop.create_task(check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5


@client.command(pass_context = True)
async def join(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice == None:
        if (ctx.author.voice):
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            source = FFmpegPCMAudio('C:\\Users\\Adithya\\Documents\\Coding\\music bot\\theme\\theme.mp3')
            player = voice.play(source)
        else:
            await ctx.send('You have to be in a voice channel for me to join you kekw')
    else:
        await ctx.send('Already in a vc dummy')

@client.command()
async def queue(ctx): # display the current guilds queue
    if len(song_queue[ctx.guild.id]) == 0:
        return await ctx.send("There are currently no songs in the queue.")

    embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
    i = 1
    for url in song_queue[ctx.guild.id]:
        embed.description += f"{i}) {url}\n"

        i += 1

    embed.set_footer(text="Thanks for using me!")
    await ctx.send(embed=embed)
        
@client.command(pass_context = True)
async def skip(ctx):
    if ctx.voice_client is None:
        return await ctx.send("I am not playing any song.")

    if ctx.author.voice is None:
        return await ctx.send("You are not connected to any voice channel.")

    if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
        return await ctx.send("I am not currently playing any songs for you.")

    else:
        embed = discord.Embed(title="Skip Successful", description="***Skipping now.***", colour=discord.Colour.green())
        await ctx.channel.send(embed=embed)
        ctx.voice_client.stop()


@client.command(pass_context = True)
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("Not in a VC rn")

@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No audio playing rn")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('A song has to be paused for me to resume it lol')

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    voice.stop()

@client.command()
async def howto(ctx):
    embed = discord.Embed(title=f"Commands:-", description="*?play:- Play a song\n?skip:- Skip a song\n?queue\n?search:- Search for the first 5 results from yt\n?pause:- pause the song lol\n?resume:- resume the song \n?skip:- skip song\n?leave:- make the bot leave vc(Do this if you face issues)\n?join:- Make the bot join your vc*\n", colour=discord.Colour.red())
    await ctx.send(embed=embed)

@client.command()
async def search(ctx, *, song=None):
    if song is None: return await ctx.send("You forgot to include a song to search for.")

    await ctx.send("Searching for song, this may take a few seconds.")

    info = await search_song(5, song)

    embed = discord.Embed(title=f"Results for '{song}':", description="*You can use these URL's to play an exact song if the one you want isn't the first result.*\n", colour=discord.Colour.red())
    
    amount = 0
    for entry in info["entries"]:
        embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
        amount += 1

    embed.set_footer(text=f"Displaying the first {amount} results.")
    await ctx.send(embed=embed)



@client.command(pass_context = True)
async def play(ctx, *, song=None ):
    if song is None:
        await ctx.send("You must include a song to play.")
    
    if ctx.voice_client is None:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()

    # handle song where song isn't url
    if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
        await ctx.send("Searching for song, this may take a few seconds.")

        result = await search_song(1, song, get_url=True)

        if result is None:
            return await ctx.send("Sorry, I could not find the given song, try using my search command.")

        song = result[0]

    if ctx.voice_client.source is not None:
        guild_id = ctx.message.guild.id
        if guild_id in song_queue:
            queue_len = len(song_queue[ctx.guild.id])

            if queue_len < 10:
                song_queue[ctx.guild.id].append(song)
                return await ctx.send(f"I am currently playing a song, this song has been added to the queue at position: {queue_len+1}.")

            else:
                return await ctx.send("Sorry, I can only queue up to 10 songs, please wait for the current song to finish.")
        else:
            song_queue[guild_id] = [song]
            return await ctx.send(f"I am currently playing a song, this song has been added to the queue at position: {len(song_queue[ctx.guild.id])}.")

    await play_song(ctx, song)
    await ctx.send(f"Now playing: {song}")


    

     
client.run('OTI5MDEwNjk5OTkxMTU0Njg4.YdhGow.aj_Tt5tdiow6WjC7keZ5NIOYiUc')