import os
from random import randrange
import discord
from discord import Guild

client = discord.Client(activity=discord.Game(name="!verify"))

ids = []
cash = []
level = []
exp = []
exp_boost = []
cash_boost = []
guard = []
pistol = []

no = "\u26d4"
yes = "\u2705"
red = 0xff0000
green = 0x00ff80


@client.event
async def on_message(message):
    if is_verified(message.author):
        c = get_c_by_author(message.author)
        await increase_exp(c)
        if message.content[0] == "c!":
            if message.content.startswith("c!bal"):
                await send(title="Your balance: ", color=green, description=cash[c])
            elif message.content.startswith("c!level"):
                await show_level(c)
            elif message.content.startswith("c!owner"):
                await send(title="Cringegod#2404 is my owner", color=green)
            elif message.content.startswith("c!bust"):
                try:
                    await bust_user(message.author, message.content.split(" ")[1])
                except IndexError:
                    await send(title="Incorrect syntax", description="bust [username]", color=red)
            elif message.content.startswith("c!unbust"):
                try:
                    await unbust_user(message.author, message.content.split(" ")[1])
                except IndexError:
                    await send(title="Incorrect syntax", description="unbust [username]", color=red)
            elif message.content.startswith("c!send"):
                try:
                    send_cash(c, await get_c_by_username(message.content.split(" ")[1]), int(message.content.split(" ")[2]))
                except IndexError:
                    await send(title="Incorrect syntax", description="send [username] [amount]", color=red)
            elif message.content.startswith("c!bet"):
                try:
                    await bet(c, int(message.content.split(" ")[1]))
                except IndexError:
                    await send(title="Incorrect syntax", description="bet [amount]", color=red)
            elif message.content.startswith("c!leaderboard"):
                await leaderboard()
            elif message.content.startswith("c!boosts"):
                await send(title="Your boosts",
                           description=f"cashboost: x{cash_boost[c] * 2}\nxpboost: x{exp_boost[c] * 2}", color=green)
            elif message.content.startswith("c!shop"):
                await shop()
            elif message.content.startswith("c!buy"):
                try:
                    if len(message.content.split(" ")) == 2:
                        await buy(c, message.content.split(" ")[1])
                    else:
                        await buy(c, message.content.split(" ")[1], int(message.content.split(" ")[2]))
                except IndexError:
                    await send(title="Incorrect syntax", description="buy [product] ([amount])", color=red)
            elif message.content.startswith("c!rob"):
                try:
                    await rob(c, await get_c_by_username(message.content.split(" ")[1]))
                except IndexError:
                    await send(title="Incorrect syntax", description="rob [username]", color=red)
            elif message.content.startswith("c!debug"):
                if is_owner(message.author):
                    if message.content.split(" ")[1] == "cash":
                        try:
                            give_cash(await get_c_by_username(message.content.split(" ")[2]),
                                      int(message.content.split(" ")[3]))
                        except IndexError:
                            await send(title="Incorrect syntax", description="debug cash [username] [amount]", color=red)
                    elif message.content.split(" ")[1] == "level":
                        try:
                            give_level(await get_c_by_username(message.content.split(" ")[2]),
                                       int(message.content.split(" ")[3]))
                        except IndexError:
                            await send(title="Incorrect syntax", description="debug level [username] [amount]", color=red)
                    elif message.content.split(" ")[1] == "shutdown":
                        await client.close()
                else:
                    await send(title=f"Unfortunately you don't have the required permissions {no}", color=red)
            save_to_txt()
    elif message.content.startswith("c!verify"):
        c = get_c_by_author(message.author)
        if c == len(ids):
            ids.append(message.author.id)
            cash.append(1000)
            level.append(1)
            exp.append(0)
            exp_boost.append(0)
            cash_boost.append(0)
            guard.append(0)
            pistol.append(0)
            save_to_txt()
            await send(title=f"You are now verified {yes}", color=green)
        else:
            await send(title=f"You are already verified {yes}", color=red)
    else:
        if message.author.id != 915564829320814592 and message.content[0] == "c!":
            await send(title="You aren't verified", color=red, description="Verify yourself with c!verify")


