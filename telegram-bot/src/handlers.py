from __future__ import annotations

import logging
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from .config import Settings
from .generator import PostGenerator
from .publisher import publish_to_channel

logger = logging.getLogger(__name__)

router = Router(name="andrey-bot")

# Черновики в памяти процесса: draft_id -> text
_DRAFTS: dict[str, str] = {}
_DRAFT_SEQ = 0


def _next_draft_id() -> str:
    global _DRAFT_SEQ
    _DRAFT_SEQ += 1
    return str(_DRAFT_SEQ)


def _is_admin(user_id: int | None, settings: Settings) -> bool:
    if user_id is None:
        return False
    if not settings.admin_ids:
        return True
    return user_id in settings.admin_ids


def _draft_keyboard(draft_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Опубликовать в канал",
                    callback_data=f"publish:{draft_id}",
                ),
                InlineKeyboardButton(
                    text="Отменить",
                    callback_data=f"discard:{draft_id}",
                ),
            ]
        ]
    )


def _parse_flags(args: str) -> tuple[str, dict[str, str]]:
    """Разбирает флаги вида --genre opinion --length short тема..."""
    tokens = args.split()
    flags: dict[str, str] = {}
    rest: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("--") and i + 1 < len(tokens):
            key = token[2:].strip().lower()
            flags[key] = tokens[i + 1]
            i += 2
            continue
        rest.append(token)
        i += 1
    return " ".join(rest).strip(), flags


@router.message(Command("start", "help"))
async def cmd_help(message: Message, settings: Settings) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None, settings):
        await message.answer("Нет доступа. Добавьте свой Telegram id в ADMIN_IDS.")
        return

    text = (
        "Бот канала в голосе Андрея Анатольевича (ATON+).\n\n"
        "Команды:\n"
        "/post <тема> — сгенерировать пост\n"
        "/post --genre opinion|shopfloor|answer|note --length short|medium|long <тема>\n"
        "/publish — опубликовать последний черновик в канал\n"
        "/whoami — показать ваш Telegram id\n"
        "/help — эта справка\n\n"
        f"Канал: {settings.channel_id}\n"
        f"Режим: {settings.post_mode}\n"
        f"Модель: {settings.openai_model}"
    )
    await message.answer(text)


@router.message(Command("whoami"))
async def cmd_whoami(message: Message) -> None:
    user = message.from_user
    if user is None:
        await message.answer("Не вижу пользователя.")
        return
    await message.answer(f"Ваш Telegram id: `{user.id}`", parse_mode="Markdown")


@router.message(Command("post"))
async def cmd_post(
    message: Message,
    command: CommandObject,
    settings: Settings,
    generator: PostGenerator,
) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None, settings):
        await message.answer("Нет доступа.")
        return

    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "Укажите тему.\nПример: /post почему лучше вложить в станок, чем в пафос"
        )
        return

    topic, flags = _parse_flags(raw)
    if not topic:
        await message.answer("После флагов нужна тема поста.")
        return

    status = await message.answer("Пишу черновик в голосе Андрея Анатольевича…")
    try:
        text = await generator.generate(
            topic,
            genre=flags.get("genre", "auto"),
            length=flags.get("length"),
            extra=flags.get("extra"),
        )
    except Exception as exc:  # noqa: BLE001 — отдаём причину админу
        logger.exception("generation failed")
        await status.edit_text(f"Ошибка генерации: {exc}")
        return

    if settings.post_mode == "publish":
        try:
            msg_id = await publish_to_channel(message.bot, settings.channel_id, text)
        except Exception as exc:  # noqa: BLE001
            logger.exception("publish failed")
            await status.edit_text(f"Сгенерировано, но публикация не удалась: {exc}\n\n{text}")
            return
        await status.edit_text(f"Опубликовано в канал (message_id={msg_id}).\n\n{text}")
        return

    draft_id = _next_draft_id()
    _DRAFTS[draft_id] = text
    # последний черновик для /publish без id
    _DRAFTS["last"] = text
    await status.edit_text(
        f"Черновик #{draft_id}:\n\n{text}",
        reply_markup=_draft_keyboard(draft_id),
    )


@router.message(Command("publish"))
async def cmd_publish(message: Message, settings: Settings) -> None:
    if not _is_admin(message.from_user.id if message.from_user else None, settings):
        await message.answer("Нет доступа.")
        return

    text = _DRAFTS.get("last")
    if not text:
        await message.answer("Нет черновика. Сначала /post <тема>.")
        return

    try:
        msg_id = await publish_to_channel(message.bot, settings.channel_id, text)
    except Exception as exc:  # noqa: BLE001
        logger.exception("publish failed")
        await message.answer(f"Публикация не удалась: {exc}")
        return

    await message.answer(f"Опубликовано (message_id={msg_id}).")


@router.callback_query(F.data.startswith("publish:"))
async def cb_publish(callback: CallbackQuery, settings: Settings) -> None:
    if not _is_admin(callback.from_user.id if callback.from_user else None, settings):
        await callback.answer("Нет доступа", show_alert=True)
        return

    draft_id = (callback.data or "").split(":", 1)[-1]
    text = _DRAFTS.get(draft_id)
    if not text:
        await callback.answer("Черновик уже недоступен", show_alert=True)
        return

    try:
        msg_id = await publish_to_channel(callback.bot, settings.channel_id, text)
    except Exception as exc:  # noqa: BLE001
        logger.exception("publish failed")
        await callback.answer(f"Ошибка: {exc}", show_alert=True)
        return

    _DRAFTS.pop(draft_id, None)
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(f"Опубликовано в канал (message_id={msg_id}).")
    await callback.answer("Готово")


@router.callback_query(F.data.startswith("discard:"))
async def cb_discard(callback: CallbackQuery, settings: Settings) -> None:
    if not _is_admin(callback.from_user.id if callback.from_user else None, settings):
        await callback.answer("Нет доступа", show_alert=True)
        return

    draft_id = (callback.data or "").split(":", 1)[-1]
    _DRAFTS.pop(draft_id, None)
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(f"Черновик #{draft_id} отменён.")
    await callback.answer("Отменено")
