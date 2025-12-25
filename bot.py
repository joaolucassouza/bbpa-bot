import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
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
PEDIR_NOME, PERGUNTAR_SE_TEM_ALGO, PEDIR_SAFEWORD, ESCOLHER_CATEGORIA, ESCOLHER_INDICADO, INSERIR_VALOR = range(6)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {6098995197}
BOT_COMMANDS = [
    BotCommand("start", "Registrar e pegar saldo inicial"),
    BotCommand("saldo", "Ver seu saldo atual"),
    BotCommand("deposito", "Depositar moedas em um indicado"),
    BotCommand("status", "Ver em quais categorias você já votou"),
    BotCommand("meus_depositos", "Ver onde você já depositou"),
]

# --------- CATEGORIAS E INDICADOS ---------
CATEGORIAS = {
    # POP
    "Artista Pop": [
        "Ariana Grande",
        "Gracie Abrams",
        "Lady Gaga",
        "Lorde",
        "Marina Sena",
        "ROSALÍA",
        "Sabrina Carpenter",
        "Taylor Swift",
    ],
    "Música Pop": [
        "Abracadabra, Lady Gaga",
        "dandelion, Ariana Grande",
        "David, Lorde",
        "La Yugular, ROSALÍA",
        "The Fate of Ophelia, Taylor Swift",
        "The Subway, Chappell Roan",
        "twilight zone, Ariana Grande",
        "What Was That, Lorde",
    ],
    "Álbum Pop": [
        "Coisas Naturais, Marina Sena",
        "DON'T TAP THE GLASS, Tyler, the Creator",
        "eternal sunshine deluxe: brighter days ahead, Ariana Grande",
        "Man's Best Friend, Sabrina Carpenter",
        "MAYHEM, Lady Gaga",
        "The Life Of a Showgirl, Taylor Swift",
        "Virgin, Lorde",
        "LUX, ROSALÍA",
    ],

    # FOLK/ROCK
    "Álbum Folk/Rock": [
        "All is love and pain in the mouse parade, Of Monsters and Men",
        "Ego Death at a Bachalorette Party, Hayley Williams",
        "Glory, Perfume Genius",
        "I quit, HAIM",
        "mouisturizer, Wet Leg",
        "Older (and Wiser), Lizzy McAlpine",
        "What a Devastating Turn of Events, Rachel Chinouriri",
        "Willoughby Tucker, I'll Always Love You, Ethel Cain",
    ],
    "Artista Folk/Rock": [
        "ANAVITÓRIA",
        "Bon Iver",
        "Ethel Cain",
        "HAIM",
        "Lizzy McAlpine",
        "Of Monsters and Men",
        "Rachel Chinouriri",
        "Wet Leg",
    ],
    "Música Folk/Rock": [
        "All Over Me, HAIM",
        "Everybody Scream, Florence + the Machine",
        "If Only I Could Wait, Bon Iver",
        "isso é deus, ANAVITÓRIA",
        "Nettles, Ethel Cain",
        "pillow talk, Wet Leg",
        "Sanctuary, Tamino",
        "Television Love, Of Monsters and Men",
    ],

    # R&B/RAP
    "Álbum R&B/Rap": [
        "Alligator Bites Never Heal, Doechii",
        "Escape Room, Teyana Taylor",
        "Eu Venci o Mundo, Veigh",
        "GNX, Kendrick Lamar",
        "Hurry Up Tomorrow, The Weeknd",
        "no escuro, quem é você?, Carol Biazin",
        "Positions, Ariana Grande",
        "SOS Deluxe: LANA, SZA",
    ],
    "Artista R&B/Rap": [
        "Brent Faiyaz",
        "Carol Biazin",
        "Doechii",
        "Frank Ocean",
        "Kendrick Lamar",
        "SZA",
        "Tyler, The Creator",
        "Veigh",
    ],
    "Música R&B/Rap": [
        "30 for 30 (with Kendrick Lamar), SZA",
        "Amina, Tasha & Tracie",
        "DENIAL IS A RIVER, Doechii",
        "Lifetime, Erika de Casier",
        "Loud, Olivia Dean",
        "luther (with SZA), Kendrick Lamar",
        "past life, Ariana Grande",
        "sunshine & rain…, Kali Uchis",
    ],

    # GLOBAL
    "Artista Global": [
        "ANAVITÓRIA",
        "Bad Bunny",
        "Gaby Amarantos",
        "JENNIE",
        "KAROL G",
        "Marina Sena",
        "ROSALÍA",
        "Veigh",
    ],
    "Álbum Global": [
        "Coisas Naturais, Marina Sena",
        "DeBÍ TiRAR MáS FoTOS, Bad Bunny",
        "Esquinas, ANAVITÓRIA",
        "Eu Venci o Mundo, Veigh",
        "LUX, ROSALÍA",
        "no escuro, quem é você?, Carol Biazin",
        "Rock Doido, Gaby Amarantos",
        "TROPICOQUETA, KAROL G",
    ],
    "Música Global": [
        "Amina, Tasha & Tracie",
        "Bandida Entrenada, Karol G",
        "Idiota Raiz (Deixa Ir), Joyce Alane",
        "La Yugular, ROSALÍA",
        "JUMP, BLACKPINK",
        "Marolento, Puterrier",
        "Reliquia, ROSALÍA",
        "VOY A LLeVARTE PA PR, Bad Bunny",
    ],

    # TBT
    "#BillboardinhesAlbumTBT": [
        "Bewitched, Laufey",
        "evermore, Taylor Swift",
        "Good Ridance, Gracie Abrams",
        "GUTS, Olivia Rodrigo",
        "Mr. Morale & the Big Steppers, Kendrick Lamar",
        "Positions, Ariana Grande",
        "What’s Your Pleasure?, Jessie Ware",
    ],
    "#BillboardinhesMusicaTBT": [
        "“Heroes”, David Bowie",
        "0208, Jessie Ware",
        "Pessoa, Marina Lima",
        "Poema, Ney Matogrosso",
        "Russian Roulette, Rihanna",
        "Safaera, Bad Bunny",
        "White Ferrari, Frank Ocean",
        "You Belong With Me, Taylor Swift",
    ],

    # Fandom / fan favourite / comeback / track twist / viral / chart breaker
    "Fandom do Ano": [
        "Arianators (Ariana Grande)",
        "Carpenters (Sabrina Carpenter)",
        "Daughters of Cain (Ethel Cain)",
        "Little Monsters (Lady Gaga)",
        "Lordelings (Lorde)",
        "Roses (ROSALÍA)",
        "Swifties (Taylor Swift)",
    ],
    "Fan Favourite": [
        "Ariana Grande",
        "Bad Bunny",
        "Ethel Cain",
        "Kendrick Lamar",
        "Lady Gaga",
        "Lorde",
        "Taylor Swift",
    ],
    "Comeback do Ano": [
        "Ariana Grande – eternal sunshine deluxe: brighter days ahead",
        "Bad Bunny – DeBÍ TiRAR MÁS FOToS",
        "Kendrick Lamar – GNX",
        "Lady Gaga – MAYHEM",
        "Lorde – Virgin",
        "ROSALÍA – LUX",
        "Taylor Swift – The Life Of a Showgirl",
    ],
    "Track Twist": [
        "Broken Glass, Lorde",
        "ODDWADD, Lace Manhattan",
        "Porcelana, ROSALÍA",
        "Ring Ring Ring, Tyler, the Creator",
        "Safaera, Bad Bunny",
        "Stars + DJ Caio Prince + Adame DJ, PinkPantheress",
        "Time, Arca",
    ],
    "Smash Viral": [
        "Bandida Entrenada, KAROL G",
        "Midnight Sun, Zara Larsson",
        "Nettles, Ethel Cain",
        "ODDWADD, Lace Manhattan",
        "Poema, Ney Matogrosso",
        "Spiders, Lola Young",
        "Television Love, Of Monsters and Men",
    ],
    "Chart Breaker": [
        "DENIAL IS A RIVER, Doechii",
        "How Bad Do U Want Me, Lady Gaga",
        "If Only I Could Wait, Bon Iver",
        "La Yugular, ROSALÍA",
        "Opalite, Taylor Swift",
        "SUGAR ON MY TONGUE, Tyler, the Creator",
        "What Was That, Lorde",
    ],
    "Feat do Ano": [
        "Berghain – ROSALÍA & Björk & Yves Tumor",
        "Born Again - LISA, RAYE, Doja Cat",
        "ExtraL (feat. Doechii) – JENNIE",
        "If Only I Could Wait – Bon Iver & Danielle Haim",
        "luther (with SZA) – Kendrick Lamar",
        "The Life Of a Showgirl (feat. Sabrina Carpenter) – Taylor Swift",
        "Walk Of Fame (feat. Brittany Howard) – Miley Cyrus",
    ],
    "Sample do Ano": [
        "Anxiety, Doechii",
        "Berghain, ROSALÍA",
        "Current Affairs, Lorde",
        "Father Figure, Taylor Swift",
        "FLOR DE MAIO, Xamã",
        "luther (with SZA), Kendrick Lamar",
        "Safaera, Bad Bunny",
    ],
    "Hitmaker do Ano": [
        "Ethel Cain",
        "Gracie Abrams",
        "HAIM",
        "Kendrick Lamar",
        "Laufey",
        "Lorde",
        "Taylor Swift",
    ],
    "Bangermaker do Ano": [
        "Ariana Grande",
        "Bad Bunny",
        "Lady Gaga",
        "Marina Sena",
        "ROSALÍA",
        "Sabrina Carpenter",
        "SZA",
    ],
    "Single do Ano": [
        "Abracadabra - Lady Gaga",
        "Fuck Me Eyes - Ethel Cain",
        "luther (with SZA) - Kendrick Lamar",
        "The Fate Of Ophelia - Taylor Swift",
        "The Subway - Chappell Roan",
        "twilight zone - Ariana Grande",
        "What Was That - Lorde",
    ],

    # BIG FIVE
    "Dominador dos Charts": [
        "Ariana Grande",
        "Bad Bunny",
        "Ethel Cain",
        "Kendrick Lamar",
        "Lady Gaga",
        "Lorde",
        "ROSALÍA",
        "Sabrina Carpenter",
        "SZA",
        "Taylor Swift",
    ],
    "Álbum do Ano": [
        "A Matter of Time – Laufey",
        "Coisas Naturais – Marina Sena",
        "DeBÍ TiRAR MáS FOToS – Bad Bunny",
        "eternal sunshine deluxe: brighter days ahead – Ariana Grande",
        "GNX – Kendrick Lamar",
        "LUX – ROSALÍA",
        "Man's Best Friend – Sabrina Carpenter",
        "MAYHEM – Lady Gaga",
        "The Life Of a Showgirl – Taylor Swift",
        "Virgin – Lorde",
    ],
    "Hit do Ano": [
        "Abracadabra – Lady Gaga",
        "dandelion – Ariana Grande",
        "David – Lorde",
        "DENIAL IS A RIVER – Doechii",
        "Fuck Me Eyes – Ethel Cain",
        "La Yugular – ROSALÍA",
        "luther (with SZA) – Kendrick Lamar",
        "The Fate of Ophelia – Taylor Swift",
        "The Subway – Chappell Roan",
        "What Was That – Lorde",
    ],
    "Sleeper Hit": [
        "Abracadabra — Lady Gaga",
        "Current Affairs — Lorde",
        "DENIAL IS A RIVER — Doechii",
        "La Yugular — ROSALÍA",
        "luther (with SZA) — Kendrick Lamar",
        "Midnight Sun — Zara Larsson",
        "Opalite — Taylor Swift",
        "twilight zone — Ariana Grande",
        "What Was That — Lorde",
        "WHERE IS MY HUSBAND! — RAYE",
    ],
    "Revelação do Ano": [
        "Amaarae",
        "Carol Biazin",
        "Doechii",
        "JENNIE",
        "Lizzy McAlpine",
        "Olivia Dean",
        "RAYE",
        "Rachel Chinouriri",
        "The Marías",
        "Wet Leg",
    ],
}

