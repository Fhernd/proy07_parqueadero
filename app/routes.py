from app import app


@app.route("/")
def hello():
    return "¡Hola a todos!"


@app.route('/otro-saludo')
def otro_saludo():
    return 'Hello!'


@app.route('/saludo/<nombre>')
def saludo(nombre):
    return '¡Hola, {}!'.format(nombre)
