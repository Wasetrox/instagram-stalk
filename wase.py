import os
import asyncio
import json
from datetime import datetime
from instagrapi import Client
from instagrapi.types import DirectThread
import discord
from discord.ext import commands
from discord import Embed, Colour
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_USER_ID = int(os.getenv("DISCORD_USER_ID"))
SPECIFIC_SENDER_USERNAME = os.getenv("SPECIFIC_SENDER_USERNAME")
MONITORED_USERNAME = os.getenv("MONITORED_USERNAME")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

cl = Client()
session_file = "session.json"

processed_message_ids = set()
previous_followers = set()
previous_following = set()
state_file = "user_state.json"
user_cache = {}

def load_state():
    global previous_followers, previous_following
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
            previous_followers = set(state.get("followers", []))
            previous_following = set(state.get("following", []))
        logging.info("Durum dosyası başarıyla yüklendi.")
    except FileNotFoundError:
        logging.info("Durum dosyası bulunamadı, yeni oluşturulacak.")

def save_state():
    state = {
        "followers": list(previous_followers),
        "following": list(previous_following)
    }
    with open(state_file, "w") as f:
        json.dump(state, f)
    logging.info("Durum dosyasına kaydedildi.")

def login_instagram():
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            logging.info("Oturum dosyası yüklendi.")
            return True
        except Exception as e:
            logging.error(f"Oturum yüklenirken hata: {e}")
    try:
        verification_code = None
        if os.getenv("INSTAGRAM_2FA_ENABLED") == "true":
            verification_code = input("2FA kodunu girin: ")
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, verification_code=verification_code)
        cl.dump_settings(session_file)
        logging.info("Yeni oturum oluşturuldu ve kaydedildi.")
        return True
    except Exception as e:
        logging.error(f"Instagram girişi başarısız: {e}")
        return False

if not login_instagram():
    raise Exception("Instagram'a giriş yapılamadı. Lütfen kullanıcı adı ve şifreyi kontrol edin.")

async def get_user_info(user_id):
    try:
        if user_id in user_cache:
            logging.info(f"Önbellekten kullanıcı bilgisi alındı: {user_id}")
            return user_cache[user_id]
        user_info = cl.user_info(user_id)
        username = user_info.username
        user_info = cl.user_info_by_username(username)
        user_cache[user_id] = user_info
        logging.info(f"Kullanıcı bilgisi alındı: {username}")
        return user_info
    except Exception as e:
        logging.error(f"Kullanıcı bilgisi alınırken hata (user_id: {user_id}): {e}")
        return None

