# Примеры API

Все примеры предполагают, что API запущен по `http://localhost:8000`.

## Регистрация и вход

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"correct-horse-battery-staple"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"correct-horse-battery-staple"}'
```

Сохраните `access_token` из ответа в переменную окружения `ACCESS_TOKEN`.

## Создание отслеживания

```bash
curl -X POST http://localhost:8000/api/v1/watches \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name":"Mechanical keyboard",
    "product_url":"https://shop.example.com/keyboard",
    "target_price":"99.99",
    "currency":"USD"
  }'
```

Сохраните идентификатор из ответа в `WATCH_ID`.

## История и статистика

```bash
curl "http://localhost:8000/api/v1/watches/$WATCH_ID/prices?limit=20" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

curl "http://localhost:8000/api/v1/watches/$WATCH_ID/prices/statistics" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Настройка Telegram

```bash
curl -X PUT http://localhost:8000/api/v1/notifications/telegram \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"telegram_chat_id":"123456789"}'
```

Для реальной доставки требуется `TELEGRAM_BOT_TOKEN` в локальном `.env` и
разрешённый адаптер источника цен. Токен никогда не передаётся этому API.
