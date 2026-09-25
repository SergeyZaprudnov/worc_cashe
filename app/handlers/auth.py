from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import User
from app.keyboards.inline import get_main_keyboard
from app.config import settings
import logging


logger = logging.getLogger(__name__)

FULL_NAME, PHONE = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    logger.info(f"User {user_id} start the bot")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()

        is_admin = user_id in settings.ADMIN_IDS

        if user and user.is_autorized:
            if is_admin and not user.is_admin:
                user.is_admin = True
                await session.commit()
            await update.message.reply_text(f"👋 Добро пожаловать, {user.first_name}!",
                                            reply_markup=get_main_keyboard(user.is_admin))
            return ConversationHandler.END

        if not user:
            user = User(telegram_id = user_id, is_admin = is_admin)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif is_admin and not user.is_admin:
            user.is_admin = True
            await session.commit()

        context.user_data["user_id"] = user.id

    await update.message.reply_text("🔐 Для авторизации введите ваше ФИО:")
    return FULL_NAME

async def full_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    full_name = update.message.text.strip()
    if len(full_name) < 3:
        await update.message.replay_text("❌ ФИО минимум 3 символа. Попробуйте снова:")
        return FULL_NAME
    context.user_data["full_name"] = full_name
    await update.message.reply_text("📱 Введите ваш номер телефона:")
    return PHONE

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text.strip()
    full_name = context.user_data["full_name"]
    telegram_id = update.effective_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            await update.message.reply_text("❌ Пользователь не найден")
            return ConversationHandler.END

        user.full_name = full_name
        user.phone = phone
        user.is_autorized = True
        await session.commit()
        await session.refresh(user)

    await update.message.reply_text(f"✅ Авторизация успешна!\nДобро пожаловать, {full_name}!",
                                    reply_markup=get_main_keyboard(user.is_admin))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Действие отменено. Введите /start")
    return ConversationHandler.END