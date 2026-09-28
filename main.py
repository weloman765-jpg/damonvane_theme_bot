import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
)
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

logging.basicConfig(level=logging.INFO)

# ================= НАСТРОЙКИ БОТА =================
BOT_TOKEN = "8834965252:AAH_wdNbp3ZlZhI_I-t4evcucw1ymiI9s20"
ADMIN_ID = 8132438068
CHANNEL_ID = -1003635455941
CHANNEL_URL = "https://t.me"
# ===================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния бота
class BotState(StatesGroup):
    language = State()       # Состояние выбора языка
    bg_color = State()       # Шаги конструктора
    text_color = State()
    accent_color = State()

# Текстовая база данных для двух языков
TEXTS = {
    "ru": {
        "sub_required": "Здравствуйте! Вас приветствует бот Дэймон Вэйн Темы, подпишитесь на канл чтобы продолжить",
        "btn_sub": "Подписаться на канал",
        "btn_check_sub": "проверить подписку",
        "not_sub_alert": "подпишитесь на канал чтобы продолжить!",
        "create_here": "Создайте свою тему тут↓",
        "btn_create": "Создать тему",
        "step_bg": "Отправьте код цвета для фона чата (например, #1a1a1a):",
        "step_text": "Теперь отправьте код цвета для текста сообщений (например, #ffffff):",
        "step_accent": "Отправьте код для второго цвета (элементы интерфейса):",
        "wrong_format": "Неверный формат. Код цвета должен быть вида #FFFFFF. Попробуйте еще раз:",
        "success": "Тема создана.\n\nЦвет фона: {bg}\nЦвет текста: {text}\nВторой цвет: {accent}\n\nНажмите на кнопку ниже, чтобы применить её:",
        "btn_install": "Установить тему"
    },
    "en": {
        "sub_required": "Hello! Welcome to Damon Vane Themes bot, please subscribe to the channel to continue",
        "btn_sub": "Subscribe to channel",
        "btn_check_sub": "check subscription",
        "not_sub_alert": "subscribe to the channel to continue!",
        "create_here": "Create your theme here↓",
        "btn_create": "Create theme",
        "step_bg": "Send the color code for the chat background (for example, #1a1a1a):",
        "step_text": "Now send the color code for the message text (for example, #ffffff):",
        "step_accent": "Send the code for the second color (interface elements):",
        "wrong_format": "Invalid format. The color code must be like #FFFFFF. Try again:",
        "success": "Theme created.\n\nBackground color: {bg}\nText color: {text}\nSecond color: {accent}\n\nClick the button below to apply it:",
        "btn_install": "Install theme"
    }
}

# Функция проверки подписки на ТГК
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

# Клавиатура выбора языка
def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru")],
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")]
    ])

# Клавиатура подписки под выбранный язык
def get_start_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["btn_sub"], url=CHANNEL_URL)],
        [InlineKeyboardButton(text=TEXTS[lang]["btn_check_sub"], callback_data="check_sub")]
    ])

# Клавиатура создания темы под выбранный язык
def get_creator_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["btn_create"], callback_data="start_create_theme")]
    ])

# --- ОБРАБОТКА КОМАНДЫ /START (ВЫБОР ЯЗЫКА НА АНГЛИЙСКОМ) ---
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Вас приветствует Damon Vane Темы, выберите язык чтобы продолжить",
        reply_markup=get_lang_keyboard()
    )

# --- ОБРАБОТКА КОМАНДЫ /CREATE ИЗ МЕНЮ ---
@dp.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru") # Если язык не выбран, по умолчанию русский
    
    if not await check_subscription(message.from_user.id):
        await message.answer(TEXTS[lang]["sub_required"], reply_markup=get_start_keyboard(lang))
        return
    
    await message.answer(TEXTS[lang]["step_bg"])
    await state.set_state(BotState.bg_color)

# --- СОХРАНЕНИЕ ВЫБРАННОГО ЯЗЫКА И ВЫДАЧА ПОДПИСКИ ---
@dp.callback_query(F.data.startswith("lang_"))
async def process_language_choice(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang) # Сохраняем язык в память сессии
    await callback.answer()
    await callback.message.delete()
    
    # Отправляем сообщение на выбранном языке
    await callback.message.answer(
        TEXTS[lang]["sub_required"],
        reply_markup=get_start_keyboard(lang)
    )

# --- ПРОВЕРКА ПОДПИСКИ ПРИ НАЖАТИИ КНОПКИ ---
@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")
    
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer(
            TEXTS[lang]["create_here"], 
            reply_markup=get_creator_keyboard(lang)
        )
    else:
        await callback.answer(TEXTS[lang]["not_sub_alert"], show_alert=True)

# --- ШАГ 1 КОНСТРУКТОРА: ЗАПУСК И ЦВЕТ ФОНА ---
@dp.callback_query(F.data == "start_create_theme")
async def start_theme_creation(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")
    
    if not await check_subscription(callback.from_user.id):
        await callback.answer(TEXTS[lang]["not_sub_alert"], show_alert=True)
        return
        
    await callback.answer()
    await callback.message.answer(TEXTS[lang]["step_bg"])
    await state.set_state(BotState.bg_color)

# --- ШАГ 2 КОНСТРУКТОРА: ЦВЕТ ТЕКСТА ---
@dp.message(BotState.bg_color)
async def process_bg_color(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")
    color = message.text.strip()
    
    if not color.startswith("#") or len(color) != 7:
        await message.answer(TEXTS[lang]["wrong_format"])
        return
        
    await state.update_data(bg_color=color)
    await message.answer(TEXTS[lang]["step_text"])
    await state.set_state(BotState.text_color)

# --- ШАГ 3 КОНСТРУКТОРА: ВТОРОЙ ЦВЕТ ---
@dp.message(BotState.text_color)
async def process_text_color(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")
    color = message.text.strip()
    
    if not color.startswith("#") or len(color) != 7:
        await message.answer(TEXTS[lang]["wrong_format"])
        return
        
    await state.update_data(text_color=color)
    await message.answer(TEXTS[lang]["step_accent"])
    await state.set_state(BotState.accent_color)

# --- ФИНАЛ: ВЫДАЧА ССЫЛКИ НА ТЕМУ + КНОПКА СТАРТА ЗАНОВО ---
@dp.message(BotState.accent_color)
async def process_accent_color(message: Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")
    accent = message.text.strip()
    
    if not accent.startswith("#") or len(accent) != 7:
        await message.answer(TEXTS[lang]["wrong_format"])
        return
        
    bg = user_data['bg_color']
    text = user_data['text_color']
    
    # Сохраняем язык, но очищаем цвета для новой темы
    await state.update_data(bg_color=None, text_color=None, accent_color=None)
    
    bg_clean = bg.replace("#", "")
    text_clean = text.replace("#", "")
    accent_clean = accent.replace("#", "")
    
    theme_url = f"https://t.me{bg_clean}&text={text_clean}&accent={accent_clean}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["btn_install"], url=theme_url)],
        [InlineKeyboardButton(text=TEXTS[lang]["btn_create"], callback_data="start_create_theme")]
    ])
    
    response_text = TEXTS[lang]["success"].format(bg=bg, text=text, accent=accent)
    await message.answer(response_text, reply_markup=kb)

# --- ЗАПУСК БОТА ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
