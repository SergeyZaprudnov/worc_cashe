from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from datetime import date, timedelta
from app. database import AsyncSessionLocal
from app.models import User, UserOperation, WorkSession
from app.keyboards.inline import get_back_keyboard
from app.utils.helpers import calculate_total, format_currency
import logging


logger = logging.getLogger(__name__)

async def _get_user(session, telegram_id):
    r = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return r.scalar_one_or_none()

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id

    async with AsyncSessionLocal() as session:
        user = await _get_user(session, telegram_id)
        if not user:
            await query.edit_message_text("❌ Пользователь не найден")
            return

        r = await session.execute(
            select(UserOperation)
            .where(UserOperation.user_id == user.id)
            .order_by(UserOperation.created_at.desc())
        )
        operations = r.scalar().all()

        if not operations:
            text = "📊 У вас пока нет выполненных операций"
        else:
            text = "📊 ВСЯ СТАТИСТИКА\n" + "═" * 30 + "\n\n"
            stats = {}
            total_quantity = 0
            total_earned = 0.0

            for op in operations:
                cat  = op.category.name if op.category else "_"
                sub = op.suboperation.name if op.suboperation else "_"
                unit = op.suboperation.unit if op.suboperation else ""
                key = (cat, sub, unit)
                if key not in stats:
                    stats[key] = {"quantyti": 0.0, "total": 0.0, "count": 0}
                stats[key]["quantyti"] += op.quantity
                stats[key]["total"] += op.quantity
                stats[key]["count"] += 1
                total_quantity += op.quantity
                total_earned += op.total_price

                current_cat = None
                for (cat, sub, unit), d in stats.items():
                    if current_cat != cat:
                        current_cat = cat
                        text += f"\n📂 {cat}:\n"
                    u = "м" if unit == "метр" else "шт"
                    text += f" • {sub}:\n"
                    text += f"   КоличествоЖ {d['quantity']:.2f} {u}\n"
                    text += f"   Операций: {d['count']}\n"

                text += "\n" + "═" * 30 + "\n📊 ИТОГО:\n"
                text += f"   • Общее количество: {total_quantity:.2f}\n"

            await query.edit_message_text(text, reply_markup=get_back_keyboard())

async def earned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Заработано - только для администраторов"""
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id

    async with AsyncSessionLocal() as session:
        user = await _get_user(session, telegram_id)
        if not user:
            await query.edit_message_text("❌ Пользователь не найден")
            return

        if not user.is_admin:
            await query.edit_message_text("⛔ Раздел «Заработано» доступен только администраторам",
                                          reply_markup=get_back_keyboard()
                                          )
            return

        r = await session.execute(
            select(UserOperation)
            .where(UserOperation.user_id == user.id)
            .order_by(UserOperation.created_at.desc())
        )
        operations = r.scalar().all()
        total = calculate_total(operations)

        text = f"💰 ВСЕГО ЗАРАБОТАНО: {format_currency(total)}\n" + "═" * 30 + "\n\n"

        if operations:
            cat_stats = {}
            for op in operations:
                cat = op.category.name if op.category else "_"
                cat_stats.setdefault(cat, {"total": 0.0, "count": 0})
                cat_stats[cat]["total"] += op.total_price
                cat_stats[cat]["count"] += 1

            text += "📋 ПО КАТЕГОРИЯМ:\n\n"
            for cat, d in cat_stats.items():
                text += f"📂 {cat}:\n"
                text += F"   • Сумма: {format_currency(d['total'])}\n"
                text += f"   • Операций: {d['count']}\n\n"

            today = date.today()
            first_day = date(today.year, today.month, 1)
            month_total = calculate_total([o for o in operations if o.execution_date >= first_day])
            week_ago = today - timedelta(days=7)
            week_total = calculate_total([o for o in operations if o.execution_date >= week_ago])
            today_total = calculate_total([o for o in operations if o.execution_date == today])

            text += "═" * 30 + "\n📅 ПО ПЕРИОДАМ:\n"
            text += f"• За сегодня: {format_currency(today_total)}\n"
            text += f"• За неделю:  {format_currency(week_total)}\n"
            text += f"• За месяц:   {format_currency(month_total)}\n"
        else:
            text += "❌ Нет выполненных операций"

        await query.edit_message_text(text, reply_markup=get_back_keyboard())


async def daily_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Статистика за сегодня. Суммы видят только админы."""
    query = update.callback_query
    await query.answer()
    telegram_id = update.effective_user.id
    today = date.today()

    async with AsyncSessionLocal() as session:
        user = await _get_user(session, telegram_id)
        if not user:
            await query.edit_message_text("❌ Пользователь не найден")
            return

        r = await session.execute(
            select(UserOperation)
            .where(
                UserOperation.user_id == user.id,
                UserOperation.execution_date == today,
            )
            .order_by(UserOperation.created_at)
        )
        today_ops = r.scalars().all()

        r = await session.execute(
            select(WorkSession).where(
                WorkSession.user_id == user.id,
                WorkSession.is_active == True,  # noqa: E712
            )
        )
        active_session = r.scalar_one_or_none()

        text = f"📊 СТАТИСТИКА ЗА СЕГОДНЯ\n📅 {today.strftime('%d.%m.%Y')}\n" + "═" * 30 + "\n\n"

        if today_ops:
            stats = {}
            total_quantity = 0
            total_earned = 0.0
            for op in today_ops:
                cat = op.category.name if op.category else "—"
                sub = op.suboperation.name if op.suboperation else "—"
                unit = op.suboperation.unit if op.suboperation else ""
                key = (cat, sub, unit)
                stats.setdefault(key, {"quantity": 0.0, "total": 0.0, "count": 0})
                stats[key]["quantity"] += op.quantity
                stats[key]["total"] += op.total_price
                stats[key]["count"] += 1
                total_quantity += op.quantity
                total_earned += op.total_price

            current_cat = None
            for (cat, sub, unit), d in stats.items():
                if current_cat != cat:
                    current_cat = cat
                    text += f"\n📂 {cat}:\n"
                u = "м" if unit == "метр" else "шт"
                text += f"   • {sub}:\n"
                text += f"     Количество: {d['quantity']:.2f} {u}\n"
                if user.is_admin:
                    text += f"     Сумма: {format_currency(d['total'])}\n"

            text += "\n" + "═" * 30 + f"\n📊 ИТОГО за день:\n"
            text += f"   • Общее количество: {total_quantity:.2f}\n"
            if user.is_admin:
                text += f"   • Заработано: {format_currency(total_earned)}\n"
        else:
            text += "❌ Нет выполненных операций за сегодня\n"

        if active_session:
            text += "\n" + "═" * 30
            text += f"\n▶️ Смена активна (с {active_session.start_time.strftime('%H:%M')})"

        await query.edit_message_text(text, reply_markup=get_back_keyboard())
