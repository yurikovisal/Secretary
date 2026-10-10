from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from .config import get_settings
from .generator import PostGenerator
from .handlers import router
from .middleware import InjectMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("andrey-bot")


async def run() -> None:
    settings = get_settings()
    generator = PostGenerator(settings)
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    inject = InjectMiddleware(settings, generator)
    dp.message.middleware(inject)
    dp.callback_query.middleware(inject)
    dp.include_router(router)

    me = await bot.get_me()
    logger.info(
        "Bot @%s started. Channel=%s mode=%s skill=%s",
        me.username,
        settings.channel_id,
        settings.post_mode,
        settings.skill_path,
    )
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
