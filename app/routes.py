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
            <img src="https://pypi.org/static/images/logo-small.8998e9d1.svg" alt="Python Package Index">
            <br>
            <a href="https://ortizol.blogspot.com">Blog de John Ortiz</a>
        </body>
    </html>
    """
    
    return contenido.format(nombre)