async def check_followers_following():
    while True:
        try:
            monitored_user = cl.user_info_by_username(MONITORED_USERNAME)
            current_followers = set(cl.user_followers(monitored_user.pk, amount=50).keys())
            current_following = set(cl.user_following(monitored_user.pk, amount=50).keys())

            new_followers = current_followers - previous_followers
            for user_id in new_followers:
                user_info = await get_user_info(user_id)
                if user_info:
                    discord_user = await bot.fetch_user(DISCORD_USER_ID)
                    embed = Embed(
                        title="Yeni Takipçi!",
                        description=f"**{MONITORED_USERNAME}**'ı yeni bir kullanıcı takip etmeye başladı.",
                        colour=Colour.green(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Kullanıcı Adı", value=user_info.username, inline=True)
                    embed.add_field(name="Ad Soyad", value=user_info.full_name or "Bilinmiyor", inline=True)
                    embed.add_field(name="Takipçi Sayısı", value=str(user_info.follower_count), inline=True)
                    embed.add_field(name="Profil", value=f"[Tıkla](https://www.instagram.com/{user_info.username}/)", inline=True)
                    if user_info.profile_pic_url:
                        embed.set_thumbnail(url=user_info.profile_pic_url)
                    embed.set_footer(text="Instagram Takip Bildirimi")
                    await discord_user.send(embed=embed)
                    logging.info(f"Yeni takipçi: {user_info.username}")

            lost_followers = previous_followers - current_followers
            for user_id in lost_followers:
                user_info = await get_user_info(user_id)
                if user_info:
                    discord_user = await bot.fetch_user(DISCORD_USER_ID)
                    embed = Embed(
                        title="Takipçi Kaybı!",
                        description=f"**{MONITORED_USERNAME}**'ı bir kullanıcı takip etmeyi bırakta.",
                        colour=Colour.red(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Kullanıcı Adı", value=user_info.username, inline=True)
                    embed.add_field(name="Ad Soyad", value=user_info.full_name or "Bilinmiyor", inline=True)
                    embed.add_field(name="Takipçi Sayısı", value=str(user_info.follower_count), inline=True)
                    embed.add_field(name="Profil", value=f"[Tıkla](https://www.instagram.com/{user_info.username}/)", inline=True)
                    if user_info.profile_pic_url:
                        embed.set_thumbnail(url=user_info.profile_pic_url)
                    embed.set_footer(text="Instagram Takip Bildirimi")
                    await discord_user.send(embed=embed)
                    logging.info(f"Takipçi kaybı: {user_info.username}")

            new_following = current_following - previous_following
            for user_id in new_following:
                user_info = await get_user_info(user_id)
                if user_info:
                    discord_user = await bot.fetch_user(DISCORD_USER_ID)
                    embed = Embed(
                        title="Yeni Takip!",
                        description=f"**{MONITORED_USERNAME}** yeni bir kullanıcıyı takip etmeye başladı.",
                        colour=Colour.blue(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Kullanıcı Adı", value=user_info.username, inline=True)
                    embed.add_field(name="Ad Soyad", value=user_info.full_name or "Bilinmiyor", inline=True)
                    embed.add_field(name="Takipçi Sayısı", value=str(user_info.follower_count), inline=True)
                    embed.add_field(name="Profil", value=f"[Tıkla](https://www.instagram.com/{user_info.username}/)", inline=True)
                    if user_info.profile_pic_url:
                        embed.set_thumbnail(url=user_info.profile_pic_url)
                    embed.set_footer(text="Instagram Takip Bildirimi")
                    await discord_user.send(embed=embed)
                    logging.info(f"Yeni takip edilen: {user_info.username}")

            lost_following = previous_following - current_following
            for user_id in lost_following:
                user_info = await get_user_info(user_id)
                if user_info:
                    discord_user = await bot.fetch_user(DISCORD_USER_ID)
                    embed = Embed(
                        title="Takip Bırakıldı!",
                        description=f"**{MONITORED_USERNAME}** bir kullanıcıyı takip etmeyi bırakta.",
                        colour=Colour.orange(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="Kullanıcı Adı", value=user_info.username, inline=True)
                    embed.add_field(name="Ad Soyad", value=user_info.full_name or "Bilinmiyor", inline=True)
                    embed.add_field(name="Takipçi Sayısı", value=str(user_info.follower_count), inline=True)
                    embed.add_field(name="Profil", value=f"[Tıkla](https://www.instagram.com/{user_info.username}/)", inline=True)
                    if user_info.profile_pic_url:
                        embed.set_thumbnail(url=user_info.profile_pic_url)
                    embed.set_footer(text="Instagram Takip Bildirimi")
                    await discord_user.send(embed=embed)
                    logging.info(f"Takip etmeyi bırakan: {user_info.username}")

            previous_followers.clear()
            previous_followers.update(current_followers)
            previous_following.clear()
            previous_following.update(current_following)
            save_state()

        except Exception as e:
            logging.error(f"Takipçi/takip edilen kontrolü sırasında hata: {e}")
            if "login_required" in str(e).lower() or "jsondecodeerror" in str(e).lower():
                logging.info("Oturum geçersiz, yeniden giriş yapılıyor...")
                if login_instagram():
                    logging.info("Oturum yenilendi, kontrol devam ediyor.")
                else:
                    logging.error("Oturum yenileme başarısız, kontrol durduruluyor.")
                    await asyncio.sleep(600)
        await asyncio.sleep(600)

async def check_instagram_messages():
    while True:
        try:
            threads = cl.direct_threads(amount=10)
            for thread in threads:
                if thread.messages:
                    last_message = thread.messages[0]
                    message_id = last_message.id
                    if message_id not in processed_message_ids:
                        sender = last_message.user_id
                        try:
                            user_info = await get_user_info(sender)
                            if user_info and user_info.username == SPECIFIC_SENDER_USERNAME:
                                discord_user = await bot.fetch_user(DISCORD_USER_ID)
                                message_text = last_message.text
                                embed = Embed(
                                    title="Yeni Instagram Mesajı",
                                    description=f"**{user_info.username}**'dan yeni bir mesaj geldi.",
                                    colour=Colour.purple(),
                                    timestamp=datetime.now()
                                )
                                embed.add_field(name="Mesaj", value=message_text, inline=False)
                                embed.set_footer(text="Instagram DM Bildirimi")
                                await discord_user.send(embed=embed)
                                processed_message_ids.add(message_id)
                                logging.info(f"İşlenen mesaj ID: {message_id}")
                        except Exception as e:
                            logging.error(f"Kullanıcı bilgisi alınırken hata: {e}")
        except Exception as e:
            logging.error(f"Mesaj kontrolü sırasında hata: {e}")
            if "login_required" in str(e).lower() or "jsondecodeerror" in str(e).lower():
                logging.info("Oturum geçersiz, yeniden giriş yapılıyor...")
                if login_instagram():
                    logging.info("Oturum yenilendi, kontrol devam ediyor.")
                else:
                    logging.error("Oturum yenileme başarısız, kontrol durduruluyor.")
                    await asyncio.sleep(600)
        await asyncio.sleep(120)

@bot.event
async def on_ready():
    logging.info(f"Discord botu {bot.user} olarak giriş yaptı!")
    load_state()

    try:
        monitored_user = cl.user_info_by_username(MONITORED_USERNAME)
        discord_user = await bot.fetch_user(DISCORD_USER_ID)
        embed = Embed(
            title=f"{MONITORED_USERNAME} Profili",
            description="Bot başlatıldı! İşte izlenen hesabın mevcut bilgileri:",
            colour=Colour.dark_blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Kullanıcı Adı", value=monitored_user.username, inline=True)
        embed.add_field(name="Ad Soyad", value=monitored_user.full_name or "Bilinmiyor", inline=True)
        embed.add_field(name="Takipçi Sayısı", value=str(monitored_user.follower_count), inline=True)
        embed.add_field(name="Takip Edilen Sayısı", value=str(monitored_user.following_count), inline=True)
        embed.add_field(name="Biyografi", value=monitored_user.biography or "Yok", inline=False)
        embed.add_field(name="Profil", value=f"[Tıkla](https://www.instagram.com/{monitored_user.username}/)", inline=True)
        if monitored_user.profile_pic_url:
            embed.set_thumbnail(url=monitored_user.profile_pic_url)
        embed.set_footer(text="Instagram Profil Özeti")
        await discord_user.send(embed=embed)
        logging.info(f"Başlangıç bilgileri gönderildi: {MONITORED_USERNAME}")
    except Exception as e:
        logging.error(f"Başlangıç bilgileri alınırken hata: {e}")
        discord_user = await bot.fetch_user(DISCORD_USER_ID)
        await discord_user.send(f"**Hata:** {MONITORED_USERNAME} profil bilgileri alınamadı: {e}")

    bot.loop.create_task(check_instagram_messages())
    bot.loop.create_task(check_followers_following())

@bot.event
async def on_message(message):
    if message.author.id == DISCORD_USER_ID and isinstance(message.channel, discord.DMChannel):
        try:
            target_user = cl.user_info_by_username(SPECIFIC_SENDER_USERNAME)
            cl.direct_send(message.content, [target_user.pk])
            embed = Embed(
                title="Mesaj Gönderildi",
                description=f"Mesaj **{SPECIFIC_SENDER_USERNAME}** kullanıcısına Instagram üzerinden gönderildi.",
                colour=Colour.gold(),
                timestamp=datetime.now()
            )
            embed.add_field(name="Gönderilen Mesaj", value=message.content, inline=False)
            embed.set_footer(text="Instagram DM Bildirimi")
            await message.channel.send(embed=embed)
            logging.info(f"Mesaj gönderildi: {message.content}")
        except Exception as e:
            await message.channel.send(f"Mesaj gönderilirken hata: {e}")
            logging.error(f"Mesaj gönderilirken hata: {e}")
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)