@client.event
async def on_ready():
    await send(title="I'm now online!", color=green)
    with open("status.txt") as f1:
        for line in f1:
            (id1, cash1, level1, exp1, exp_boost1, cash_boost1, guard1, pistol1, daily1) = line.split(" ")
            ids.append(int(id1))
            cash.append(int(cash1))
            level.append(int(level1))
            exp.append(int(exp1))
            exp_boost.append(int(exp_boost1))
            cash_boost.append(int(cash_boost1))
            guard.append(int(guard1))
            pistol.append(int(pistol1))


def save_to_txt():
    with open("status.txt", "w") as f1:
        for i in range(len(ids)):
            f1.write(f"{ids[i]} {cash[i]} {level[i]} {exp[i]} {exp_boost[i]} {cash_boost[i]} {guard[i]} {pistol[i]}\n")


async def show_level(c):
    embed = discord.Embed(title="Your level", color=green)
    embed.add_field(name=level[c], value="You're missing " + str(level[c] * 10 - exp[c]) + "xp for next level")
    await send(embed=embed)


async def bet(c, amount):
    if cash[c] >= amount:
        you = randrange(1, 6)
        bot = randrange(1, 6)
        color = green
        embed = discord.Embed(title="Bet")
        embed.add_field(name="You:", value=str(you))
        embed.add_field(name="Bot", value=str(bot))
        if you > bot:
            if cash_boost[c] > 0:
                embed.description = f"You won {amount * cash_boost[c] * 2}$"
                cash[c] += amount * cash_boost[c] * 2
            else:
                embed.description = f"You won {amount}$"
                cash[c] += amount
        elif bot > you:
            embed.description = f"You lost {amount}$"
            cash[c] -= amount
            color = red
        elif bot == you:
            embed.description = "Draw!"
            color = 0xffff00
        embed.colour = color
        await send(embed=embed)
    else:
        await send(title="You don't have that much!", color=green)


async def leaderboard():
    level1 = sorted(level, reverse=True)
    k = 1
    embed = discord.Embed(title="Leaderboard", color=green)
    for i in range(len(ids)):
        for j in range(len(ids)):
            if level1[i] == level[j]:
                user = await client.fetch_user(ids[j])
                embed.add_field(name=f"{k}. {user.display_name}", value=f"Level {level[j]}\n{cash[j]}$")
                k += 1
    await send(embed=embed)


async def bust_user(author, user):
    userid = await get_id_by_discord_name(user)
    if userid != 0:
        guild = await client.fetch_guild(891248820451676240)
        user = await Guild.fetch_member(guild, userid)
        author = await Guild.fetch_member(guild, author.id)
        if author.top_role == discord.utils.get(guild.roles, id=913102966410588180):
            await user.add_roles(discord.utils.get(guild.roles, id=919146149888286731))
            await send(title=f"Done {yes}", color=green)
        else:
            await send(title=f"Unfortunately you don't have the required permissions {no}", color=red)
    else:
        await send(title=f"Wrong username {no}", color=red)


async def unbust_user(author, user):
    userid = await get_id_by_discord_name(user)
    if userid != 0:
        guild = await client.fetch_guild(891248820451676240)
        user = await Guild.fetch_member(guild, userid)
        author = await Guild.fetch_member(guild, author.id)
        if author.top_role == discord.utils.get(guild.roles, id=913102966410588180):
            await user.remove_roles(discord.utils.get(guild.roles, id=919146149888286731))
            await send(title=f"Done {yes}", color=green)
        else:
            await send(title=f"Unfortunately you don't have the required permissions {no}", color=red)
    else:
        await send(title=f"Wrong username {no}", color=red)


