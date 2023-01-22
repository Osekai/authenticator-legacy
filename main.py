import asyncio
import datetime
import discord
import requests
import sys
import base64
import subprocess
import magic

import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg

import cairo
import traceback
import os
url = "https://osekai.net/authenticator/";

role_95p = 880874323160748102
role_90p = 880874345101148181
role_75p = 880874366206885909

role_50p = 880874379695783967
genericuserrole = 880874306756808706


intents = discord.Intents.default()
intents.members = True

import vars
import osu_utils

client = discord.Client(intents=intents)

processing = False;

@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))
    processing = False
    # set custom status
    await client.change_presence(activity=discord.Game(name="run oa!reprocessme to update your roles!"))
    # channelId = 639515567233171478
    # channel = client.get_channel(channelId)
    # await channel.send("hi")

admins = [233170527458426880, 338688617033498624, 100295345086402560, 276087082554884096, 876577395040190464, 494883957117288448]

texts = {
    "reauth1":"Hey there! Your user was already authenticated, so we removed the old entry. You can re-authenticate using this link! : ",
}

def isAdmin(user):
    return user.id in admins;

async def reportError(content, channel):
    # use nice embed
    embed = discord.Embed(title="Error", description=content, color=0xFF0000)
    embed.set_footer(text="osekai.net")
    await channel.send(embed=embed)


