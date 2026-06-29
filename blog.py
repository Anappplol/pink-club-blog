import json
import os
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

DB_USUARIOS = "usuarios.json"
DB_GRUPOS = "grupos.json"
DB_INVITACIONES = "invitaciones.json"
DB_AMIGOS = "amigos.json"
DB_CHATS = "chats_privados.json"

def cargar_datos(archivo, por_defecto):
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return por_defecto

def guardar_datos(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

usuarios = cargar_datos(DB_USUARIOS, {})
grupos = cargar_datos(DB_GRUPOS, {})
invitaciones = cargar_datos(DB_INVITACIONES, {})
amigos = cargar_datos(DB_AMIGOS, {})
chats_privados = cargar_datos(DB_CHATS, {})

usuario_actual = None
STICKERS = ["💖", "✨", "👑", "💅", "🦄", "🎀", "🌸", "🍕", "🧸", "🍰", "🍭", "👽", "🦋", "💘"]

ESTILO_BASE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pink Club Blog</title>
    <style>
        body { background-color: #FFC0CB; font-family: 'Arial', sans-serif; text-align: center; padding: 30px; }
        .titulo-brillante { background-color: #FF1493; color: #FFFF00; font-size: 50px; font-weight: bold; padding: 20px; display: inline-block; border-radius: 15px; box-shadow: 0px 0px 20px #FF1493; margin-bottom: 10px; }
        .caja { background-color: #FFF0F5; padding: 20px; border-radius: 10px; max-width: 550px; margin: 20px auto; border: 2px solid #FF69B4; text-align: left; }
        .caja h2, .caja h3 { text-align: center; color: #FF1493; }
        .caja-alerta { background-color: #FFFFE0; padding: 15px; border-radius: 10px; max-width: 550px; margin: 15px auto; border: 2px dashed #FF1493; }
        .btn { background-color: #FF69B4; color: white; border: none; padding: 8px 15px; font-size: 14px; font-weight: bold; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn-principal { background-color: #FF1493; }
        .btn-aceptar { background-color: #32CD32; }
        .btn-borrar { background-color: #DC3545; }
        .btn-sticker { background-color: transparent; font-size: 24px; border: none; cursor: pointer; padding: 5px; margin: 2px; transition: transform 0.2s; }
        .btn-sticker:hover { transform: scale(1.3); }
        input[type="text"], input[type="password"] { padding: 10px; width: 90%; margin: 10px auto; display: block; border: 1px solid #FF69B4; border-radius: 5px; }
        .alerta { color: red; font-weight: bold; text-align: center; }
        .exito { color: green; font-weight: bold; text-align: center; }
        .post { background: white; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 5px solid #FF1493; }
        .amiga-item { display: flex; justify-content: space-between; align-items: center; background: white; padding: 8px; margin: 5px 0; border-radius: 5px; border: 1px solid #FF69B4; }
        .zona-stickers { background: #FFE4E1; padding: 10px; border-radius: 8px; margin: 10px 0; border: 1px dashed #FF69B4; text-align: center; }
    </style>
</head>
<body>
    <div class="titulo-brillante">✨ PINK CLUB ✨</div>
    <p style="color: #FF1493; font-style: italic; font-size: 18px; text-align: center;">Solo para chicas geniales 💖</p>
    {% block contenido %}{% endblock %}
</body>
</html>
"""

@app.route('/')
def inicio():
    global usuario_actual
    usuario_actual = None
    error = request.args.get('error', '')
    msg = request.args.get('msg', '')
    html = ESTILO_BASE.replace("{% block contenido %}{% endblock %}", f"""
    <div class="caja">
        <h2>Entrar al Club 🎀</h2>
        {"<p class='alerta'>" + error + "</p>" if error else ""}
        {"<p class='exito'>" + msg + "</p>" if msg else ""}
        <form action="/login" method="POST">
            <input type="text" name="user" placeholder="Tu Username" required>
            <input type="password" name="pas" placeholder="Tu Contraseña" required>
            <button class="btn btn-principal" type="submit" style="display:block; margin: 10px auto;">Iniciar Sesión 🔐</button>
        </form>
        <hr style="border: 1px solid #FFC0CB;">
        <h3>¿Eres nueva? Regístrate rápido</h3>
        <form action="/registro" method="POST">
            <input type="text" name="user" placeholder="Elige Username" required>
            <input type="password" name="pas" placeholder="Elige Contraseña" required>
            <button class="btn" type="submit" style="display:block; margin: 10px auto;">Crear Cuenta ✨</button>
        </form>
    </div>
    """)
    return render_template_string(html)

@app.route('/registro', methods=['POST'])
def registro():
    user = request.form['user'].strip()
    pas = request.form['pas']
    if user.lower() in [u.lower() for u in usuarios.keys()]:
        return redirect('/?error=Ese username ya existe. ¡Elige otro único!')
    usuarios[user] = pas
    invitaciones[user] = []
    amigos[user] = []
    guardar_datos(DB_USUARIOS, usuarios)
    guardar_datos(DB_INVITACIONES, invitaciones)
    guardar_datos(DB_AMIGOS, amigos)
    return redirect('/?msg=Cuenta creada con exito!')

@app.route('/login', methods=['POST'])
def login():
    global usuario_actual
    user = request.form['user'].strip()
    pas = request.form['pas']
    if user in usuarios and usuarios[user] == pas:
        usuario_actual = user
        return redirect('/dashboard')
    return redirect('/?error=Usuario o contraseña incorrectos')

@app.route('/dashboard')
def dashboard():
    if not usuario_actual: return redirect('/')
    mis_clubs = [g for g, d in grupos.items() if d['creadora'] == usuario_actual or usuario_actual in d['miembros']]
    mis_invitaciones = list(invitaciones.get(usuario_actual, []))
    mis_amigas = list(amigos.get(usuario_actual, []))
    html = ESTILO_BASE.replace("{% block contenido %}{% endblock %}", """
    {% if solicitudes %}
    <div class="caja-alerta">
        <h3>💌 ¡Tienes invitaciones en tu buzón!</h3>
        {% for club in solicitudes %}
            <p>Te invitaron al club <strong>{{club}}</strong></p>
            <form action="/aceptar/{{club}}" method="POST" style="display:inline;">
                <button class="btn btn-aceptar" type="submit">Aceptar 🎀</button>
            </form>
        {% endfor %}
    </div>
    {% endif %}
    <div class="caja">
        <h2>Hola, <span style="color: #FF1493;">{{usuario}}</span> 💕</h2>
        <div style="text-align: center;"><a href="/"><button class="btn" style="background-color: #8B0000;">Cerrar Sesión 🚪</button></a></div>
        <h3>👭 Mis Amigas</h3>
        {% if not lista_amigas %}
            <p style="text-align:center; color: gray;">Aún no tienes amigas agregadas.</p>
        {% else %}
            {% for amiga in lista_amigas %}
                <div class="amiga-item">
                    <span>👑 <strong>{{amiga}}</strong></span>
                    <div>
                        <a href="/chat/{{amiga}}"><button class="btn btn-principal">Chatear 💬</button></a>
                        <a href="/borrar-amiga/{{amiga}}"><button class="btn btn-borrar">Borrar ❌</button></a>
                    </div>
                </div>
            {% endfor %}
        {% endif %}
        <hr style="border: 1px solid #FFC0CB;">
        <h3>Mis Clubs 🌸</h3>
        {% if not clubs %}
            <p style="text-align:center;">No estás en ningún club todavía.</p>
        {% else %}
            {% for c in clubs %}
                <p>🌸 <a href="/grupo/{{c}}" style="color: #FF1493; font-weight: bold; font-size: 18px;">Club: {{c}}</a></p>
            {% endfor %}
        {% endif %}
        <hr style="border: 1px solid #FFC0CB;">
        <h3>Crear un Nuevo Club ➕</h3>
        <form action="/crear-grupo" method="POST">
            <input type="text" name="nombre_g" placeholder="Nombre del Club" required>
            <button class="btn btn-principal" type="submit" style="display:block; margin: 10px auto;">Fundar Club 💅</button>
        </form>
    </div>
    """)
    return render_template_string(html, usuario=usuario_actual, clubs=mis_clubs, solicitudes=mis_invitaciones, lista_amigas=mis_amigas)

@app.route('/crear-grupo', methods=['POST'])
def crear_grupo():
    if not usuario_actual: return redirect('/')
    nombre_g = request.form['nombre_g'].strip()
    if nombre_g and nombre_g not in grupos:
        grupos[nombre_g] = {"creadora": usuario_actual, "miembros": [], "posts": []}
        guardar_datos(DB_GRUPOS, grupos)
    return redirect('/dashboard')

@app.route('/grupo/<nombre>')
def grupo(nombre):
    if not usuario_actual or nombre not in grupos: return redirect('/')
    g = grupos[nombre]
    html = ESTILO_BASE.replace("{% block contenido %}{% endblock %}", """
    <div class="caja">
        <h2>🔮 Club: {{nombre}}</h2>
        <div style="text-align: center;"><a href="/dashboard"><button class="btn">⬅ Volver al Panel</button></a></div>
        <hr style="border: 1px solid #FFC0CB;">
        <h3>Invitar Amiga por Username 👥</h3>
        <form action="/invitar/{{nombre}}" method="POST">
            <input type="text" name="invitada" placeholder="Username de tu amiga" required>
            <button class="btn btn-principal" type="submit" style="display:block; margin: 10px auto;">Enviar al Buzón 📬</button>
        </form>
        <hr style="border: 1px solid #FFC0CB;">
        <h3>Muro del Blog 📝</h3>
        <form action="/post/{{nombre}}" method="POST">
            <input type="text" name="texto" placeholder="¿Qué quieres contar hoy?" required>
            <button class="btn btn-principal" type="submit" style="display:block; margin: 10px auto;">Publicar Post ✨</button>
        </form>
        <div style="margin-top: 20px;">
            {% for p in posts %}
                <div class="post">{{p}}</div>
            {% endfor %}
        </div>
    </div>
    """)
    return render_template_string(html, nombre=nombre, posts=reversed(g['posts']))

@app.route('/invitar/<nombre>', methods=['POST'])
def invitar(nombre):

