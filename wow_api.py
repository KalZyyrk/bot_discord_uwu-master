import re
import discord
import asyncio
from discord.ext import commands
import json
import shutil
import requests
import os
from dotenv import load_dotenv
load_dotenv()




def getAccessToken():
    res = requests.post('https://oauth.battle.net/token', data={'grant_type': 'client_credentials', }, auth=(
    os.environ['CLIENT_ID'],os.environ['CLIENT_SECRET']))
    return res.json()['access_token']


def listServer():
    res = requests.get("https://us.api.blizzard.com/data/wow/connected-realm/index?namespace=dynamic-us&locale=en_US&access_token=EUmkntchsBDAeHSvioQC9s6L318wjq4Z3H")
    return res.json()



async def PVPBracketStatistic(ctx, region, server, bracket, username):
    token = getAccessToken()
    res = requests.get(f"https://{region}.api.blizzard.com/profile/wow/character/{server}/{username}/pvp-bracket/{bracket}?namespace=profile-{region}&locale=en_US&access_token={token}")
    return res.json()


async def PVEBracketStatistic(ctx, region, server, username):
    token = getAccessToken()
    res = requests.get(f"https://{region}.api.blizzard.com/profile/wow/character/{server}/{username}/mythic-keystone-profile?namespace=profile-{region}&locale=en_US&access_token={token}")
    return res.json()


async def ratingPVE(ctx, region, server,username):
    data = await PVEBracketStatistic(ctx, region, server, username)
    sentence = f"Le cote du joueur {data['character']['name']} est {int(data['current_mythic_rating']['rating'])}"
    return sentence


async def ratingPVP(ctx, region, server, bracket, username):
    data = await PVPBracketStatistic(ctx, region, server, bracket, username)
    sentence = f"Le cote du joueur {data['character']['name']} est {data['rating']}"
    return sentence



async def mediaUrl(region, server,username):
    token = getAccessToken()
    res = requests.get(f"https://{region}.api.blizzard.com/profile/wow/character/{server}/{username}/character-media?namespace=profile-{region}&locale=en_US&access_token={token}")
    return res.json()

async def findImgUrl(region,server,username):
    data = await mediaUrl(region,server,username)
    avatar_url = ""
    for asset in data["assets"]:
        if asset["key"] == "avatar":
            avatar_url = asset["value"]
    return avatar_url
async def imageToUrl(region,server,username):
    url = await (findImgUrl(region,server,username)) #prompt user for img url
    file_name = (f'avatar{username}.jpg') #prompt user for file_name
    res = requests.get(url, stream = True)
    if res.status_code == 200:
        with open(file_name,'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully Downloaded: ',file_name)
        file = file_name
        return file
    else:
        print('Image Couldn\'t be retrieved')