CAT_IDS = {nome: f"c{idx}" for idx, nome in enumerate(CATEGORIAS.keys(), start=1)}
ID_TO_CAT = {v: k for k, v in CAT_IDS.items()}
# garante IDs para categorias problemáticas
CAT_IDS["Feat do Ano"] = "feat"
CAT_IDS["Álbum Folk/Rock"] = "album_folk_rock"

ID_TO_CAT["feat"] = "Feat do Ano"
ID_TO_CAT["album_folk_rock"] = "Álbum Folk/Rock"
# IDs curtos para indicados por categoria
IND_IDS = {}
ID_TO_IND = {}

for categoria, lista in CATEGORIAS.items():
    inds_cat = {}
    rev_inds_cat = {}
    for idx, nome in enumerate(lista, start=1):
        ind_id = f"i{idx}"
        inds_cat[nome] = ind_id
        rev_inds_cat[ind_id] = nome
    IND_IDS[categoria] = inds_cat
    ID_TO_IND[categoria] = rev_inds_cat

# --------- DESCRIÇÕES DAS CATEGORIAS ---------
DESCRICOES_CATEGORIAS = {
    "Single do Ano": (
        "Categoria que considera apenas singles de trabalho, lançados isoladamente "
        "para divulgar o artista, um álbum ou engajar o fandom."
    ),
    "Hitmaker do Ano": (
        "Categoria que premia o artista que mais teve músicas consideradas grandes "
        "composições durante o ano."
    ),
    "Bangermaker do Ano": (
        "Categoria que premia o artista que mais teve músicas ouvidas principalmente "
        "pela produção e batida, aquelas faixas que viram banger pelo som em si."
    ),
    "Sample do Ano": (
        "Melhor uso criativo de sample ou interpolação: não é só copiar, é transformar "
        "a referência em algo novo e marcante."
    ),
    "Feat do Ano": (
        "Colaboração mais impactante: química entre artistas, destaque de todos os "
        "envolvidos e efeito da parceria nos charts."
    ),
    "Chart Breaker": (
        "Faixa que mais quebrou as paradas: grandes subidas, picos inesperados ou "
        "saltos absurdos em relação ao debut."
    ),
    "Smash Viral": (
        "Música que inesperadamente hitou dentro do grupo sem ter fandom estabelecido: "
        "geralmente começa com uma pessoa colocando nos charts e, a partir daí, alcança mais gente "
        "ou vira um hit de um só."
    ),
    "Crossover do Ano": (
        "Música que atravessou fronteiras: juntou gêneros ou públicos diferentes e "
        "conseguiu se tornar grande em mais de uma bolha."
    ),
    "Comeback do Ano": (
        "Retorno mais relevante às paradas: artista que voltou de hiato, flop, sumiço "
        "ou mudança de fase e reassumiu seu espaço."
    ),
    "Fan Favourite": (
        "Artista ou ato que o grupo mais abraçou emocionalmente: xodó coletivo, "
        "presença constante em comentários e playlists, mesmo sem ser necessariamente o maior em números."
    ),
    "Fandom do Ano": (
        "Fandom mais ativo e barulhento: quem mais mobiliza o grupo, força streams, "
        "defende artista em discussão e pesa nos charts."
    ),
    "Track Twist": (
        "Faixa que mistura mundos diferentes: gêneros improváveis, referências estranhas "
        "ou viradas inesperadas que ainda assim funcionam muito bem."
    ),
}

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

