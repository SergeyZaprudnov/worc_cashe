from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List


def get_main_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="statistics")],
        [InlineKeyboardButton("💰 Заработано", callback_data="earned")],
        [InlineKeyboardButton("📈 Статистика за сегодня", callback_data="daily_stats")],
        [InlineKeyboardButton("▶️ Начало работы", callback_data="start_work")],
        [InlineKeyboardButton("⏹ Конец работы", callback_data="end_work")],
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("⚙️ Админ панель", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)


def get_categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f"📂 {c.name}", callback_data=f"cat_{c.id}")]
        for c in categories
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)


def get_suboperations_keyboard(suboperations, show_price: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    for s in suboperations:
        if show_price:
            unit = "м" if s.unit == "метр" else "шт"
            text = f"✏️ {s.name} ({s.price:.2f}₽/{unit})"
        else:
            text = f"• {s.name}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"sub_{s.id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]])


def get_back_to_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]])


def get_work_summary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Статистика за сегодня", callback_data="daily_stats")],
        [InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_main")],
    ])


def get_admin_categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f"📂 {c.name}", callback_data=f"admin_cat_{c.id}")]
        for c in categories
    ]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)


def get_admin_suboperations_keyboard(category_id: int, suboperations) -> InlineKeyboardMarkup:
    keyboard = []
    for s in suboperations:
        unit = "м" if s.unit == "метр" else "шт"
        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {s.name} ({s.price:.2f}₽/{unit})",
                callback_data=f"admin_sub_{s.id}",
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin_categories")])
    return InlineKeyboardMarkup(keyboard)


def get_admin_suboperation_detail_keyboard(subop_id: int, category_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Изменить название", callback_data=f"edit_name_{subop_id}")],
        [InlineKeyboardButton("💰 Изменить цену", callback_data=f"edit_price_{subop_id}")],
        [InlineKeyboardButton("📏 Изменить единицу", callback_data=f"edit_unit_{subop_id}")],
        [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_sub_{subop_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"admin_cat_{category_id}")],
    ])


def get_confirmation_keyboard(yes_data: str, no_data: str = "back_to_admin_categories") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Да", callback_data=yes_data),
            InlineKeyboardButton("❌ Нет", callback_data=no_data),
        ]
    ])