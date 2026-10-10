# StockWatch

[![CI](https://github.com/Nek1s/stockwatch/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Nek1s/stockwatch/actions/workflows/ci.yml)

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

Docker Compose также запускает Celery worker и Celery Beat. Каждые пять минут Beat
ставит в очередь активные отслеживания. Сейчас источник цен намеренно является
безопасной заглушкой: он не обращается к закрытым или недокументированным API
магазинов. Новый источник должен реализовать интерфейс `PriceSource` и работать
только с согласованным публичным источником данных.

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

## История цен

История снимков отслеживания доступна владельцу через
`GET /api/v1/watches/{watch_id}/prices`. Базовая статистика доступна по
`GET /api/v1/watches/{watch_id}/prices/statistics` и содержит последнюю,
минимальную и максимальную цену.

## Telegram-уведомления

После достижения целевой цены StockWatch отправляет одно уведомление при
пересечении порога. Повторные проверки, пока цена остаётся ниже цели, сообщения
не дублируют. Чтобы включить доставку в self-hosted окружении:

1. Добавьте токен созданного у `@BotFather` бота только в локальный `.env`:
   `TELEGRAM_BOT_TOKEN=...`. Не передавайте его в API, чат или Git.
2. Напишите боту `/start` и узнайте идентификатор личного чата через
   проверенный инструмент Telegram, которому доверяете.
3. Сохраните ID через защищённый endpoint:

```bash
curl -X PUT http://localhost:8000/api/v1/notifications/telegram \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"telegram_chat_id":"123456789"}'
```

Новый endpoint доступен и в OpenAPI UI. После изменения `.env` перезапустите
`worker` и `beat`.

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

Для запуска фоновых процессов без Docker используйте два отдельных терминала:

```bash
celery -A app.worker:celery_app worker --loglevel=INFO
celery -A app.worker:celery_app beat --loglevel=INFO
```

## Документация

- [Roadmap](ROADMAP.md)
- [Текущее состояние](PROJECT_STATE.md)
- [Backlog issues](docs/ISSUES.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Примеры API](docs/API_EXAMPLES.md)
- [ADR 001: источники цен](docs/ADR/001-approved-price-sources.md)
- [Наблюдаемость](docs/OBSERVABILITY.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Changelog](CHANGELOG.md)

## Лицензия

Проект распространяется по лицензии [MIT](LICENSE).