def debug_log_safewords():
    data = get_safewords()
    print("DEBUG_SAFEWORDS:", data)

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

async def meu_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Seu ID é: {chat_id}")

async def relatorio_depositos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in ADMIN_IDS:
        await update.message.reply_text("Comando disponível só para admin.")
        return

    usuarios = get_usuarios()

    # --- totais por categoria/indicado ---
    totais = {}  # (categoria, indicado) -> soma
    categorias_por_usuario = {}  # chat_id -> set(categorias com depósito)

    for uid, dados in usuarios.items():
        depositos = dados.get("depositos", [])
        cats_user = set()
        for dep in depositos:
            categoria = dep["categoria"]
            indicado = dep["indicado"]
            valor = dep["valor"]

            chave = (categoria, indicado)
            totais[chave] = totais.get(chave, 0) + valor

            cats_user.add(categoria)

        categorias_por_usuario[uid] = cats_user

    if not usuarios:
        await update.message.reply_text("Ainda não há usuários registrados.")
        return

    if not totais:
        await update.message.reply_text("Ainda não há depósitos registrados.")
        return

    linhas = []

    # --- parte 1: totais por indicado ---
    categorias_ordenadas = sorted({c for (c, _) in totais.keys()})
    for categoria in categorias_ordenadas:
        linhas.append(f"\n📂 {categoria}:")
        pares = [(ind, v) for (c, ind), v in totais.items() if c == categoria]
        pares.sort(key=lambda x: -x[1])
        for indicado, valor in pares:
            linhas.append(f"  • {indicado}: {valor} moedas")

    # --- parte 2: quem ainda não depositou em cada categoria ---
    todas_categorias = set(CATEGORIAS.keys())
    linhas.append("\n\n👥 Usuários que ainda não depositaram por categoria:")

    # mapeia id -> nome para ficar legível
    nomes_usuarios = {
        uid: dados.get("nome", uid)
        for uid, dados in usuarios.items()
    }

    for categoria in sorted(todas_categorias):
        faltam = [
            nomes_usuarios[uid]
            for uid, cats in categorias_por_usuario.items()
            if categoria not in cats
        ]
        if not faltam:
            continue

        linhas.append(f"\n• {categoria}:")
        for nome in sorted(faltam):
            linhas.append(f"  - {nome}")

    await update.message.reply_text("\n".join(linhas[:4000]))

