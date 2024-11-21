from vehiculo_tipo_routes import VehiculoTipoRoutes


def register_routes(app):
    vehiculo_tipo_routes = VehiculoTipoRoutes()

    app.register_blueprint(vehiculo_tipo_routes.blueprint, url_prefix='/api')
