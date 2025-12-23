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
# --------- FLUXO DE REGISTRO COM /start ---------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Início da conversa: pedir o nome de exibição."""
    user = update.effective_user
    context.user_data.clear()  # zera qualquer conversa anterior

    await update.message.reply_text(
        "Oi! Eu sou o bot da BBPA.\n\n"
        "Primeiro, me diz um nome para eu te chamar aqui dentro:"
    )
    return PEDIR_NOME


async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda o nome que a pessoa escolheu e pergunta se tem algo a mais."""
    nome = update.message.text.strip()
    context.user_data["nome_exibicao"] = nome

    # Botões "Sim" / "Não"
    keyboard = [
        [
            InlineKeyboardButton("Sim", callback_data="tem_algo_sim"),
            InlineKeyboardButton("Não", callback_data="tem_algo_nao"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Beleza, vou te chamar de {nome}.\n\n"
        "Você tem mais algo para me contar?",
        reply_markup=reply_markup,
    )
    return PERGUNTAR_SE_TEM_ALGO


async def perguntar_se_tem_algo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata o clique nos botões Sim/Não."""
    query = update.callback_query
    await query.answer()

    escolha = query.data  # 'tem_algo_sim' ou 'tem_algo_nao'

    if escolha == "tem_algo_nao":
        await query.edit_message_text(
            "Ainda não te reconheço. Você não está registrado no meu banco de Payola.\n\n"
            "Quando quiser se registrar, use /start novamente."
        )
        return ConversationHandler.END

    # Se respondeu "Sim", pedir a safeword
    await query.edit_message_text(
        "Então me conta.\n\n"
        "Escreve a sua palavra secreta (safeword):"
    )
    return PEDIR_SAFEWORD


async def receber_safeword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a safeword, confere nos arquivos e registra o usuário."""
    safeword_digitada = update.message.text.strip()

    safewords = get_safewords()
    saldos_iniciais = get_saldos_iniciais()
    usuarios = get_usuarios()

    if safeword_digitada not in safewords:
        await update.message.reply_text(
            "Não te encontrei na minha lista com essa palavra.\n\n"
            "Confere a safeword ou fala com a produção.\n"
            "Se quiser tentar de novo, use /start."
        )
        return ConversationHandler.END

    username_oficial = safewords[safeword_digitada]

    if username_oficial not in saldos_iniciais:
        await update.message.reply_text(
            "Encontrei sua safeword, mas não achei seu saldo inicial.\n"
            "Fala com a produção para corrigirem seu cadastro."
        )
        return ConversationHandler.END

    saldo_inicial = saldos_iniciais[username_oficial]
    chat_id = str(update.effective_chat.id)
    nome_exibicao = context.user_data.get("nome_exibicao", username_oficial)

    # Cria ou atualiza o usuário em usuarios.json
    usuarios[chat_id] = {
        "nome_exibicao": nome_exibicao,
        "username_oficial": username_oficial,
        "saldo": saldo_inicial,
        "categorias_votadas": [],
        "depositos": {}
    }
    set_usuarios(usuarios)

    await update.message.reply_text(
        f"Certo, {nome_exibicao}.\n\n"
        f"Você foi reconhecido como @{username_oficial} com {saldo_inicial} moedas de Payola de Ouro.\n"
        "Agora você pode usar /saldo e, em breve, /deposito."
    )

    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permite cancelar a conversa a qualquer momento."""
    await update.message.reply_text("Registro cancelado. Use /start se quiser tentar de novo.")
    return ConversationHandler.END
# --------- COMANDO /saldo ---------

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra o saldo atual do usuário, se ele já estiver registrado."""
    chat_id = str(update.effective_chat.id)
    usuarios = get_usuarios()

    if chat_id not in usuarios:
        await update.message.reply_text(
            "Ainda não te reconheço.\n"
            "Use /start para se registrar com sua safeword."
        )
        return

    dados = usuarios[chat_id]
    saldo_atual = dados.get("saldo", 0)
    nome_exibicao = dados.get("nome_exibicao", "você mesmo")

    await update.message.reply_text(
        f"{nome_exibicao}, seu saldo atual é de {saldo_atual} moedas de Payola de Ouro."
    )


# --------- FUNÇÃO PRINCIPAL ---------

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN não foi definido nas variáveis de ambiente.")

    app = ApplicationBuilder().token(TOKEN).build()

    # ConversationHandler para o fluxo de registro com /start
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PEDIR_NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)],
            PERGUNTAR_SE_TEM_ALGO: [CallbackQueryHandler(perguntar_se_tem_algo)],
            PEDIR_SAFEWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_safeword)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("saldo", saldo))

    app.run_polling()


if __name__ == "__main__":
    main()