@client.event
async def on_message(message):
    if message.author.bot == False:
        try:
            items = message.content.split(" ")
            #await message.channel.send("uwu")
            if items[0] == "oa!resend":
                if(len(items) > 1):
                    if(items[1] == "to"):
                        if isAdmin(message.author):
                            user = client.get_user(int(items[2]))
                            if(len(items) > 3 and items[3] == "with"):
                                await user.send(texts[items[4]] + str(await requestAuthenticationToken(user)))
                            else:
                                await user.send("You should be able to simply click this link and authenticate your osu! account: " + str(await requestAuthenticationToken(user)))
                else:
                    url = "https://osekai.net/authenticator/api/users.php?key=" + vars.key
                    x = requests.get(url)
                    users = x.json()
                    id = message.author.id
                    alreadySent = False
                    for user in users:
                        if int(user["DiscordID"]) == id:
                            alreadySent = True
                            print("User already sent link!")
                            await reportError("You are already authenticated. If this seems incorrect, please ping a moderator.", message.channel)
                            break
                    if alreadySent == False:
                        await message.author.send("Here's your auth link! - " + str(await requestAuthenticationToken(message.author)))

            if items[0] == "oa!reprocess":
                if isAdmin(message.author):
                    if items[1] == "specific":
                        await reprocessRoles("specific", int(items[2]), message.channel, 0);
                    elif items[1] == "all":
                        await reprocessRoles("all");
            if items[0] == "oa!wipe":
                if isAdmin(message.author):
                    if(items[1] == "osu"):
                        await wipeUserOsu(int(items[2]));
                    else:
                        await wipeUser(int(items[2]));
            if items[0] == "oa!wipeAndResend":
                if isAdmin(message.author):
                    if(items[1] == "osu"):
                        await wipeUserOsu(int(items[2]));
                    else:
                        await wipeUser(int(items[2]));
                    if(items[3] == "to" and items[4] == "discord"):
                        user = client.get_user(int(items[5]))
                        await user.send(texts["reauth1"] + str(await requestAuthenticationToken(user)))
            if items[0] == "oa!help":
                await message.channel.send("Hey there! This bot is super simple, and only has two commands:\n"+
                "- `oa!reprocessme` - Reprocesses your current medal count and percentage\n"+
                "- `oa!resend` - Resends an authentication link in the case you have not received one!");
            if items[0] == "oa!status":
                if isAdmin(message.author):
                    user = message.content.split(" ")[1]
                    await getStatus(user, message.channel)
            if items[0] == "oa!reprocessme" or items[0] == "owoa!repowocessme":
                if message.channel.id == 716706864888283174:
                    userid = message.author.id
                    await reprocessRoles("specific", userid, message.channel, message.author)
                else:
                    await message.channel.send("This command is only available in <#716706864888283174>.")
            if items[0] == "oa!render":
                if isAdmin(message.author):
                    announcementsChannel = client.get_channel(vars.announcements)
                    await sendPercentageUpdate("Tanza3D", 40, "https://a.ppy.sh/10379965", announcementsChannel, "<@876577395040190464> is testing the rendering system of Osekai Authenticator! Please, ignore this.", 0, "12.34");
            if items[0] == "oa!runloop":
                if isAdmin(message.author):
                    if len(items) > 1:
                        loopType = items[1]
                        await message.channel.send("Running loop with type " + loopType)
                        proc = subprocess.Popen(["python3", "/root/scripts/loop.py", loopType], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        await message.channel.send("Done!");
                    else:
                        await message.channel.send("Error: no loop type specified!")
        except Exception as e:
            # just shove the error in whatever channel we're in
            channel = client.get_channel(message.channel.id)
            await channel.send("uh oh! - Error: " + str(e) + ":\n" + traceback.format_exc())

async def wipeUser(id):
    print("wiping " + str(id));

    guild = client.get_guild(639515567233171476)
    member = guild.get_member(int(id));
    print(member);
    await removeRoles(member)
    requests.get(url + "api/destroy_entry.php?discordId=" + str(member.id) + "&key=" + vars.key)

async def wipeUserOsu(id):
    await wipeUser(requests.get(url + "api/get_discord_id_from_osu_id.php?osu=" + str(id)).text + "&key=" + vars.key)

async def sendPercentageUpdate(name, percentage, avatar, channel, message, medalcount, rawpercentage):
    print("Sending percentage update with name" + name + ", percentage " + str(percentage) + ", avatar " + str(avatar))

    svg = "";

    path = "95club.svg"
    if percentage == 95:
        path = "new_95club.svg"
    if percentage == 90:
        path = "new_90club.svg"
    if percentage == 80:
        path = "new_80club.svg"
    if percentage == 60:
        path = "new_60club.svg"
    if percentage == 40:
        path = "new_40club.svg"

    with open(path, "r") as f:
        svg = f.read()
    svg = svg.replace("&#60;USER&#62;" , name)

    userpfp = "data:image/"

    
    r = requests.get(avatar)
    
    mime = magic.Magic(mime=True)
    mime = magic.from_buffer(r.content, mime=True);
    #await channel.send("type is " + mime);

    if(mime == "image/gif"):
        userpfp += "gif;base64,"
    elif(mime == "image/jpeg"):
        userpfp += "jpeg;base64,"
    elif(mime == "image/png"):
        userpfp += "png;base64,"
    else:
        userpfp += "png;base64,"

    userpfp += base64.b64encode(r.content).decode("utf-8")
    
    svg = svg.replace("USERPFP" , userpfp)
    svg = svg.replace("&#60;MEDALS&#62;" , str(medalcount))
    output = "output_" + str(datetime.datetime.now().timestamp()) + ".png"

    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1366,768)
    ctx = cairo.Context(img)
    svg = Rsvg.Handle.new_from_data(svg.encode("utf-8"))
    svg.render_cairo(ctx)
    img.write_to_png(output)

    await channel.send(file=discord.File(output), content=message)
    os.remove(output)

@client.event
async def on_member_join(user):
    await memberJoined(user)
    

async def requestAuthenticationToken(user):
    print(url + "api/create_token.php?discordId=" + str(user.id));
    x = requests.get(url + "api/create_token.php?discordId=" + str(user.id) + "&key=" + vars.key)
    return "https://osekai.net/authenticator/auth?token=" + str(x.text);

