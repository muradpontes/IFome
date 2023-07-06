import json, ssl
import sqlite3
from flask import Flask, render_template, request, session, jsonify, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = '10d5a0555a83f8bb41290c1e14e603e3' #frango MD5 hash
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'

def from_json(value):
    return json.loads(value)

app.jinja_env.filters['from_json'] = from_json

def get_db_connection():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

def verificar_login(login, senha):
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM usuario WHERE nome = ?", (login,))
    usuario = cursor.fetchone()
    conn.close()
    if usuario and usuario['senha'] == senha:
        return True
    return False

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['login']
        senha = request.form['senha']

        if verificar_login(usuario, senha):
            conn = get_db_connection()
            pedidos = conn.execute('SELECT * FROM pedido').fetchall()

            conn.close()
            return render_template('admin.html', pedidos=pedidos, usuario=usuario)

        else:
            return render_template('login.html', erro="Nome ou senha incorretos.")

    return render_template('login.html')

@app.route('/admin')
def admin():

    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM pedido').fetchall()

    pedidos = [json.dumps(dict(row)) for row in rows]

    conn.close()
    return render_template('admin.html', pedidos=pedidos)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['nome'] = request.form['nome']
        session['semestre'] = int(request.form['semestre'])

        return render_template('pedido.html', nome=session['nome'], semestre=session['semestre'])

    return render_template('index.html')

@app.route('/pedido', methods=['GET', 'POST'])
def pedido():

    cupons = {
        "CUPOM20": 0.2,
        "CUPOM10": 0.1,
        "CUPOM30": 0.3
    }

    if request.method == 'POST':
        nome = session.get('nome')
        semestre = session.get('semestre')
        salgados = ['coxinha', 'pastel_carne', 'pastel_frango', 'pastel_queijo', 'enroladinho']
        descricao = []

        total = 0.0
            
        for salgado, quantidade in request.form.items():
            if salgado in salgados:
                quantidade = int(quantidade)
                if quantidade > 0:
                    preco_salgado = 2.0
                    total_salgado = preco_salgado * quantidade
                    total += total_salgado
                    descricao.append({
                        'salgado': salgado,
                        'quantidade': quantidade
                    })

        session['total'] = total
        session['descricao_json'] = descricao

        cupom = request.form.get('cupom')

        if cupom:
            if cupom in cupons:
                desconto = cupons[cupom]
                valor_desconto = total * desconto
                total -= valor_desconto
                flash('Cupom aplicado com sucesso!', 'flash-success')
            else:
                flash('Cupom inválido.', 'flash-error')

        total_pedido = "{:.2f}".format(total)

        session['total'] = total_pedido
        descricao_json = json.dumps(descricao)

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO pedido (nome, semestre, descricao, total) VALUES (?, ?, ?, ?)",
            (nome, semestre, descricao_json, total))
        conn.commit()
        conn.close()

        return render_template('checkout.html', total=total, descricao_json=descricao, flash=flash)

    return render_template('pedido.html', salgados=salgados)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')