async def meus_depositos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    usuarios = get_usuarios()

    if chat_id not in usuarios:
        await update.message.reply_text(
            "Ainda não te reconheço.\n"
            "Use /start para se registrar com sua safeword."
        )
        return

    usuario = usuarios[chat_id]
    lista = usuario.get("depositos", [])

    if not lista:
        await update.message.reply_text("Você ainda não fez nenhum depósito.")
        return

    # agrupa por categoria/indicado
    totais = {}
    for dep in lista:
        chave = (dep["categoria"], dep["indicado"])
        totais[chave] = totais.get(chave, 0) + dep["valor"]

    linhas = ["Seus depósitos:"]
    categorias = sorted({c for (c, _) in totais.keys()})
    for categoria in categorias:
        linhas.append(f"\n📂 {categoria}:")
        pares = [(ind, v) for (c, ind), v in totais.items() if c == categoria]
        pares.sort(key=lambda x: -x[1])
        for indicado, valor in pares:
            linhas.append(f"  • {indicado}: {valor} moedas")

    await update.message.reply_text("\n".join(linhas[:4000]))

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
    
# --------- COMANDO /status ---------

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra saldo e situação de depósitos por categoria."""
    chat_id = str(update.effective_chat.id)
    usuarios = get_usuarios()

    if chat_id not in usuarios:
        await update.message.reply_text(
            "Ainda não te reconheço.\n"
            "Use /start para se registrar com sua safeword."
        )
        return

    usuario = usuarios[chat_id]
    saldo_atual = usuario.get("saldo", 0)

    # usa os depósitos reais para descobrir em quais categorias a pessoa já apostou
    depositos = usuario.get("depositos", [])
    categorias_votadas = {dep["categoria"] for dep in depositos}

    todas_categorias = set(CATEGORIAS.keys())
    categorias_faltantes = sorted(todas_categorias - categorias_votadas)
    categorias_feitas = sorted(categorias_votadas & todas_categorias)

    texto = [f"Seu saldo atual: {saldo_atual} moedas de Payola de Ouro.\n"]

    if categorias_feitas:
        texto.append("Categorias em que você já votou:")
        for cat in categorias_feitas:
            texto.append(f"• {cat}")
    else:
        texto.append("Você ainda não votou em nenhuma categoria.")

    if categorias_faltantes:
        texto.append("\nCategorias que ainda faltam:")
        for cat in categorias_faltantes:
            texto.append(f"• {cat}")
    else:
        texto.append("\nVocê já votou em todas as categorias disponíveis!")

    await update.message.reply_text("\n".join(texto))

# --------- FLUXO DE DEPÓSITO COM /deposito ---------

async def deposito_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o fluxo de depósito: escolhe categoria."""
    chat_id = str(update.effective_chat.id)
    usuarios = get_usuarios()

    if chat_id not in usuarios:
        await update.message.reply_text(
            "Ainda não te reconheço.\n"
            "Use /start para se registrar com sua safeword antes de depositar moedas."
        )
        return ConversationHandler.END

    # Zera dados temporários de depósito
    context.user_data["deposito"] = {}

    # Monta teclado com todas as categorias
    botoes = []
    linha = []
    for nome_cat in CATEGORIAS.keys():
        # usa ID curto para não estourar limite de callback_data
        cat_id = CAT_IDS[nome_cat]
        linha.append(
            InlineKeyboardButton(
                nome_cat,
                callback_data=f"cat_{cat_id}",
            )
        )
        if len(linha) == 2:
            botoes.append(linha)
            linha = []
    if linha:
        botoes.append(linha)

    reply_markup = InlineKeyboardMarkup(botoes)

    await update.message.reply_text(
        "Escolha a categoria em que você quer depositar moedas:",
        reply_markup=reply_markup,
    )
    return ESCOLHER_CATEGORIA

