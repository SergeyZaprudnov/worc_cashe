.PHONY: help install run init-db seed clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {print "%-20s %s\n", $$1, $$2}'

install: # Установка зависимостей
	poetry install --with dev

run: # Запуск бота
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

init-db: # Инициализация БД
	poetry run python -m app.scripts.init_db

seed: # Заполнить операции
	poetry run python -m app.scripts.seed_operations

clean: # Очистка кэша
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
