from flask import render_template

from app import app


@app.route("/")
def index():
    return render_template("index.html", titulo='Inicio', nombre='Alex')

@app.route("/hola/<nombre>")
def hola(nombre):
    return render_template("hola.html", titulo='Hola', nombre=nombre)


@app.route('/lenguajes-programacion')
def lenguajes_programacion():
    lenguajes = ['Python', 'Java', 'JavaScript', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin']
    return render_template('lenguajes.html', titulo='Lenguajes de programación', lenguajes=lenguajes)
