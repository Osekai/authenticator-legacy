#!/usr/bin/python

import sys
import osu_utils
import json

osuid = str(sys.argv[1])
discordid = str(sys.argv[2])

osu_user_raw = osu_utils.get_user(osuid);
osu_user = osu_user_raw;



import discord
import requests

# include vars.py
import vars

medalcount = 0

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.guilds = True

client = discord.Client(intents=intents)

unneeded_roles = ["Discord Manager", "Server Dev", "Osekai Staff",
"Server Booster", "Osekai Contributor", "osu!team", "news", "Bots", "Retro Colour",
"Current Champion", "Former Champion", "Other Bots", "Retro Achiever",
"Emoji Manager", "Medals Hunter", "Moderation", "Hidden Mod",
"auth", "owo", "Tiny Bot", "Bathbot", "Medalbot", "BathBoi", "Osekai Development",
"no talkie", "nouveau rôle", "Server dev", "Osekai Devs", "Osekai Contributor", "Moderation", "Osekai Development",
"VexAkita", "chromb", "Sowisty", "-Matyr-", "Mamat", "osu!team", "multimode tournament", "TheEggo", "Discord Manager", "Server Booster",
"Former Champion", "Role Manager", "Retro Achiever", "Emoji Manager", "Moderation", "multimode tournament",
"Remyria"]

needed_roles = [
    "95% Club", "90% Club", "80% Club", "60% Club", "40% Club", "Medals Hunter"
]




@client.event
async def on_ready():
    # kill self after 1 minute, just in case something goes wrong and it gets stuck

    print('Logged on as {0}!'.format(client.user))

    print("checking for " + discordid);
    
    guild = client.get_guild(vars.serverid) # find ID by right clicking on server icon and choosing "copy id" at the bottom
    print(guild.name)
    print(guild.get_member(int(discordid)));

    if guild.get_member(int(discordid)) is not None: # find ID by right clicking on a user and choosing "copy id" at the bottom
        user = guild.get_member(int(discordid))
        #await user.send('Your username should be ' + osu_user['username'] + ' and your osu!id is ' + osuid + '.')
        await user.send('Processing your osu! account [{0}]'.format(osu_user['username']))
        role95p =   guild.get_role(vars.new_role_95p)
        role90p =   guild.get_role(vars.new_role_90p)
        role80p =   guild.get_role(vars.new_role_80p)
        role60p =   guild.get_role(vars.new_role_60p)
        role40p =   guild.get_role(vars.new_role_40p)
        userrrole = guild.get_role(vars.genericuserrole)
        print(role95p.name)

        roles = user.roles
        amount = len(roles)
        rolesstr = str(roles)
        
        #removed = []
#
        #for x in roles:
        #    if x in rolesstr:
        #        # if it's already been removed don't again
        #        if x not in removed:
        #            amount -= 1;
        #            removed.append(x)
    # i no longer care about this check
        amount = 1
        if amount == 1:
            medalcount = 0
            # each medal is inside an array inside osu_user
            for medal in osu_user['user_achievements']:
                medalcount += 1
            # the roles are based on percentage
            # role95p is 95% or more
            # role90p is 90% or more
            # role75p is 75% or more
            # role50p is 50% or more
            # so we need to calculate percentages
            percentage = medalcount / vars.total_medals * 100

            await user.remove_roles(role95p)
            await user.remove_roles(role90p)
            await user.remove_roles(role80p)
            await user.remove_roles(role60p)
            await user.remove_roles(role40p)
            
            if percentage >= 95:
                await user.add_roles(role95p)
            elif percentage >= 90:
                await user.add_roles(role90p)
            elif percentage >= 80:
                await user.add_roles(role80p)
            elif percentage >= 60:
                await user.add_roles(role60p)
            elif percentage >= 40:
                await user.add_roles(role40p)

            
            await user.add_roles(userrrole)
            
            # round percentage to XX.XX
            rounded = str(round(percentage, 2))
            # add extra 0 to decimal if needed (e.g. 95.1 -> 95.10)
            if len(str(rounded).split(".")[1]) == 1:
                rounded += "0"

            username = osu_user['username']
            roundpercentageforusername = str(round(percentage, 2))
            username = username + " | " + roundpercentageforusername + "%"



            # rename user to osu_user['username']
            try:
                await user.edit(nick=username)
            except:
                print("failed to rename user")

            await user.send('Authentication Successful! You will receive your roles soon! You have ' + str(medalcount) + ' medals!')
            # send request back to https://osekai.net/authenticator/createUser.php
            # with osuid, discordid, username, and medalcount
            url = 'https://osekai.net/authenticator/api/create_user.php'
            payload = {'osuid': osuid, 'discordid': discordid, 'username': osu_user['username'], 'medalcount': medalcount, 'percentage': percentage, 'key': vars.key}
            r = requests.post(url, data=payload)

            url = 'https://osekai.net/authenticator/api/expire_token.php'
            payload = {'discordid': discordid, 'key': vars.key}
            r = requests.post(url, data=payload)
            
            logs = client.get_channel(vars.logschannel)
            await logs.send('User ' + osu_user['username'] + ' has been authenticated!')

            print(r.text)
        else:
            await user.send('You seemingly already have some roles. Please contact me at <@233170527458426880>. - Error Code ' + str(amount) + ":000A")
            logs = client.get_channel(vars.logschannel)
            await logs.send('User ' + osu_user['username'] + ' has failed to authenticate! - Error Code ' + str(amount) + ":000A")  
    else:
        print("user is not in server. exiting")
        logs = client.get_channel(vars.logschannel)
        await logs.send('Failure: User ' + osu_user['username'] + ' is not in the server!')
    await client.close()

client.run('token')

