from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from .config import Settings
from .generator import PostGenerator


class InjectMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings, generator: PostGenerator) -> None:
        self.settings = settings
        self.generator = generator

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["settings"] = self.settings
        data["generator"] = self.generator
        return await handler(event, data)
