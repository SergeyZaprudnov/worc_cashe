"""
Скрипт инициализации базы данных.
Создаёт все таблицы на основе моделей SQLAlchemy.

Запуск:
    poetry run python -m app.scripts.init_db
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH (на случай запуска вне Poetry)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database import init_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Точка входа: создаём все таблицы в БД."""
    logger.info("🚀 Инициализация базы данных...")
    try:
        await init_db()
        logger.info("✅ Таблицы успешно созданы!")
    except Exception as e:
        logger.error(f"❌ Ошибка при создании таблиц: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())