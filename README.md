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

Перед первым запуском API примените миграции:

```bash
docker compose exec api alembic upgrade head
```

## Аутентификация

Регистрация создаёт пользователя, а вход возвращает пару access/refresh JWT. Пароль должен содержать не менее 12 символов.

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"correct-horse-battery-staple"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"correct-horse-battery-staple"}'
```

Для приватного endpoint передайте access token:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Отслеживания цен

Создайте отслеживание товара с целевой ценой. Список поддерживает пагинацию через
`limit` (1–100) и `offset`, а также фильтр `is_active`.

```bash
curl -X POST http://localhost:8000/api/v1/watches \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name":"Mechanical keyboard",
    "product_url":"https://shop.example.com/keyboard",
    "target_price":"99.99",
    "currency":"USD"
  }'
```

Доступны `GET /api/v1/watches`, `GET/PATCH/DELETE /api/v1/watches/{watch_id}`.
Отслеживания изолированы: пользователь не может читать или менять данные другого пользователя.

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
