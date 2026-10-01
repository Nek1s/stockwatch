# StockWatch

StockWatch — API-сервис мониторинга цен товаров. Пользователь добавляет товар и целевую цену, а сервис регулярно проверяет цену, сохраняет историю и уведомляет о снижении.

## MVP

- регистрация и аутентификация пользователей;
- товары, отслеживания и целевые цены;
- фоновая проверка цен через Celery и Redis;
- история цен и события изменения;
- уведомления в Telegram;
- OpenAPI-документация FastAPI.

## Планируемый стек

Python 3.13, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, Celery, Docker Compose, pytest, Ruff, mypy и GitHub Actions.

Подробный план — в [ROADMAP.md](ROADMAP.md), текущая стадия — в [PROJECT_STATE.md](PROJECT_STATE.md).

## Статус

Проект находится на этапе инициализации.
