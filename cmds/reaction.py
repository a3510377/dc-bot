import discord
import random
import asyncio
import datetime

from discord.ext import commands
from datetime import datetime
from datahook import yamlhook

class reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    channel_ticket = None
    ticket_creator = None

    ydata = yamlhook("channel.yaml").load()

    if (ydata == None or type(ydata['ID']) is not list):
        ydata['ID'] = []

    yamlhook("channel.yaml").Operate('ID', ydata['ID'])

    if (ydata == None or type(ydata['USER']) is not list):
        ydata['USER'] = []

    yamlhook("channel.yaml").Operate('USER', ydata['USER'])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        MESSAGE_ID = 800279346799444008
        CATEGORY_ID = 800231308672499713
        BOT_ID = 593746376404500490
        LOG_CHANNEL_ID = 800042340600643644
        ROLE_ID = 701784905755000874
        CHANNEL_ID = 800279155341918209

        guild_id = payload.guild_id
        guild = self.bot.get_guild(guild_id)
        user_id = payload.user_id
        user = self.bot.get_user(user_id)
        message_id = payload.message_id
        channel = self.bot.get_channel(payload.channel_id)

        # TICKETS
        emoji = payload.emoji.name

        if message_id == MESSAGE_ID and emoji == "📩":
            self.ticket_creator = user_id

            message = await channel.fetch_message(message_id)
            await message.remove_reaction("📩", user)

            ydata = yamlhook("channel.yaml").load()
            if payload.user_id not in ydata['USER']:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                support_role = guild.get_role(ROLE_ID)
                category = guild.get_channel(CATEGORY_ID)
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                ticket_nr = random.randint(0, 9999)
                self.channel_ticket = await category.create_text_channel(f'{member}的匿名-{ticket_nr}', overwrites=overwrites)

                embed = discord.Embed(title="心裡有話沒地方說嗎??",color=0x0000ff)
                embed.set_author(name="匿名機器人")
                embed.add_field(name='匿名格式:', value='```-匿名模式 (1️⃣/2️⃣)：\n''-內容： \n''> \n''> \n''>  ```', inline=False)

                embed.add_field(name='這裡可以讓你匿名說出來喔!!.', value=':white_check_mark: - 輸入完畢時請點選此貼圖來通知管理員處理\n:lock: - 關閉此匿名頻道 \n:floppy_disk: - 儲存頻道聊天紀錄 `管理員專用`', inline=False)

                await self.channel_ticket.send(f"{member.mention}")

                msg = await self.channel_ticket.send(embed=embed)

                await msg.add_reaction("✅")
                await asyncio.sleep(0.3)
                await msg.add_reaction("🔒")
                await asyncio.sleep(0.3)
                await msg.add_reaction("💾")
                embedd = discord.Embed(title='使用說明', color=0x0000ff)
                embedd.add_field(name='匿名模式', value=
                                                    '```1️⃣ 公開匿名留言說明\n'
                                                    '幫你們把留言以匿名公開出來\n'
                                                    '只有擁有 @♕蹦蹦老大♕ \n'
                                                    '的兩位群主知道是你留的言。\n'
                                                    '---------------------------------\n'
                                                    '2️⃣ 蹦蹦聽你說說明\n'
                                                    '是讓你們訴說心事.煩惱之類的\n'
                                                    '一樣只有擁有 @♕蹦蹦老大♕ \n'
                                                    '的兩位群主知道並且不會公開給他人知道```')
                embedd.add_field(name='範例', value='-匿名模式 (1️⃣/2️⃣)：1️⃣\n'
                                                    '-內容： \n'
                                                    '> XXX\n'
                                                    '> XXX\n'
                                                    '> XXX')
                await self.channel_ticket.send(embed=embedd)
                try:
                    ydata = yamlhook("channel.yaml").load()
                    ydata['ID'].append(msg.id)
                    yamlhook("channel.yaml").Operate('ID', ydata['ID'])
                except ValueError:
                    print("not add or return1")

                try:
                    ydata = yamlhook("channel.yaml").load()
                    ydata['USER'].append(payload.user_id)
                    yamlhook("channel.yaml").Operate('USER', ydata['USER'])
                except ValueError:
                    print("not add or return2")
            else:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                channel1 = self.bot.get_channel(CHANNEL_ID)
                OAO = await channel1.send(f'{member.mention}您已開啟匿名頻道,請勿重複開啟')
                await asyncio.sleep(5)
                await OAO.delete()

        ydata = yamlhook("channel.yaml").load()
        if payload.message_id in ydata['ID']:

            if emoji == "✅" and user_id != BOT_ID:
                message = await channel.fetch_message(message_id)
                await message.remove_reaction("✅", user)
                await channel.send(f"此匿名頻道 <#{payload.channel_id}> 已通知管理員,請等待處理. <@&{ROLE_ID}>")

            if 800007570483707965 in list(map(lambda x: x.id, payload.member.roles)):
                if emoji == "💾" and user_id != BOT_ID:
                    message = await channel.fetch_message(message_id)
                    await message.remove_reaction("💾", user)

                    now = datetime.now()
                    time = now.strftime(str("%d.%m.%Y") + " at " + str("%H:%M"))

                    channel_log = self.bot.get_channel(LOG_CHANNEL_ID)

                    messages = await channel.history(limit=None).flatten()

                    file = open(f"{channel}.html", "a", encoding='utf8')
                    for i in messages:
                        file.write(f'[{i.created_at}]{i.author} | {i.channel.name} | {i.content}<br> \n')
                    file.close()

                    await channel_log.send(f" <#{payload.channel_id}> `{channel}` 頻道存檔紀錄")
                    await channel_log.send(file=discord.File(f"{channel}.html"))

                    text = f"此匿名 <#{payload.channel_id}> 以儲存, 操作者 {user.mention} 在 {time} 儲存."
                    embed = discord.Embed(
                        title="儲存匿名!",
                        description=text,
                        color=0x0000ff)

                    await channel.send(embed=embed)

            if emoji == "🔒" and user_id != BOT_ID:
                message = await channel.fetch_message(message_id)
                await message.remove_reaction("🔒", user)

                now = datetime.now()
                time = now.strftime(str("%d.%m.%Y") + " at " + str("%H:%M"))

                channel_log = self.bot.get_channel(LOG_CHANNEL_ID)
                text = f"此匿名 `{channel}` 即將關閉, 操作者 {user.mention} 在 {time} 刪除."

                embed = discord.Embed(
                    title="關閉匿名!",
                    description=text,
                    color=0x0000ff)

                await channel_log.send(embed=embed)

                embed = discord.Embed(
                    title="關閉匿名!",
                    description=f":tickets: 匿名已關閉,操作者: {user.mention}.",
                    color=0x0000ff)

                await channel.send(embed=embed)

                try:
                    ydata = yamlhook("channel.yaml").load()
                    ydata['ID'].remove(payload.message_id)
                    yamlhook("channel.yaml").Operate('ID', ydata['ID'])
                except ValueError:
                    print("no id")

                try:
                    ydata = yamlhook("channel.yaml").load()
                    ydata['USER'].remove(payload.user_id)
                    yamlhook("channel.yaml").Operate('USER', ydata['USER'])
                except ValueError:
                    print("not add or return2")

                await asyncio.sleep(3)
                await channel.delete()

def setup(bot):
    bot.add_cog(reaction(bot))