async def increase_exp(c):
    if exp_boost == 0:
        exp[c] += randrange(1, 9)
    else:
        exp[c] += randrange(1, 9) * exp_boost[c] * 2
    await check_level_up(c)


async def check_level_up(c):
    if exp[c] >= level[c] * 10:
        exp[c] -= level[c] * 10
        level[c] += 1
        await send(title=f"Level up! You're now level {level[c]}", color=green)


async def shop():
    embed = discord.Embed(title="Shop", color=green)
    embed.add_field(name="1. xpboost * 2", value="1000$", inline=False)
    embed.add_field(name="2. cashboost * 2", value="1000$", inline=False)
    embed.add_field(name="3. guard", value="10000$", inline=False)
    embed.add_field(name="4. pistol", value="8000$", inline=False)
    embed.set_footer(text="Buy things with !buy [name of product]")
    await send(embed=embed)


async def buy(c, product, amount=1):
    if product.casefold() == "xpboost":
        if cash[c] - 1000 * amount >= 0:
            exp_boost[c] += amount
            cash[c] -= 1000 * amount
            await send(f"Bought {amount} {product}", "", green)
        else:
            await send(f"Not enough money {no}", "", red)
    elif product.casefold() == "cashboost":
        if cash[c] - 1000 * amount >= 0:
            cash_boost[c] += amount
            cash[c] -= 1000 * amount
            await send(f"Bought {amount} {product}", "", green)
        else:
            await send(f"Not enough money {no}", "", red)
    elif product.casefold() == "guard":
        if cash[c] - 10000 * amount >= 0:
            guard[c] += amount
            cash[c] -= 10000 * amount
            await send(f"Bought {amount} {product}", "", green)
        else:
            await send(f"Not enough money {no}", "", red)
    elif product.casefold() == "pistol":
        if cash[c] - 8000 * amount >= 0:
            pistol[c] += 1 * amount
            cash[c] -= 8000 * amount
            await send(f"Bought {amount} {product}", "", green)
        else:
            await send(f"Not enough money {no}", "", red)
    else:
        await send(title="Product Not Found", description="Possible products are: xpboost, cashboost, guard and pistol", color=red)


async def rob(author, user):
    random_num = randrange(1, 100)
    random_num -= guard[user]
    random_num += pistol[author]
    if random_num <= 50:
        lost_cash = (cash[author] * 0.1).__round__()
        cash[author] -= lost_cash
        cash[user] += lost_cash
        await send(title=f"Robbing failed. It cost you {lost_cash}$", color=red)
    else:
        won_cash = (cash[user] * 0.1).__round__()
        cash[author] += won_cash
        cash[user] -= won_cash
        await send(title=f"Robbing succeeded. You robbed {won_cash}$", color=green)


def get_c_by_author(author):
    id1 = author.id
    c = 0
    for i in ids:
        if id1 == i:
            break
        c += 1
    return c


async def get_c_by_username(username):
    id1 = await get_id_by_discord_name(username)
    return get_c_by_author(await client.fetch_user(id1))


async def send(title="", description="", color=None, embed=None):
    if embed is None:
        await client.get_channel(891248820451676243).send(
            embed=discord.Embed(title=title, description=description, color=color))
    else:
        await client.get_channel(891248820451676243).send(embed=embed)


async def get_id_by_discord_name(name):
    id1 = 0
    for i in ids:
        user = await client.fetch_user(i)
        if user.display_name == name:
            id1 = i
            break
    return id1


def send_cash(sender, recipient, amount):
    if cash[sender] - amount >= 0:
        cash[sender] -= amount
        cash[recipient] += amount


def is_verified(author):
    return not len(ids) == get_c_by_author(author) and author.id != 915564829320814592


def is_owner(author):
    return author.id == 671696567555588096


def give_cash(user, amount):
    cash[user] += amount


def give_level(user, amount):
    level[user] += amount


client.run(os.environ['token'])