async def deposito_escolher_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a categoria escolhida e mostra os indicados daquela categoria."""
    query = update.callback_query
    await query.answer()

    data = query.data  # ex.: 'cat_c12'
    if not data.startswith("cat_"):
        await query.edit_message_text("Categoria inválida. Use /deposito de novo.")
        return ConversationHandler.END

    cat_id = data[4:]  # remove 'cat_'
    categoria = ID_TO_CAT.get(cat_id)
    if not categoria:
        await query.edit_message_text("Categoria não encontrada. Use /deposito de novo.")
        return ConversationHandler.END

    context.user_data.setdefault("deposito", {})
    context.user_data["deposito"]["categoria"] = categoria

    indicados = CATEGORIAS[categoria]

    if not indicados:
        await query.edit_message_text(
            f"A categoria {categoria} ainda não tem indicados cadastrados."
        )
        return ConversationHandler.END

    # Monta teclado com indicados (prefixo 'ind_')
    botoes = []
    linha = []
    for nome_ind in indicados:
        ind_id = IND_IDS[categoria][nome_ind]
        linha.append(
            InlineKeyboardButton(
                nome_ind,
                callback_data=f"ind_{categoria}|{ind_id}",
        )
    )
        if len(linha) == 1:  # 1 por linha pra não ficar muito apertado
            botoes.append(linha)
            linha = []
    if linha:
        botoes.append(linha)

    # linha extra com Voltar + Cancelar
    botoes.append([
        InlineKeyboardButton("⬅️ Trocar categoria", callback_data="dep_voltar_cat"),
        InlineKeyboardButton("❌ Cancelar depósito", callback_data="dep_cancelar"),
    ])

    reply_markup = InlineKeyboardMarkup(botoes)

    # descrição da categoria antes dos botões
    desc = DESCRICOES_CATEGORIAS.get(categoria)

    texto = [f"Categoria escolhida: {categoria}"]
    if desc:
        texto.append(desc)
    texto.append("Agora escolha o indicado que vai receber moedas:")

    await query.edit_message_text(
        "\n".join(texto),
        reply_markup=reply_markup,
    )

    return ESCOLHER_INDICADO

async def deposito_escolher_indicado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recebe o indicado escolhido e pergunta quantas moedas depositar."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("ind_"):
        await query.edit_message_text("Indicado inválido.")
        return ConversationHandler.END

    payload = data[4:]
    try:
        categoria, ind_id = payload.split("|", 1)
    except ValueError:
        await query.edit_message_text("Indicado inválido.")
        return ConversationHandler.END

# reconstrói o nome do indicado a partir do ID curto
    indicado = ID_TO_IND.get(categoria, {}).get(ind_id)
    if not indicado:
        await query.edit_message_text("Não consegui identificar esse indicado.")
        return ConversationHandler.END

# garante que categoria bate com o que estava salvo no contexto
    deposito = context.user_data.get("deposito", {})
    categoria_ctx = deposito.get("categoria")
    if categoria_ctx != categoria:
        await query.edit_message_text(
        "Não consegui associar esse indicado à categoria atual. Use /deposito de novo."
    )
        return ConversationHandler.END

    deposito = context.user_data.get("deposito", {})
    categoria = deposito.get("categoria")

    if not categoria or categoria not in CATEGORIAS:
        await query.edit_message_text(
            "Não consegui associar esse indicado a uma categoria válida."
        )
        return ConversationHandler.END

    context.user_data["deposito"]["indicado"] = indicado

    desc = DESCRICOES_CATEGORIAS.get(categoria)

    texto = [f"Categoria: {categoria}"]
    if desc:
        texto.append(desc)
    texto.append(f"\nIndicado: {indicado}\n")
    texto.append("Quantas moedas você quer depositar aqui?")
    texto.append("(Lembre-se: máximo 50 moedas por indicado.)")

    await query.edit_message_text("\n".join(texto))
    
    return INSERIR_VALOR

async def deposito_inserir_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o valor em moedas, valida e registra o depósito."""
    texto = update.message.text.strip()

    try:
        valor = int(texto)
    except ValueError:
        await update.message.reply_text(
            "Não entendi esse número.\n"
            "Digite apenas o valor em moedas (ex.: 20)."
        )
        return INSERIR_VALOR

    if valor <= 0:
        await update.message.reply_text(
            "O valor precisa ser maior que zero. Tente de novo."
        )
        return INSERIR_VALOR

    deposito = context.user_data.get("deposito", {})
    categoria = deposito.get("categoria")
    indicado = deposito.get("indicado")

    if not categoria or not indicado:
        await update.message.reply_text(
            "Perdi o contexto do seu depósito. Use /deposito de novo."
        )
        return ConversationHandler.END

    chat_id = str(update.effective_chat.id)
    usuarios = get_usuarios()

    if chat_id not in usuarios:
        await update.message.reply_text(
            "Ainda não te reconheço.\n"
            "Use /start para se registrar com sua safeword."
        )
        return ConversationHandler.END

    usuario = usuarios[chat_id]
    saldo_atual = usuario.get("saldo", 0)

    # valida saldo
    if valor > saldo_atual:
        await update.message.reply_text(
            f"Você não tem saldo suficiente. Seu saldo atual é de {saldo_atual} moedas."
        )
        return INSERIR_VALOR

    # garante que 'depositos' é lista
    if not isinstance(usuario.get("depositos"), list):
        usuario["depositos"] = []

    usuario["depositos"].append(
        {"categoria": categoria, "indicado": indicado, "valor": valor}
    )

    # atualiza saldo e salva JSON
    usuario["saldo"] = saldo_atual - valor
    usuarios[chat_id] = usuario
    set_usuarios(usuarios)  # usa a função que já existe para salvar em usuarios.json

    await update.message.reply_text(
        f"Depósito registrado!\n"
        f"Categoria: {categoria}\n"
        f"Indicado: {indicado}\n"
        f"Valor: {valor} moedas\n"
        f"Novo saldo: {usuario['saldo']} moedas."
    )

    # limpa contexto do depósito
    context.user_data.pop("deposito", None)

    return ConversationHandler.END