async def memberJoined(user):
    token = await requestAuthenticationToken(user);
    print("Please authenticate your osu! account at " + str(url) + "auth?token=" + str(token) + " !");
    try:
        await user.send("Hey there! Please authenticate your osu! account at " + str(token) + " !\n\n" +
        "By authenticating with this link, you will gain access to uploading images and attachments, and be auto-roled with your medal percentage in the osu! Medal Hunters server!\n\n"
        + "Please make sure to read our server rules at <#667136725478408203> before you start joining in on conversations.")
        logs = client.get_channel(vars.logschannel)
        await logs.send("User " + str(user.name) + " has joined the server! Sent authentication link with token: " + str(token))
    except:
        print("Error sending message to user. Most likely they have DM's disabled.")
        # send error to 639515567233171478
        general = client.get_channel(639515567233171478)
        await general.send("Hey <@" + str(user.id) + ">! We couldn't send you a link to authenticate your osu! account.\nPlease enable Direct Messages for this server `Right Click > Privacy Settings > Direct Messages [On]`, and then run `oa!resend` in <#716706864888283174> to get a new link.")

async def removeRoles(member):
    guild = client.get_guild(vars.serverid)
    role95p =   guild.get_role(vars.new_role_95p)
    role90p =   guild.get_role(vars.new_role_90p)
    role80p =   guild.get_role(vars.new_role_80p)
    role60p =   guild.get_role(vars.new_role_60p)
    role40p =   guild.get_role(vars.new_role_40p)
    userrrole = guild.get_role(vars.genericuserrole)
    print("the user " + str(member.name) + " has the roles:")
    print(str(member.roles));
    try:
        await member.remove_roles(role95p, role90p, role80p, role60p, role40p, userrrole)
    except ValueError:
        print("we do not have permission to remove roles from " + str(member))

async def removeAllRoles():
    members = client.get_guild(vars.serverid).members
    for member in members:
        removeRoles(member);
        # wait 0.5 seconds
        # await asyncio.sleep(0.1)

