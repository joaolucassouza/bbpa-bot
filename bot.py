import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# --------- CONSTANTES DE ESTADO DA CONVERSA ---------
PEDIR_NOME, PERGUNTAR_SE_TEM_ALGO, PEDIR_SAFEWORD = range(3)

TOKEN = os.getenv("BOT_TOKEN")


# --------- FUNÇÕES AUXILIARES PARA JSON ---------
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_saldos_iniciais():
    return load_json("saldos_iniciais.json", {})


def get_safewords():
    return load_json("safewords.json", {})


def get_usuarios():
    return load_json("usuarios.json", {})


def set_usuarios(data):
    save_json("usuarios.json", data)
