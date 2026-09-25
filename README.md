# Qual é o seu signo? — Flask + SQL

## Como rodar

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000 no navegador. O banco `signos.db` (SQLite) é criado
automaticamente na primeira execução, a partir de `schema.sql`.

## Estrutura

```
signo-flask/
├── app.py              # rotas Flask + lógica de cálculo do signo
├── schema.sql           # criação da tabela `submissions`
├── requirements.txt
└── templates/
    └── index.html       # front-end (fetch para /api/descobrir)
```

## Rotas da API

- `POST /api/descobrir` — recebe `{ "name": "...", "birthdate": "AAAA-MM-DD" }`,
  calcula o signo, salva a consulta no banco e devolve os dados do signo em JSON.
- `GET /api/historico` — devolve as 20 últimas consultas salvas (bom para
  conferir se o SQL está gravando certo).

## Trocando o SQLite por MySQL/Postgres

O projeto usa SQLite por ser zero-configuração. Para migrar:

1. Troque `sqlite3.connect(...)` em `app.py` pelo driver desejado
   (`psycopg2` para Postgres, `mysql-connector-python` para MySQL).
2. Ajuste `schema.sql` para a sintaxe do banco escolhido (ex.: `SERIAL` no
   lugar de `AUTOINCREMENT` no Postgres).
3. Se preferir um ORM, o SQLAlchemy funciona com qualquer um dos três bancos
   trocando só a connection string.
