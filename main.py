import asyncio, logging, json, os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import web

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8834965252:AAH_wdNbp3ZlZhI_I-t4evcucw1ymiI9s20"
ADMIN_ID = 8132438068
CHANNEL_ID = -1003635455941
CHANNEL_URL = "tg://resolve?domain=damvaninfo"
WEBAPP_URL = "https://github.io"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

TEXTS = {
    "ru": {
        "sub_required": "подпишитесь на канал чтобы продолжить",
        "btn_sub": "Подписаться на канал",
        "btn_check_sub": "проверить подписку",
        "not_sub_alert": "подпишитесь на канал чтобы продолжить!",
        "create_here": "Создайте свою тему, нажав на кнопку внизу чата ↓",
        "btn_create": "Создать тему"
    },
    "en": {
        "sub_required": "subscribe to the channel to continue",
        "btn_sub": "Subscribe to channel",
        "btn_check_sub": "check subscription",
        "not_sub_alert": "subscribe to the channel to continue!",
        "create_here": "Create your theme by clicking the button below ↓",
        "btn_create": "Create theme"
    }
}

async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        logging.error(f"Ошибка подписки: {e}")
        return False

def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")]
    ])

def get_start_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["btn_sub"], url=CHANNEL_URL)],
        [InlineKeyboardButton(text=TEXTS[lang]["btn_check_sub"], callback_data=f"check_{lang}")]
    ])

def get_reply_creator_keyboard(lang):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["btn_create"], web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hello! Welcome to Damon Vane Theme, please choose a language to continue", reply_markup=ReplyKeyboardRemove())
    await message.answer("Choose a language:", reply_markup=get_lang_keyboard())

@dp.callback_query(F.data.startswith("lang_"))
async def process_language_choice(callback: CallbackQuery):
    lang = callback.data.replace("lang_", "")
    await callback.answer()
    await callback.message.answer(TEXTS[lang]["sub_required"], reply_markup=get_start_keyboard(lang))
    try:
        await callback.message.delete()
    except Exception:
        pass

@dp.callback_query(F.data.startswith("check_"))
async def process_check_sub(callback: CallbackQuery):
    lang = callback.data.replace("check_", "")
    user_id = callback.from_user.id
    
    if await check_subscription(user_id):
        await callback.answer()
        await callback.message.answer(TEXTS[lang]["create_here"], reply_markup=get_reply_creator_keyboard(lang))
        try:
            await callback.message.delete()
        except Exception:
            pass
    else:
        await callback.answer(TEXTS[lang]["not_sub_alert"], show_alert=True)

@dp.message(F.web_app_data)
async def process_webapp_data(message: Message):
    lang = "ru"
    try:
        data = json.loads(message.web_app_data.data)
        theme_url = data.get("url")
        bg = data.get("bg")
        text = data.get("text")
        accent = data.get("accent")
        device = data.get("device", "android").upper()
        has_wp = data.get("has_wallpaper", "Нет")
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Установить тему 📥", url=theme_url)]
        ])
        
        success_text = (
            f"✨ **Ваша кастомная тема готова!** ✨\n\n"
            f"📱 Платформа: `{device}`\n"
            f"🎨 Цвет фона: `{bg}`\n"
            f"📝 Цвет текста: `{text}`\n"
            f"⚡️ Акцент: `{accent}`\n"
            f"🖼 Собственные обои: `{has_wp}`\n\n"
            f"Нажмите на кнопку ниже, чтобы применить настройки конфигурации интерфейса:"
        )
        await message.answer(success_text, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка WebApp данных: {e}")

async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    asyncio.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get('/', handle)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
