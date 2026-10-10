from __future__ import annotations

from pathlib import Path

SKILL_FILES = (
    "SKILL.md",
    "persona.md",
    "voice-patterns.md",
    "examples.md",
)


def load_skill_prompt(skill_dir: Path) -> str:
    """Собирает system-prompt из файлов reusable skill."""
    if not skill_dir.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    chunks: list[str] = []
    for name in SKILL_FILES:
        path = skill_dir / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        chunks.append(f"## Файл скилла: {name}\n\n{text}")

    if not chunks:
        raise FileNotFoundError(f"No skill files in {skill_dir}")

    return (
        "Ниже — reusable skill голоса Андрея Анатольевича. "
        "Следуй ему при генерации постов. Не копируй дословно чужие интервью; "
        "пиши оригинальный текст в его манере и позиции.\n\n"
        + "\n\n---\n\n".join(chunks)
    )
