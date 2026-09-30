.PHONY: help install run init-db seed reset-db clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'

install: ## Установка зависимостей
	poetry install --with dev

run: ## Запуск бота
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

init-db: ## Создать таблицы в БД
	poetry run python -m app.scripts.init_db

seed: ## Заполнить категории и подоперации
	poetry run python -m app.scripts.seed_operations

seed-force: ## Заполнить заново (удалить старые категории)
	poetry run python -m app.scripts.seed_operations --force

reset-db: ## Полный сброс БД (удалить файл + создать + заполнить)
	rm -f telegram_bot.db
	poetry run python -m app.scripts.init_db
	poetry run python -m app.scripts.seed_operations
	@echo "✅ База данных пересоздана"

clean: ## Очистка кэша
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage