from telegram import Update
from telegram.ext import ContextTypes
import json
from pathlib import Path

_I18N_PATH = Path(__file__).parent.parent / "i18n"
_TRANSLATIONS: dict[str, dict[str, str]] = {}

def load_translations() -> None:
    for file in _I18N_PATH.glob("*.json"):
        lang = file.stem
        with open(file, encoding="utf-8") as f:
            _TRANSLATIONS[lang] = json.load(f)

def t(lang: str, key: str) -> str:
    return (
        _TRANSLATIONS
        .get(lang, _TRANSLATIONS.get("en", {}))
        .get(key, key)
    )

def get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get( # type: ignore
        "lang",
        update.effective_user.language_code or "uz" # type: ignore
    )