async def reprocessRoles(amount, xuser = 0, channel = 0, author = 0):
    global processing
    if amount == "all" or amount == "specific":
        if amount == "all":
            await client.change_presence(status=discord.Status.idle,activity=discord.Game(name="we're reprocessing all our roles! you cannot reprocess right now."))
            processing = True
        else:
            if processing == True:
                # you cannot reprocess specific users while processing all users
                await channel.send("We are currently reprocessing all the users. During this process, you cannot reprocess yourself manually. Please try again later!")
                return;
            elif vars.total_medals >= vars.old_total_medals and vars.newMedals is True:
                # the medal count hasnt been updated yet
                await channel.send("This command is temporarily disabled. This is not a bug. See <#926427871596134420> for more information.")
                #await channel.send("no")
                return;
            else:
                await channel.send("Processing your medal count...")
        # we can get all the users which need to be reprocessed from https://osekai.net/authenticator/api/users.php
        print("fetching users");
        url = "https://osekai.net/authenticator/api/users.php?key=" + vars.key
        x = requests.get(url)
        users = x.json()
        print("found " + str(len(users)) + " users");

        guild =     client.get_guild(vars.serverid)
        role95p =   guild.get_role(vars.new_role_95p)
        role90p =   guild.get_role(vars.new_role_90p)
        role80p =   guild.get_role(vars.new_role_80p)
        role60p =   guild.get_role(vars.new_role_60p)
        role40p =   guild.get_role(vars.new_role_40p)
        userrrole = guild.get_role(vars.genericuserrole)
        logchannel = client.get_channel(vars.logs)

        doneprocess = False
        for user in users:
            try:
                if amount == "specific" and str(user['DiscordID']) != str(xuser):
                    #print("skipping " + str(user['DiscordID'] + " because it is not " + str(xuser)))
                    continue
                
                doneprocess = True

                print("processing " + str(user['DiscordID']))
                
                print("processing user " + str(user["osuID"]))
                osu_user = osu_utils.get_user(user["osuID"]);

                #print("finding user " + str(user["DiscordID"]))
                duser = guild.get_member(int(user["DiscordID"]))
                # if user does not exist, continue
                if duser == None:
                    print("user " + str(user["DiscordID"]) + " does not exist")
                    logmsg = "user " + str(user["DiscordID"]) + " does not exist"
                    await logchannel.send(logmsg)
                    continue
                #print("found user " + duser.name)

                medalcount = 0
                # each medal is inside an array inside osu_user
                for medal in osu_user['user_achievements']:
                    medalcount += 1

                percentage = medalcount / vars.total_medals * 100
                await duser.remove_roles(role95p)
                await duser.remove_roles(role90p)
                await duser.remove_roles(role80p)
                await duser.remove_roles(role60p)
                await duser.remove_roles(role40p)

                # round percentage to XX.XX
                rounded = str(round(percentage, 2))
                # add extra 0 to decimal if needed (e.g. 95.1 -> 95.10)
                if len(str(rounded).split(".")[1]) == 1:
                    rounded += "0"

                if(channel != 0):
                    title = "Done!"
                    content_start = "You have been processed! You now have {0} medals! ({1}%)"
                    if(osu_user['username'] == "chromb"):
                        title = "chromb!";
                        content_start = "chromb chromb chromb chromb! chromb chromb chromb {0} chromb! ({1}chromb)"
                    content_start = content_start.format(str(medalcount), str(rounded))
                    if(osu_user['username'] == "chromb"):
                        # chromb easter egg
                        embed=discord.Embed(title=title, description= content_start, color=0x00ff00)
                        embed.set_image(url="https://chromb.uk/chromb.png")
                        embed.set_thumbnail(url="https://chromb.uk/chromb.png")
                        embed.set_author(name="chromb", icon_url="https://chromb.uk/chromb.png")
                        await channel.send(embed=embed)
                    else:
                        await channel.send(embed=discord.Embed(title=title, description= content_start, color=0x00ff00))

                oldPercentage = float(user["Percentage"])

                if percentage >= 95:
                    await duser.add_roles(role95p)
                elif percentage >= 90:
                    await duser.add_roles(role90p)
                elif percentage >= 80:
                    await duser.add_roles(role80p)
                elif percentage >= 60:
                    await duser.add_roles(role60p)
                elif percentage >= 40:
                    await duser.add_roles(role40p)

                announcementsChannel = client.get_channel(vars.announcements)

                if percentage >= 95 and oldPercentage < 95:
                    await duser.send("You have received the **95%** role! That's an insane achievement, welcome to the club! :tada:")
                    await sendPercentageUpdate(osu_user['username'], 95, "https://a.ppy.sh/" + str(user['osuID']), announcementsChannel, "<@" + str(duser.id) + "> has received the **95%** role! That's an insane achievement, welcome to the club! :tada:", medalcount, str(rounded))
                elif percentage >= 90 and oldPercentage < 90:
                    await duser.send("You have received the **90%** role! Great job! :tada:")
                    await sendPercentageUpdate(osu_user['username'], 90, "https://a.ppy.sh/" + str(user['osuID']), announcementsChannel, "<@" + str(duser.id) + "> has received the **90%** role! Great job! :tada:", medalcount, str(rounded))
                elif percentage >= 80 and oldPercentage < 80:
                    await duser.send("You have received the **80%** role! Nice stuff! :tada:")
                    await sendPercentageUpdate(osu_user['username'], 80, "https://a.ppy.sh/" + str(user['osuID']), announcementsChannel, "<@" + str(duser.id) + "> has received the **80%** role! Nice stuff! :tada:", medalcount, str(rounded))
                elif percentage >= 60 and oldPercentage < 60:
                    await duser.send("You have received the **60%** role! You're getting there! :tada:")
                    await sendPercentageUpdate(osu_user['username'], 60, "https://a.ppy.sh/" + str(user['osuID']), announcementsChannel, "<@" + str(duser.id) + "> has received the **60%** role! That's " + str(rounded) + "% of total medals! :tada:", medalcount, str(rounded))
                elif percentage >= 40 and oldPercentage < 40:
                    await duser.send("You have received the **40%** role! You're almost there! :tada:")
                    await sendPercentageUpdate(osu_user['username'], 40, "https://a.ppy.sh/" + str(user['osuID']), announcementsChannel, "<@" + str(duser.id) + "> has received the **40%** role! Thats a whole " + str(medalcount) + " medals! :tada:", medalcount, str(rounded))

                username = osu_user['username']
                # username should be
                # XX.X% | username
                roundpercentageforusername = str(round(percentage, 2))
                
                username = username + " | " + roundpercentageforusername + "%"
                # nickname the user to their osu username

                await duser.edit(nick=username)

                logmessage = "Reprocessed https://osu.ppy.sh/users/" + str(user["osuID"]) + " with " + str(medalcount) + " medals (" + str(percentage) + "%)"
                await logchannel.send(logmessage)
                await updateUser(duser.id, medalcount, percentage);
                # wait 1 second before sending the next message
                await asyncio.sleep(0.5)
                if amount == "specific":
                    break
            except Exception as e:
                print("error: " + str(e))
                logmessage = "Error processing user " + str(user["osuID"]) + ": " + str(e)
                logmessage += "\non line: " + str(sys.exc_info()[-1].tb_lineno)
                logmessage += "\nwith discord id: " + str(duser.id)
                await logchannel.send(logmessage)
                continue
        if amount == "all":
            processing = False
            await client.change_presence(status=discord.Status.online,activity=discord.Game(name="run oa!reprocessme to update your roles!"))
        if doneprocess is False:
            await channel.send("You are not currently authenticated. We've sent an authentication link, give that a go!")
            await author.send("Here's your auth link! - " + str(await requestAuthenticationToken(author)))