async def deposito_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.pop("deposito", None)
    await query.edit_message_text("Depósito cancelado.")
    return ConversationHandler.END


async def deposito_voltar_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data.pop("deposito", None)

    botoes = []
    linha = []
    for categoria in CATEGORIAS.keys():
        linha.append(InlineKeyboardButton(categoria, callback_data=f"cat_{categoria}"))
        if len(linha) == 1:
            botoes.append(linha)
            linha = []
    if linha:
        botoes.append(linha)

    reply_markup = InlineKeyboardMarkup(botoes)

    await query.edit_message_text(
        "Escolha a categoria em que você quer depositar moedas:",
        reply_markup=reply_markup,
    )

    return ESCOLHER_CATEGORIA


async def deposito_voltar_indicado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    deposito = context.user_data.get("deposito", {})
    categoria = deposito.get("categoria")

    if not categoria or categoria not in CATEGORIAS:
        await query.edit_message_text("Não consegui recuperar a categoria. Use /deposito de novo.")
        return ConversationHandler.END

    indicados = CATEGORIAS[categoria]

    botoes = []
    linha = []
    for nome_ind in indicados:
        linha.append(InlineKeyboardButton(nome_ind, callback_data=f"ind_{nome_ind}"))
        if len(linha) == 1:
            botoes.append(linha)
            linha = []
    if linha:
        botoes.append(linha)

    botoes.append([
        InlineKeyboardButton("⬅️ Trocar categoria", callback_data="dep_voltar_cat"),
        InlineKeyboardButton("❌ Cancelar depósito", callback_data="dep_cancelar"),
    ])

    reply_markup = InlineKeyboardMarkup(botoes)

    desc = DESCRICOES_CATEGORIAS.get(categoria)
    texto = [f"Categoria escolhida: {categoria}"]
    if desc:
        texto.append(desc)
    texto.append("Agora escolha o indicado que vai receber moedas:")

    await query.edit_message_text(
        "\n".join(texto),
        reply_markup=reply_markup,
    )

    return ESCOLHER_INDICADO

    # ---- Regra 1: limite de 50 moedas por indicado ----
    depositos_user = usuario.setdefault("depositos", {})
    depositos_cat = depositos_user.setdefault(categoria, {})
    ja_depositado = depositos_cat.get(indicado, 0)
    total_indicado = ja_depositado + valor

    if total_indicado > 50:
        max_extra = 50 - ja_depositado
        if max_extra < 0:
            max_extra = 0
        await update.message.reply_text(
            f"Depósito recusado: você já colocou {ja_depositado} moedas em\n"
            f"“{indicado}” ({categoria}) e o limite por indicado é 50.\n"
            f"Você ainda pode colocar no máximo {max_extra} moedas nesse indicado."
        )
        return INSERIR_VALOR

    # ---- Regra 2: saldo total disponível ----
    if valor > saldo_atual:
        await update.message.reply_text(
            f"Depósito recusado: você só tem {saldo_atual} moedas de Payola de Ouro."
        )
        return INSERIR_VALOR

    # Atualiza saldo e depósitos
    usuario["saldo"] = saldo_atual - valor
    depositos_cat[indicado] = total_indicado

    categorias_votadas = usuario.setdefault("categorias_votadas", [])
    if categoria not in categorias_votadas:
        categorias_votadas.append(categoria)

    usuarios[chat_id] = usuario
    set_usuarios(usuarios)

    await update.message.reply_text(
        f"Depósito confirmado: {valor} moedas em\n"
        f"“{indicado}” ({categoria}).\n\n"
        f"Seu saldo atual é de {usuario['saldo']} moedas de Payola de Ouro.\n"
        "Se quiser fazer outro depósito, use /deposito novamente."
    )

    # Limpa os dados temporários de depósito
    context.user_data.pop("deposito", None)

    return ConversationHandler.END

