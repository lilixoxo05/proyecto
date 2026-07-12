from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

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
        cur.execute("SELECT * FROM usuarios WHERE correo=%s AND password=%s",
                    (correo, password))
        user = cur.fetchone()
        cur.close()

        if user:
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM donaciones")
    donaciones = cur.fetchall()
    cur.close()

    return render_template("inicio.html", donaciones=donaciones)

@app.route("/publicar", methods=["GET", "POST"])
def publicar():
    if request.method == "POST":

        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        tipo = request.form['tipo']

        usuario_id = 1  # temporal

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


if __name__ == "__main__":
    app.run(debug=True)