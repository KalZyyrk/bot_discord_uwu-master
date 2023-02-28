import json
import re
import discord
import asyncio
import openai
import wow_api
from discord.ext import commands
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv
import os
import requests
load_dotenv()


openai.api_key = os.environ['OPENAI_TOKEN']
question = [
    "Est-ce qu'il y a des mots vulgaires ou un manque de respect dans cet extrait? Le moindre mot provocant doit être "
    "considéré comme une insulte meme si ce mais pas forcément méchant! Voici la reponse préformaté a me donner. "
    "Je ne veux rien d'autres que cela. GrosMots:oui ou GrosMots:non . Voici le text a analyser: \n",
    "Est-ce qu'il y a des passages raciste dans cet extrait? Voici la reponse préformaté a me donner. "
    "Je ne veux rien d'autres que cela. racisme:oui ou racisme:non . Voici le text a analyser: "]
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), description="mon giga bot")
api_key = os.environ['RIOT_TOKEN']
watcher = LolWatcher(api_key)




@bot.command()
async def avatar(ctx, region, server, username):
    filename = await wow_api.imageToUrl(region,server,username)
    with open(filename, "rb") as f:
        file = discord.File(f, filename)
        await ctx.send(file=file)
@bot.command()
async def cote(ctx):
    await ctx.send("Souhaitez avoir votre cote en pvp ou en pve ?")
    try:
        type = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=60)
        if type.content.lower() == "pve":
            await ctx.send("Merci de me donnez vos information de personnage")
            message = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=60)
            argument = message.content.split(" ")
            region = argument[0]
            server = argument[1]
            username = argument[2]
            cotepve = await wow_api.ratingPVE(ctx, region=region, server=server,username=username)
            await ctx.send(cotepve)
        if type.content.lower() == "pvp":
            await ctx.send("Merci de me donnez vos information de personnage")
            message = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=60)
            argument = message.content.split(" ")
            region = argument[0]
            server = argument[1]
            bracket = argument[2]
            username = argument[3]
            cotepvp = await wow_api.ratingPVP(ctx, region=region,server=server, bracket=bracket, username=username)
            await ctx.send(cotepvp)


    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé, merci de recommencer.")



'''
@bot.command()
async def cote(ctx, region, server, bracket, username):
    test = await wow_api.ratingPVP(ctx, region, server, bracket, username)
'''

@bot.command()
async def server_list(ctx):
        server_list = []
        for guild in bot.guilds:
            server_list.append(guild.name)
        with open('list_server.json', 'w') as f:
            json.dump(server_list, f, indent=4)

@bot.command()
async def lol(ctx, region, username: str):
    if region.lower() == 'na1' or region.lower() == 'euw1':
        if len(username) <= 16 and re.match("^[a-zA-Z0-9_]*$", username):
            compte = username.strip()
            me = watcher.summoner.by_name(region, compte)
            my_ranked_stats = watcher.league.by_summoner(region, me['id'])
            if len(my_ranked_stats) > 0:
                rank = my_ranked_stats[0]['tier']
                rank_T = my_ranked_stats[0]['rank']
                rank_LP = my_ranked_stats[0]['leaguePoints']
                await ctx.send(f"Le rang de ce joueur est {rank} {rank_T} {rank_LP} LP")
            else:
                await ctx.send("aucunne stat pour ce joueur")

        else:
            await ctx.send("Le pseudo est trop long")
            return
    else:
        await ctx.send("Region incorrecte")


@bot.event
async def on_ready():
    print("ready")


@bot.command()
async def up(ctx):
    await ctx.send("Le bot est prêt")
    return

@bot.command()
async def ia(ctx, message):
    if re.match("^[a-zA-Z0-9_]*$", message):
        message_text = ctx.message.content
        response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{message_text}",
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=1,
    )
    Reponse_Lower2 = response["choices"][0]["text"].lower()
    await ctx.send(f"{Reponse_Lower2}")



@bot.command()
async def give_guest_role(ctx):
    guest_role = discord.utils.get(ctx.guild.roles, name="AoE")
    await ctx.author.add_roles(guest_role)


