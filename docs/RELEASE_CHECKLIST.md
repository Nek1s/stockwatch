# Release checklist

Этот список используется перед созданием первого публичного GitHub Release.
Он не заменяет code review и не хранит секреты.

## Качество кода

- [ ] `ruff format --check .`
- [ ] `ruff check .`
- [ ] `mypy app`
- [ ] `pytest`
- [ ] GitHub Actions для PR и `main` завершились успешно.

## Данные и API

- [ ] `alembic upgrade head --sql` генерируется без ошибок.
- [ ] На чистой локальной базе применена `alembic upgrade head`.
- [ ] Проверены `/health`, `/docs` и защищённые сценарии API.
- [ ] CHANGELOG содержит заметку о релизе.

## Локальная инфраструктура

- [ ] На машине с Docker выполнены `docker compose up --build` и проверка
  `docker compose ps`.
- [ ] Открыты `http://localhost:8000/metrics`, Prometheus и Grafana.
- [ ] Dashboard `StockWatch Overview` показывает HTTP- и worker-метрики.
- [ ] В `.env` нет значений, предназначенных для публикации; `.env.example`
  содержит только имена настроек и безопасные примеры.

## Telegram и источники цен

- [ ] `TELEGRAM_BOT_TOKEN` задан только в локальном `.env` или секретах среды.
- [ ] Пользователь сохранил Telegram chat ID через `PUT /api/v1/notifications/telegram`.
- [ ] Ручной тест подтверждает одно уведомление при пересечении целевой цены.
- [ ] Источник цены использует публичный согласованный контракт и покрыт тестами.

## Публикация

- [ ] Создана версия в `CHANGELOG.md` и Git-тег SemVer.
- [ ] Создан GitHub Release с кратким описанием изменений.
- [ ] Проверены README, архитектура, лицензия и ссылки на документацию.
