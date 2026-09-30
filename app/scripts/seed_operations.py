"""
Скрипт заполнения базы данных категориями и подоперациями.

Создаёт 8 категорий с подоперациями согласно ТЗ:
  • Обметать бурлет       (Финтек, ППУ, Ручная обметка) — метры
  • Резка буклетов        (Массовка КН, Единичные КН, Массовка Grassi, Единичные Grassi, Ручная резка) — количество
  • Бурлет без рисунка    (Финтек, ППУ) — количество
  • Бурлет с рисунком 229 (От 19 до 24 высоты, От 25 до 30 высоты, ППУ+Финтек) — метры
  • Бурлет с декором      (3D сетка, Лента, 3D сетка и лента) — метры
  • Ручки                 (Заготовка ручек, Пришив ручек) — количество
  • Нарезка роликов       (Ткань, Спонбонд) — количество
  • Ручная разметка ручек (Разметка ручек) — количество

Цены по умолчанию = 0 — их задаёт администратор в админ-панели.

Запуск:
    poetry run python -m app.scripts.seed_operations
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import OperationCategory, SubOperation
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Структура данных: категория → список подопераций
OPERATIONS_DATA = [
    {
        "name": "Обметать бурлет",
        "description": "Обметка бурлета различными способами",
        "suboperations": [
            {"name": "Финтек",        "unit": "метр", "price": 0.0},
            {"name": "ППУ",           "unit": "метр", "price": 0.0},
            {"name": "Ручная обметка", "unit": "метр", "price": 0.0},
        ],
    },
    {
        "name": "Резка буклетов",
        "description": "Резка буклетов различными способами",
        "suboperations": [
            {"name": "Массовка КН",      "unit": "количество", "price": 0.0},
            {"name": "Единичные КН",     "unit": "количество", "price": 0.0},
            {"name": "Массовка Grassi",  "unit": "количество", "price": 0.0},
            {"name": "Единичные Grassi", "unit": "количество", "price": 0.0},
            {"name": "Ручная резка",     "unit": "количество", "price": 0.0},
        ],
    },
    {
        "name": "Бурлет без рисунка",
        "description": "Бурлет без рисунка",
        "suboperations": [
            {"name": "Финтек", "unit": "количество", "price": 0.0},
            {"name": "ППУ",    "unit": "количество", "price": 0.0},
        ],
    },
    {
        "name": "Бурлет с рисунком 229",
        "description": "Бурлет с рисунком 229",
        "suboperations": [
            {"name": "От 19 до 24 высоты", "unit": "метр", "price": 0.0},
            {"name": "От 25 до 30 высоты", "unit": "метр", "price": 0.0},
            {"name": "ППУ+Финтек",         "unit": "метр", "price": 0.0},
        ],
    },
    {
        "name": "Бурлет с декором",
        "description": "Бурлет с декором",
        "suboperations": [
            {"name": "3D сетка",         "unit": "метр", "price": 0.0},
            {"name": "Лента",            "unit": "метр", "price": 0.0},
            {"name": "3D сетка и лента", "unit": "метр", "price": 0.0},
        ],
    },
    {
        "name": "Ручки",
        "description": "Изготовление и пришив ручек",
        "suboperations": [
            {"name": "Заготовка ручек", "unit": "количество", "price": 0.0},
            {"name": "Пришив ручек",    "unit": "количество", "price": 0.0},
        ],
    },
    {
        "name": "Нарезка роликов",
        "description": "Нарезка роликов",
        "suboperations": [
            {"name": "Ткань",    "unit": "количество", "price": 0.0},
            {"name": "Спонбонд", "unit": "количество", "price": 0.0},
        ],
    },
    {
        "name": "Ручная разметка ручек",
        "description": "Ручная разметка ручек",
        "suboperations": [
            {"name": "Разметка ручек", "unit": "количество", "price": 0.0},
        ],
    },
]


async def seed_operations(force: bool = False) -> None:
    """
    Заполняет БД категориями и подоперациями.

    :param force: если True — удалит существующие категории перед заполнением.
    """
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже данные
        result = await session.execute(select(OperationCategory))
        existing = result.scalars().all()

        if existing and not force:
            logger.info(
                f"ℹ️ В базе уже есть {len(existing)} категорий. "
                f"Пропускаю заполнение (используйте force=True для перезаписи)."
            )
            return

        if existing and force:
            logger.warning("⚠️ Удаляю существующие категории (force=True)...")
            for cat in existing:
                await session.delete(cat)
            await session.commit()

        logger.info("🌱 Заполнение операций и подопераций...")

        total_categories = 0
        total_subops = 0

        for op_data in OPERATIONS_DATA:
            category = OperationCategory(
                name=op_data["name"],
                description=op_data.get("description", ""),
                is_active=True,
            )
            session.add(category)
            await session.flush()  # чтобы получить category.id

            for sub_data in op_data["suboperations"]:
                subop = SubOperation(
                    category_id=category.id,
                    name=sub_data["name"],
                    unit=sub_data["unit"],
                    price=sub_data["price"],
                    is_active=True,
                )
                session.add(subop)
                total_subops += 1

            total_categories += 1
            logger.info(
                f"  ✅ {op_data['name']} — "
                f"{len(op_data['suboperations'])} подопераций"
            )

        await session.commit()

        logger.info("─" * 50)
        logger.info(f"🎉 Готово! Добавлено категорий: {total_categories}")
        logger.info(f"🎉 Готово! Добавлено подопераций: {total_subops}")
        logger.info("─" * 50)
        logger.info("👉 Теперь задайте цены через /start → ⚙️ Админ панель")


async def main() -> None:
    """
    Точка входа.

    Примеры:
        poetry run python -m app.scripts.seed_operations
        poetry run python -m app.scripts.seed_operations --force
    """
    force = "--force" in sys.argv
    try:
        await seed_operations(force=force)
    except Exception as e:
        logger.error(f"❌ Ошибка при заполнении БД: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())