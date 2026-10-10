from __future__ import annotations

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest


async def publish_to_channel(
    bot: Bot,
    channel_id: str,
    text: str,
    *,
    parse_mode: ParseMode | None = None,
) -> int:
    """Публикует текст в канал. Возвращает message_id."""
    try:
        message = await bot.send_message(
            chat_id=channel_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=True,
        )
    except TelegramBadRequest as exc:
        # Если пользователь случайно добавил Markdown — повторяем plain text
        if parse_mode is not None:
            message = await bot.send_message(
                chat_id=channel_id,
                text=text,
                disable_web_page_preview=True,
            )
        else:
            raise RuntimeError(f"Не удалось отправить в канал: {exc}") from exc
    return message.message_id
