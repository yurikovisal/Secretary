from __future__ import annotations

from openai import AsyncOpenAI

from .config import Settings
from .skill_loader import load_skill_prompt

LENGTH_HINTS = {
    "short": "Короткий пост: 400–700 знаков.",
    "medium": "Средний пост: 700–1200 знаков.",
    "long": "Развёрнутый пост: 1200–1800 знаков, без воды.",
}

GENRE_HINTS = {
    "opinion": "Жанр: мнение / позиция по теме.",
    "shopfloor": "Жанр: цех / производство / команда.",
    "answer": "Жанр: ответ на типичный вопрос или возражение.",
    "note": "Жанр: наблюдение / короткий разбор.",
    "auto": "Жанр выбери сам под тему (мнение, цех, ответ или наблюдение).",
}


class PostGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._skill_prompt = load_skill_prompt(settings.skill_path)
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def generate(
        self,
        topic: str,
        *,
        genre: str = "auto",
        length: str | None = None,
        extra: str | None = None,
    ) -> str:
        length_key = (length or self.settings.default_post_length).lower()
        if length_key not in LENGTH_HINTS:
            length_key = "medium"
        genre_key = genre.lower() if genre in GENRE_HINTS else "auto"

        user_parts = [
            f"Тема / задание: {topic.strip()}",
            LENGTH_HINTS[length_key],
            GENRE_HINTS[genre_key],
            "Верни только текст поста для Telegram, без кавычек-обёрток и без пояснений.",
        ]
        if extra and extra.strip():
            user_parts.append(f"Дополнительные указания: {extra.strip()}")

        response = await self._client.chat.completions.create(
            model=self.settings.openai_model,
            temperature=0.7,
            messages=[
                {"role": "system", "content": self._skill_prompt},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
        )
        content = response.choices[0].message.content
        if not content or not content.strip():
            raise RuntimeError("Модель вернула пустой ответ")
        return content.strip()
