from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html")

@app.route("/publicar")
def publicar():
    return render_template("publicidad_donaciones.html")

if __name__ == "__main__":
    app.run(debug=True)