# --------- FUNÇÃO PRINCIPAL ---------
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN não foi definido nas variáveis de ambiente.")

    async def post_init(application):
        # define o menu de comandos do bot
        bot_commands = [
            BotCommand("start", "Registrar e pegar saldo inicial"),
            BotCommand("saldo", "Ver seu saldo atual"),
            BotCommand("deposito", "Depositar moedas em um indicado"),
            BotCommand("status", "Ver em quais categorias você já votou"),
            BotCommand("meus_depositos", "Ver onde você já depositou"),
        ]
        await application.bot.set_my_commands(bot_commands)

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

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

    # ConversationHandler para o fluxo de depósito com /deposito
    deposito_handler = ConversationHandler(
        entry_points=[CommandHandler("deposito", deposito_inicio)],
        states={
            ESCOLHER_CATEGORIA: [
                CallbackQueryHandler(deposito_escolher_categoria, pattern="^cat_"),
                CallbackQueryHandler(deposito_cancelar, pattern="^dep_cancelar$"),
            ],
            ESCOLHER_INDICADO: [
                CallbackQueryHandler(deposito_escolher_indicado, pattern="^ind_"),
                CallbackQueryHandler(deposito_voltar_categoria, pattern="^dep_voltar_cat$"),
                CallbackQueryHandler(deposito_cancelar, pattern="^dep_cancelar$"),
            ],
            INSERIR_VALOR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deposito_inserir_valor),
                CallbackQueryHandler(deposito_voltar_indicado, pattern="^dep_voltar_ind$"),
                CallbackQueryHandler(deposito_cancelar, pattern="^dep_cancelar$"),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.add_handler(deposito_handler)
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("meu_id", meu_id))
    app.add_handler(CommandHandler("meus_depositos", meus_depositos))
    app.add_handler(CommandHandler("relatorio_depositos", relatorio_depositos))

    app.run_polling()


if __name__ == "__main__":
    main()
