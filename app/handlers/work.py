from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import OperationCategory, SubOperation
from app.keyboards.inline import (
    get_categories_keyboard,
    get_suboperations_keyboard,
    get_back_keyboard,
)
from app.utils.helpers import validate_quantity
import logging

logger = logging.getLogger(__name__)

SELECT_CATEGORY, SELECT_SUBOPERATION, ENTER_QUANTITY, ENTER_ORDER, ENTER_DATE = range(5)


async def start_work(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    async with AsyncSessionLocal() as session:
        r = await session.execute(
            select(OperationCategory).where(OperationCategory.is_active == True)  # noqa: E712
        )
        categories = r.scalars().all()

        if not categories:
            await query.edit_message_text(
                "❌ Нет доступных операций. Обратитесь к администратору.",
                reply_markup=get_back_keyboard(),
            )
            return ConversationHandler.END

        await query.edit_message_text(
            "📋 Выберите категорию работы:",
            reply_markup=get_categories_keyboard(categories),
        )
        return SELECT_CATEGORY


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    category_id = int(query.data.split("_")[1])
    context.user_data["category_id"] = category_id

    async with AsyncSessionLocal() as session:
        r = await session.execute(
            select(SubOperation).where(
                SubOperation.category_id == category_id,
                SubOperation.is_active == True,  # noqa: E712
            )
        )
        subs = r.scalars().all()
        category = await session.get(OperationCategory, category_id)

        if not subs:
            await query.edit_message_text(
                "❌ В этой категории нет подопераций",
                reply_markup=get_back_keyboard(),
            )
            return ConversationHandler.END

        # СОТРУДНИКУ ЦЕНУ НЕ ПОКАЗЫВАЕМ
        await query.edit_message_text(
            f"📂 {category.name}\n\nВыберите подоперацию:",
            reply_markup=get_suboperations_keyboard(subs, show_price=False),
        )
        return SELECT_SUBOPERATION


async def select_suboperation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    sub_id = int(query.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        sub = await session.get(SubOperation, sub_id)
        if not sub:
            await query.edit_message_text("❌ Подоперация не найдена")
            return ConversationHandler.END

        context.user_data["suboperation_id"] = sub_id
        unit_text = "метров" if sub.unit == "метр" else "штук"

        # СОТРУДНИК НЕ ВИДИТ ЦЕНУ
        await query.edit_message_text(
            f"📌 {sub.name}\n"
            f"📂 {sub.category.name}\n"
            f"📏 Единица: {unit_text}\n\n"
            f"Введите {unit_text}:"
        )
        return ENTER_QUANTITY


async def enter_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        q = validate_quantity(update.message.text)
        context.user_data["quantity"] = q
        await update.message.reply_text("📋 Введите номер заявки:")
        return ENTER_ORDER
    except ValueError as e:
        await update.message.reply_text(f"❌ {e}\nВведите корректное число:")
        return ENTER_QUANTITY


async def enter_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    order = update.message.text.strip()