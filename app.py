from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from flask import session
app = Flask(__name__)

app.secret_key = "vitaloop2026"

# CONFIGURACIÓN MYSQL.
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'vitaloop_user'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'vitaloop'
mysql = MySQL(app)

app.config['IMG_FOLDER'] = os.path.join(app.root_path, 'static', 'img')

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM usuarios WHERE correo=%s AND password=%s",
            (correo, password)
        )

        user = cur.fetchone()

        cur.close()

        if user:

            session["usuario_id"] = user[0]
            session["nombre"] = user[1]
            session["correo"] = user[3]

            return redirect(url_for("inicio"))

        else:
            return "Usuario o contraseña incorrectos"

    return render_template("login.html")
    

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        correo = request.form["correo"]
        usuario = request.form["usuario"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuarios(nombre, apellido, correo, usuario, password)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, correo, usuario, password))

        mysql.connection.commit()
        cur.close()

        return "Usuario registrado correctamente"

    return render_template("registro.html")
@app.route("/inicio")
def inicio():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM donaciones")

    donaciones = cur.fetchall()

    cur.close()

    return render_template(
        "inicio.html",
        donaciones=donaciones
    )



@app.route("/publicar", methods=["GET", "POST"])
def publicar():
    if request.method == "POST":

        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']

        usuario_id = session["usuario_id"]

        imagen = request.files.get('imagen')

        if imagen and imagen.filename != "":
            filename = secure_filename(imagen.filename)
            ruta = os.path.join(app.config['IMG_FOLDER'], filename)
            imagen.save(ruta)
            ruta_db = f"img/{filename}"
        else:
            ruta_db = None

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO donaciones
            (usuario_id, titulo, descripcion, tipo, estado, imagen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, titulo, descripcion, tipo, "activa", ruta_db))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('inicio'))

    return render_template("publicidad_donaciones.html")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if request.method == "POST":

        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        tipo = request.form["tipo"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE donaciones
            SET titulo=%s,
                descripcion=%s,
                tipo=%s
            WHERE id=%s
        """, (titulo, descripcion, tipo, id))

        mysql.connection.commit()

        return redirect(url_for("inicio"))

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM donaciones WHERE id=%s", (id,))
    donacion = cursor.fetchone()

    return render_template("editar.html", donacion=donacion)

@app.route("/eliminar/<int:id>")
def eliminar(id):

    cursor = mysql.connection.cursor()

    cursor.execute("DELETE FROM donaciones WHERE id=%s", (id,))

    mysql.connection.commit()

    cursor.close()

    return redirect(url_for("inicio"))

@app.route("/perfil")
def perfil():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT nombre,
            apellido,
            correo,
            usuario,
            foto,
            telefono,
            provincia,
            municipio,
            biografia
        FROM usuarios
        WHERE id=%s
    """, (session["usuario_id"],))

    usuario = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*)
        FROM donaciones
        WHERE usuario_id=%s
    """, (session["usuario_id"],))

    total_publicaciones = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "perfil.html",
        usuario=usuario,
        publicaciones=total_publicaciones
    )
@app.route("/mis_donaciones")
def mis_donaciones():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()

    # Donaciones del usuario
    cursor.execute("""
        SELECT id,
            titulo,
            descripcion,
            tipo,
            fecha_creacion,
            estado,
            imagen
        FROM donaciones
        WHERE usuario_id=%s
        ORDER BY fecha_creacion DESC
    """, (session["usuario_id"],))

    donaciones = cursor.fetchall()

    # Total
    cursor.execute("""
        SELECT COUNT(*)
        FROM donaciones
        WHERE usuario_id=%s
    """, (session["usuario_id"],))

    total = cursor.fetchone()[0]

    # Activas
    cursor.execute("""
        SELECT COUNT(*)
        FROM donaciones
        WHERE usuario_id=%s
        AND estado='activa'
    """, (session["usuario_id"],))

    activas = cursor.fetchone()[0]

    # Reservadas
    cursor.execute("""
        SELECT COUNT(*)
        FROM donaciones
        WHERE usuario_id=%s
        AND estado='reservada'
    """, (session["usuario_id"],))

    reservadas = cursor.fetchone()[0]

    # Entregadas
    cursor.execute("""
        SELECT COUNT(*)
        FROM donaciones
        WHERE usuario_id=%s
        AND estado='entregada'
    """, (session["usuario_id"],))

    entregadas = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "mis_donaciones.html",
        donaciones=donaciones,
        total=total,
        activas=activas,
        reservadas=reservadas,
        entregadas=entregadas
    )
    
@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        correo = request.form["correo"]
        usuario = request.form["usuario"]
        telefono = request.form["telefono"]
        provincia = request.form["provincia"]
        municipio = request.form["municipio"]
        biografia = request.form["biografia"]

        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s,
                apellido=%s,
                correo=%s,
                usuario=%s,
                telefono=%s,
                provincia=%s,
                municipio=%s,
                biografia=%s
            WHERE id=%s
        """, (
            nombre,
            apellido,
            correo,
            usuario,
            telefono,
            provincia,
            municipio,
            biografia,
            session["usuario_id"]
        ))

        mysql.connection.commit()

        cursor.close()

        return redirect(url_for("perfil"))

    cursor.execute("""
        SELECT nombre,
            apellido,
            correo,
            usuario,
            telefono,
            provincia,
            municipio,
            biografia
        FROM usuarios
        WHERE id=%s
    """, (session["usuario_id"],))

    usuario = cursor.fetchone()

    cursor.close()

    return render_template(
        "editar_perfil.html",
        usuario=usuario
    )   
    
@app.route("/solicitar/<int:donacion_id>")
def solicitar(donacion_id):

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    cursor = mysql.connection.cursor()

    # Buscar el dueño de la donación
    cursor.execute("""
        SELECT usuario_id
        FROM donaciones
        WHERE id=%s
    """, (donacion_id,))

    donacion = cursor.fetchone()

    if not donacion:
        cursor.close()
        return "La donación no existe."

    propietario = donacion[0]

    # Evitar solicitar una donación propia
    if propietario == session["usuario_id"]:
        cursor.close()
        return "No puedes solicitar tu propia donación."

    # Verificar si ya existe una solicitud
    cursor.execute("""
        SELECT id
        FROM solicitudes
        WHERE donacion_id=%s
        AND solicitante_id=%s
    """, (donacion_id, session["usuario_id"]))

    existe = cursor.fetchone()

    if existe:
        cursor.close()
        return "Ya enviaste una solicitud para esta donación."

    # Guardar la solicitud
    cursor.execute("""
        INSERT INTO solicitudes
        (donacion_id, solicitante_id, mensaje)
        VALUES (%s,%s,%s)
    """, (
        donacion_id,
        session["usuario_id"],
        ""
    ))

    mysql.connection.commit()

    cursor.close()

    return redirect(url_for("inicio"))
    
    

if __name__ == "__main__":
    app.run(debug=True)