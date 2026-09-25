import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "signos.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Dados dos 12 signos (mesmos usados no front-end, agora centralizados aqui)
# ---------------------------------------------------------------------------
SIGNS = [
    {"name": "Áries", "glyph": "♈", "from_": (3, 21), "to": (4, 19), "element": "Fogo",
     "planet": "Marte", "modality": "Cardinal",
     "traits": ["Toma iniciativa antes de pensar duas vezes", "Direto ao ponto, sem rodeios",
                "Compete até com a própria sombra", "Recupera o ânimo rápido depois de um tropeço"],
     "compat": ["Leão", "Sagitário"]},
    {"name": "Touro", "glyph": "♉", "from_": (4, 20), "to": (5, 20), "element": "Terra",
     "planet": "Vênus", "modality": "Fixo",
     "traits": ["Valoriza conforto, comida boa e rotina", "Teimoso quando decide algo",
                "Leal até o fim com quem confia", "Aprecia o ritmo devagar e sempre"],
     "compat": ["Virgem", "Capricórnio"]},
    {"name": "Gêmeos", "glyph": "♊", "from_": (5, 21), "to": (6, 20), "element": "Ar",
     "planet": "Mercúrio", "modality": "Mutável",
     "traits": ["Curioso sobre praticamente tudo", "Muda de assunto e de humor rápido",
                "Comunicador nato, adora uma conversa", "Se entedia fácil com repetição"],
     "compat": ["Libra", "Aquário"]},
    {"name": "Câncer", "glyph": "♋", "from_": (6, 21), "to": (7, 22), "element": "Água",
     "planet": "Lua", "modality": "Cardinal",
     "traits": ["Sensível ao clima emocional ao redor", "Protege quem ama como se fosse ninho",
                "Guarda memórias com carinho exagerado", "Precisa de um lar, literal ou figurado"],
     "compat": ["Escorpião", "Peixes"]},
    {"name": "Leão", "glyph": "♌", "from_": (7, 23), "to": (8, 22), "element": "Fogo",
     "planet": "Sol", "modality": "Fixo",
     "traits": ["Brilha naturalmente em qualquer sala", "Generoso, mas espera reconhecimento",
                "Criativo e um pouco dramático", "Fiel a quem faz parte do seu círculo"],
     "compat": ["Áries", "Sagitário"]},
    {"name": "Virgem", "glyph": "♍", "from_": (8, 23), "to": (9, 22), "element": "Terra",
     "planet": "Mercúrio", "modality": "Mutável",
     "traits": ["Percebe o detalhe que todo mundo ignorou", "Ajuda de forma prática, não só com palavras",
                "Exigente consigo antes de exigir dos outros", "Organiza o caos até ele fazer sentido"],
     "compat": ["Touro", "Capricórnio"]},
    {"name": "Libra", "glyph": "♎", "from_": (9, 23), "to": (10, 22), "element": "Ar",
     "planet": "Vênus", "modality": "Cardinal",
     "traits": ["Busca equilíbrio antes de tomar partido", "Tem faro para estética e harmonia",
                "Evita conflito até não dar mais", "Ótimo em ver os dois lados de tudo"],
     "compat": ["Gêmeos", "Aquário"]},
    {"name": "Escorpião", "glyph": "♏", "from_": (10, 23), "to": (11, 21), "element": "Água",
     "planet": "Plutão", "modality": "Fixo",
     "traits": ["Vai fundo, nunca fica na superfície", "Intenso em tudo que sente",
                "Guarda segredos como cofre", "Se reinventa depois de qualquer queda"],
     "compat": ["Câncer", "Peixes"]},
    {"name": "Sagitário", "glyph": "♐", "from_": (11, 22), "to": (12, 21), "element": "Fogo",
     "planet": "Júpiter", "modality": "Mutável",
     "traits": ["Precisa de horizonte, mapa e liberdade", "Otimista mesmo quando o plano falha",
                "Fala o que pensa, sem filtro", "Aprende viajando, lendo ou testando"],
     "compat": ["Áries", "Leão"]},
    {"name": "Capricórnio", "glyph": "♑", "from_": (12, 22), "to": (1, 19), "element": "Terra",
     "planet": "Saturno", "modality": "Cardinal",
     "traits": ["Joga a longo prazo, sempre", "Disciplinado até quando ninguém está olhando",
                "Prático: prefere resultado a promessa", "Leva responsabilidade a sério, às vezes demais"],
     "compat": ["Touro", "Virgem"]},
    {"name": "Aquário", "glyph": "♒", "from_": (1, 20), "to": (2, 18), "element": "Ar",
     "planet": "Urano", "modality": "Fixo",
     "traits": ["Pensa fora do padrão por natureza", "Valoriza a coletividade mais que o próprio ego",
                "Independente até incomodar quem está perto", "Curioso por ideias que ainda não existem"],
     "compat": ["Gêmeos", "Libra"]},
    {"name": "Peixes", "glyph": "♓", "from_": (2, 19), "to": (3, 20), "element": "Água",
     "planet": "Netuno", "modality": "Mutável",
     "traits": ["Absorve o clima emocional de quem está por perto", "Imaginação fértil, meio pé no sonho",
                "Compassivo até se esquecer de si", "Artístico, mesmo sem se considerar um artista"],
     "compat": ["Câncer", "Escorpião"]},
]

MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def find_sign(month: int, day: int) -> dict:
    for s in SIGNS:
        fm, fd = s["from_"]
        tm, td = s["to"]
        if fm == tm:
            if month == fm and fd <= day <= td:
                return s
        elif fm < tm:
            if (month == fm and day >= fd) or (month == tm and day <= td):
                return s
        else:  # signo que cruza a virada do ano (Capricórnio)
            if (month == fm and day >= fd) or (month == tm and day <= td):
                return s
    return SIGNS[-1]


# ---------------------------------------------------------------------------
# Banco de dados (SQLite por padrão; troque a connection string para usar
# MySQL/Postgres com pouquíssimas mudanças)
# ---------------------------------------------------------------------------
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/descobrir", methods=["POST"])
def descobrir():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    birthdate = (data.get("birthdate") or "").strip()

    if not birthdate:
        return jsonify({"error": "Informe a data de nascimento."}), 400

    try:
        year, month, day = (int(part) for part in birthdate.split("-"))
    except ValueError:
        return jsonify({"error": "Data inválida. Use o formato AAAA-MM-DD."}), 400

    sign = find_sign(month, day)

    db = get_db()
    db.execute(
        "INSERT INTO submissions (name, birthdate, sign_name) VALUES (?, ?, ?)",
        (name or None, birthdate, sign["name"]),
    )
    db.commit()

    return jsonify({
        "name": sign["name"],
        "glyph": sign["glyph"],
        "date_range": f'{sign["from_"][1]} de {MONTHS[sign["from_"][0] - 1]} — '
                       f'{sign["to"][1]} de {MONTHS[sign["to"][0] - 1]}',
        "element": sign["element"],
        "planet": sign["planet"],
        "modality": sign["modality"],
        "traits": sign["traits"],
        "compat": [{"name": c, "glyph": next(s["glyph"] for s in SIGNS if s["name"] == c)}
                   for c in sign["compat"]],
    })


@app.route("/api/historico")
def historico():
    """Últimas consultas salvas no banco — útil para ver o SQL funcionando."""
    db = get_db()
    rows = db.execute(
        "SELECT name, birthdate, sign_name, created_at "
        "FROM submissions ORDER BY id DESC LIMIT 20"
    ).fetchall()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    if not DB_PATH.exists():
        init_db()
    app.run(debug=True)
