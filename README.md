# StockWatch

StockWatch — API-сервис мониторинга цен товаров. Пользователь добавляет товар и целевую цену, а сервис регулярно проверяет цену, сохраняет историю и уведомляет о снижении.

## MVP

- регистрация и аутентификация пользователей;
- товары, отслеживания и целевые цены;
- фоновые проверки цен через Celery и Redis;
- история цен и события изменения;
- уведомления в Telegram;
- документированный REST API.

## Технологии

Python 3.12+, FastAPI, Pydantic Settings, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, Celery, Docker Compose, pytest, Ruff, mypy и GitHub Actions.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

После запуска доступны:

- API: `http://localhost:8000`;
- liveness probe: `GET /health`;
- OpenAPI UI: `http://localhost:8000/docs`.

Для локальной разработки без Docker:

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Проверки качества:

```bash
ruff check .
ruff format --check .
mypy app
pytest
```

## Документация

- [Roadmap](ROADMAP.md)
- [Текущее состояние](PROJECT_STATE.md)
- [Backlog issues](docs/ISSUES.md)
- [Changelog](CHANGELOG.md)

## Лицензия

Проект распространяется по лицензии [MIT](LICENSE).
