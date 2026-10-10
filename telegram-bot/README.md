# Telegram-бот: голос Андрея Анатольевича

Генерирует и публикует посты в Telegram-канал в стиле Андрея Краснокуцкого (ATON+, Алматы), используя reusable skill из папки `skill/`.

Пользовательский deliverable скилла также лежит в Project store:  
`/cursor/stores/self/docs/andrey-style-skill/`.

## Что нужно от пользователя

1. **BOT_TOKEN** — токен у [@BotFather](https://t.me/BotFather)
2. **CHANNEL_ID** — `@username` канала или числовой id (`-100…`)
3. Бот добавлен в канал как **администратор** с правом публиковать сообщения
4. **OPENAI_API_KEY** — ключ OpenAI (или совместимого API через `OPENAI_BASE_URL`)
5. **ADMIN_IDS** — ваш Telegram user id (команда `/whoami` в боте; без списка доступ открыт всем — только для тестов)

## Быстрый старт

```bash
cd telegram-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполните .env
python -m src.bot
# или: python -m telegram-bot  (из /workspace, если пакет на PYTHONPATH)
```

Из корня репозитория:

```bash
cd /workspace/telegram-bot && python -m src.bot
```

## Команды бота

| Команда | Действие |
|---------|----------|
| `/post <тема>` | Черновик поста |
| `/post --genre opinion\|shopfloor\|answer\|note --length short\|medium\|long <тема>` | С жанром/длиной |
| Кнопка «Опубликовать» | Отправка черновика в канал |
| `/publish` | Опубликовать последний черновик |
| `/whoami` | Узнать свой Telegram id |

`POST_MODE=publish` — сразу публиковать после `/post` (без кнопки). По умолчанию `draft`.

## Структура

```
telegram-bot/
  skill/           # SKILL.md + persona / voice / examples
  src/
    bot.py         # entrypoint polling
    config.py      # env
    generator.py   # LLM + skill prompt
    handlers.py    # команды
    publisher.py   # send to channel
  .env.example
  requirements.txt
```

## Замечания

- Скилл задаёт голос и позиции; модель **не должна** копировать чужие интервью дословно.
- Черновики хранятся в памяти процесса (после рестарта пропадут).
- Для самохостинга подойдёт любой VPS/`systemd`; webhook не обязателен.