'''
@bot.event
async def on_message(message):
    Message_De_Detection = ["Pk tu insute", "Pk tes raciste"]
    await bot.process_commands(message)
    if message.author.guild_permissions.administrator:
        return
    prompt = question[0] + message.content
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=1,
    )
    Reponse_Lower = response["choices"][0]["text"].lower()
    if "grosmots" in Reponse_Lower:
        if "oui" in Reponse_Lower:
            await message.channel.send(Message_De_Detection[0])
            await message.delete()
        if "non" in Reponse_Lower:
            prompt = question[1] + message.content
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=2048,
                n=1,
                stop=None,
                temperature=1,
            )
            Reponse_Lower2 = response["choices"][0]["text"].lower()
            if "racisme" in Reponse_Lower2:
                if "oui" in Reponse_Lower2:
                    await message.channel.send(Message_De_Detection[1])
                    await message.delete()
'''
@bot.command()
async def cuisiner(ctx):
    await ctx.send("envoyer le plat que vous voulez cuisiner")

    try:
        async with ctx.typing():
            recette = await bot.wait_for("message", timeout=30, check=lambda m: m.channel == ctx.channel)
    except asyncio.TimeoutError:
        await ctx.send("Temps écoulé, merci de recommencer.")

    recette = recette.content
    message = await ctx.send(f"La preparation de {recette} va commencer. veilleur valider en reagissant avec :white_check_mark:")
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def checkEmoji(reaction, user):
        return ctx.message.author == user and message.id == reaction.message.id and (str(reaction.emoji) == "✅") or (str(reaction.emoji) == "❌")

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout = 10, check = checkEmoji)
        if reaction.emoji == "✅":

            response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Donne moi une recette pour : {recette}",
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=1,
        )
            Reponse_Lower2 = response["choices"][0]["text"].lower()
            await ctx.send(f"{Reponse_Lower2}")
        elif reaction.emoji == "❌":
            await ctx.send("bah nik")
    except:
        await ctx.send("Temps écoulé, merci de recommencer.")
        return
''' 
@bot.event
async def on_message_edit(before, messagee):
    Message_De_Detection = ["Pk tu insute ", "Pk tes raciste "]
    # if message.author.guild_permissions.administrator:
    # return
    prompt = question[0] + messagee.content
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=1,
    )
    Reponse_Lower = response["choices"][0]["text"].lower()
    if "grosmots" in Reponse_Lower:
        if "oui" in Reponse_Lower:
            await messagee.channel.send(Message_De_Detection[0])
            await messagee.delete()
        if "non" in Reponse_Lower:
            prompt = question[1] + messagee.content
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=2048,
                n=1,
                stop=None,
                temperature=1,
            )
            Reponse_Lower2 = response["choices"][0]["text"].lower()
            if "racisme" in Reponse_Lower2:
                if "oui" in Reponse_Lower2:
                    await messagee.channel.send(Message_De_Detection[1])
                    await messagee.delete()
'''
@bot.command()
async def unban(ctx, username: str):
    banned_users = ctx.guild.bans()
    member_name, member_discriminator = username.split('#')

    async for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.name}#{user.discriminator} a été débanni avec succès')
            return
    await ctx.send(f"{username}, na pas ete trouver")
    return

@bot.command()
@commands.has_role("Admin")
async def ban(ctx, user: discord.Member, *reason):
        reason = " ".join(reason)
        await ctx.guild.ban(user, reason = reason)
        await ctx.send(f"{user} a ete ban.")



@bot.command()
async def coucou(ctx):
    print("coucou")
    await ctx.send("Coucou !")



@bot.command()
async def serveurInfo(ctx):
    server = ctx.guild
    numberOfTextChannels = len(server.text_channels)
    numberOfVoiceChannels = len(server.voice_channels)
    serveurDescription = server.description
    numberOfPerson = server.member_count
    server = server.name
    message = f"**le serveur {server} contient {numberOfPerson} personne ainsi que {numberOfVoiceChannels} channel vocale**"
    await ctx.send(message)


@bot.command()
async def say(ctx, repeat: int, message: str):
    for i in range(repeat):
        await ctx.send(message)



@bot.command()
async def chinese(ctx, *, message: str):
    chineseChar = "丹书ㄈ力已下呂廾工丿片乚爪ㄇ口尸厶尺ㄎ丁凵人山父了乙"
    chineseText = []
    for word in message:
        for char in word:
            if char.isalpha():
                index = ord(char) - ord("a")
                transformed = chineseChar[index]
                chineseText.append(transformed)
            else:
                chineseText.append(char)
    await   ctx.send("".join(chineseText))


@bot.command()
async def clear(ctx, *, number: int):
    messages = [message async for message in ctx.channel.history(limit=number + 1)]
    for message in messages:
        await message.delete()


@bot.command()
@commands.has_role("Admin")
async def kick(ctx, user: discord.Member, *reason):
    reason = " ".join(reason)


@bot.event
async def on_disconnect():
    print("Le bot s'est déconnecté.")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur est survenue lors de l'événement {event} : {args[0]}")


@bot.command()
async def deconnection(ctx):
    await ctx.send("Le bot a ete correctement deconnecter")
    await bot.close()

discordToken = os.environ['DISCORD_TOKEN']
bot.run(discordToken)