async def updateUser(discordId, medalCount, percentage):
    # this is to update the serverside database
    # we can send request to https://osekai.net/authenticator/api/update_user.php?discordId=<discordId>&medalCount=<medalCount>&percentage=<percentage>
    url = "https://osekai.net/authenticator/api/update_user.php"
    x = requests.get(url + "?discordId=" + str(discordId) + "&medalCount=" + str(medalCount) + "&percentage=" + str(percentage) + "&key=" + vars.key)
    print(x.text)

async def kickEveryone():
    return;
    # literally kick everyone from the server
    guild = client.get_guild(vars.serverid)
    for member in guild.members:
        if member.id != 880873784347873291 and member.id != 233170527458426880:
            await member.kick()
        


async def getAllMembers():
    guild = client.get_guild(vars.serverid)
    for member in guild.members:
        print(member.name)

import json

async def getStatus(discordid, channel):
    guild = client.get_guild(vars.serverid)
    duser = guild.get_member(int(discordid))
    if duser == None:
        await channel.send("User not found")
        return
    
    # get registration status from https://osekai.net/authenticator/api/users.php
    url = "https://osekai.net/authenticator/api/users.php?key=" + vars.key
    x = requests.get(url)
    users = json.loads(x.text)
    found = False
    vuser = 0;
    for user in users:
        if user["DiscordID"] == discordid:
            found = True
            vuser = user
            break
    if found == False:
        await channel.send("User not found")
        return
    
    # print user info in nice embed
    embed = discord.Embed(title="User info", description="", color=0x00ff00)
    embed.add_field(name="Discord ID", value=str(vuser["DiscordID"]), inline=False)
    embed.add_field(name="OSU ID", value=str(vuser["osuID"]), inline=False)
    embed.add_field(name="Medal count (stored)", value=str(vuser["MedalCount"]), inline=False)
    embed.add_field(name="Percentage", value=str(vuser["Percentage"]), inline=False)
    # get actual medal count from osu! api
    osu_user = osu_utils.get_user(vuser["osuID"])
    medalcount = 0
    # each medal is inside an array inside osu_
    for medal in osu_user['user_achievements']:
        medalcount += 1
    embed.add_field(name="Medal count (realtime)", value=str(medalcount), inline=False)
    await channel.send(embed=embed)



client.run('token')
