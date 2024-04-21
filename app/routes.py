from app import app


@app.route("/")
def hello():
    return "¡Hola a todos!"


@app.route('/otro-saludo')
def otro_saludo():
    return 'Hello!'


@app.route('/saludo/<nombre>')
def saludo(nombre):

    contenido = """
    <html>
        <head>
            <title>Saludo</title>
        </head>
        <body>
            <h1>¡Hola, {}!</h1>
        </body>
    </html>
    """
    
    return contenido.format(nombre)
