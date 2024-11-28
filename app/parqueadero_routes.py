from datetime import datetime
import io
import os
import tempfile

from flask import Blueprint, g, flash, jsonify, render_template, request, url_for, redirect, send_file
from flask_login import current_user, login_required

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import qrcode

from app.forms import ParqueaderoInformacionForm
from app.models import Arrendamiento, MedioPago, Modulo, Parqueadero, Parqueo, Periodicidad, Tarifa, Usuario, Vehiculo, VehiculoTipo

from app import db
from app.routes import propietario_admin_permission, operario_permission
from app.routes import todos_permiso, propietario_permission
from app.util.utilitarios import to_json


class ParqueaderoRoutes:
    """
    Clase que gestiona las rutas de los parqueaderos.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('parqueadero', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/parqueadero", methods=['POST'])
        @login_required
        @propietario_permission.require(http_exception=403)
        def parqueadero():
            """
            Crea un nuevo parqueadero.

            :return: Respuesta JSON.
            """
            try:
                data = request.get_json()
                entidad = Parqueadero(
                    rut=data.get('rut'),
                    nombre=data.get('nombre'),
                    direccion=data.get('direccion'),
                    email=data.get('email'),
                    ciudad=data.get('ciudad'),
                    telefono=data.get('telefono'),
                    usuario_id=data.get('usuarioId'),
                    pais_id=data.get('paisId')
                )

                db.session.add(entidad)
                db.session.commit()

                return jsonify({'status': 'success', 'message': 'Parqueadero creado', 'data': {
                    'id': entidad.id,
                    'nombre': entidad.nombre,
                    'direccion': entidad.direccion,
                    'telefono': entidad.telefono,
                    'email': entidad.email,
                    'pais_id': entidad.pais_id,
                    'usuario_id': entidad.usuario_id
                }}), 201

            except Exception as e:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': str(e)}), 500


        @self.blueprint.route('/parqueadero-informacion', methods=['GET', 'POST'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
        def parqueadero_informacion():
            """
            Muestra la información del parqueadero.

            :return: Plantilla HTML.
            """
            g.template_name = 'base.html'
            
            parqueadero = Parqueadero.query.filter_by(usuario_id=current_user.parqueadero_id).first()

            form = ParqueaderoInformacionForm(obj=parqueadero)

            if form.validate_on_submit():
                form.populate_obj(parqueadero)
                db.session.commit()
                flash('Información del parqueadero actualizada correctamente.', 'parqueadero-informacion-success')
                return redirect(url_for('parqueadero_informacion'))
            
            return render_template('parqueadero-informacion.html', titulo='Información del Parqueadero', form=form)

        @self.blueprint.route('/periodicidades', methods=['GET'])
        @login_required
        @todos_permiso.require(http_exception=403)
        def periodicidades():
            """
            Muestra las periodicidades.

            :return: Respuesta JSON.
            """
            parqueadero_id = current_user.parqueadero_id
            parqueadero = Parqueadero.query.filter_by(id=parqueadero_id).first()
            periodicidades = Periodicidad.query.filter_by(parqueadero_id=parqueadero.id).all()

            return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
                'id': entidad.id,
                'nombre': entidad.nombre,
                'dias': entidad.dias
            } for entidad in periodicidades]}), 200


        @self.blueprint.route('/parqueos', methods=['GET'])
        @login_required
        @operario_permission.require(http_exception=403)
        def parqueos():
            """
            Muestra la lista de parqueos.
            """
            g.template_name = 'base.html'
            sedes = [sede.sede for sede in current_user.sedes]
            tipos_vehiculos = VehiculoTipo.query.all()
            tipos_vehiculos_json = [to_json(tipo_vehiculo) for tipo_vehiculo in tipos_vehiculos]
            medios_pago = MedioPago.query.all()
            medios_pago = [to_json(medio_pago) for medio_pago in medios_pago]
            tarifas = Tarifa.query.all()
            tarifas = [to_json(tarifa) for tarifa in tarifas]

            return render_template('parqueos.html', titulo='Parqueos', sedes=sedes, tipos_vehiculos=tipos_vehiculos_json, medios_pago=medios_pago, tarifas=tarifas)


        @self.blueprint.route('/vehiculo/buscar/<placa>', methods=['GET'])
        @login_required
        def buscar_vehiculo(placa):
            """
            Busca un vehículo por placa.

            :param placa: Placa del vehículo.

            :return: Respuesta JSON.
            """
            vehiculo = Vehiculo.query.filter_by(placa=placa).first()

            if vehiculo is None:
                return jsonify({'status': 'failure', 'message': 'No existe un vehículo con la placa indicada.'}), 200

            return jsonify({
                'status': 'success',
                'data': {
                    'id': vehiculo.id,
                    'placa': vehiculo.placa,
                    'marca': vehiculo.marca,
                    'modelo': vehiculo.modelo,
                    'tipo': vehiculo.vehiculo_tipo.nombre,
                    'vehiculoTipoId': vehiculo.vehiculo_tipo.id,
                    'disponible': vehiculo.disponible
                }
            })


        @self.blueprint.route('/parqueo/ingresar', methods=['POST'])
        @login_required
        @operario_permission.require(http_exception=403)
        def ingresar_parqueo():
            """
            Ingresa un vehículo al parqueadero.

            :return: Respuesta JSON.
            """
            try:
                data = request.get_json()
                modulo_id = data.get('moduloId')

                modulo_ocupado = Parqueo.query.filter_by(modulo_id=modulo_id, fecha_hora_salida=None).first()

                if modulo_ocupado is not None:
                    return jsonify({'status': 'warning', 'message': 'El módulo seleccionado se encuentra ocupado'}), 200

                modulo = Modulo.query.get(modulo_id)
                placa = data.get('placa')
                vehiculo = Vehiculo.query.filter_by(placa=placa).first()

                tipo_vehiculo = VehiculoTipo.query.get(data.get('vehiculoTipoId'))
                tipo_vehiculo = {
                    'id': tipo_vehiculo.id,
                    'nombre': tipo_vehiculo.nombre
                }

                if vehiculo is not None:

                    tarifa = Tarifa.query.get(vehiculo.tarifa_id)
                    tipo_vehiculo['tarifa'] = {
                        'id': tarifa.id,
                        'nombre': tarifa.nombre,
                        'costo': tarifa.costo
                    }

                    parqueo = Parqueo.query.filter_by(vehiculo_id=vehiculo.id, fecha_hora_salida=None).first()

                    if parqueo is not None:
                        return jsonify({'status': 'warning', 'message': 'El vehículo ya se encuentra en el parqueadero'}), 200
                    
                if vehiculo is not None:
                    fecha_actual = datetime.now()
                    
                    arrendamiento = Arrendamiento.query.filter_by(vehiculo_id=vehiculo.id).order_by(Arrendamiento.fecha_fin.desc()).first()

                    if arrendamiento is not None:
                        if fecha_actual > arrendamiento.fecha_fin:
                            return jsonify({'status': 'warning', 'message': 'El arrendamiento del vehículo ha finalizado'}), 200
                        
                        if arrendamiento.ha_sido_pausado:
                            return jsonify({'status': 'warning', 'message': 'El arrendamiento del vehículo se encuentra en pausa'}), 200
                        
                        parqueo = Parqueo(
                            vehiculo_id=vehiculo.id,
                            modulo_id=modulo.id,
                        )

                        tarifa = Tarifa.query.get(arrendamiento.tarifa_id)

                        db.session.add(parqueo)
                        db.session.commit()

                        return jsonify({'status': 'arrendamiento', 'message': 'El vehículo cuenta con un arrendamiento activo. Puede ingresar al parqueadero.', 'tipoVehiculo': tipo_vehiculo, 'tarifa': tarifa}), 200


                if vehiculo is None:
                    vehiculo_tipo_id = data.get('vehiculoTipoId')
                    vehiculo = Vehiculo(
                        placa=placa,
                        vehiculo_tipo_id=vehiculo_tipo_id,
                        tarifa_id=data.get('tarifaId'),
                    )

                    tarifa = Tarifa.query.get(data.get('tarifaId'))
                    tipo_vehiculo['tarifa'] = {
                        'id': tarifa.id,
                        'nombre': tarifa.nombre,
                        'costo': tarifa.costo
                    }

                    db.session.add(vehiculo)
                    db.session.flush()
                
                parqueo = Parqueo(
                    vehiculo_id=vehiculo.id,
                    modulo_id=modulo.id,
                )

                db.session.add(parqueo)

                db.session.commit()

                return jsonify({'status': 'success', 'message': 'Vehículo ingresado al parqueadero', 'data': {
                    'tipoVehiculo': tipo_vehiculo
                }}), 200
            except Exception as e:
                print('Error:', e)
                db.session.rollback()
                return jsonify({'status': 'error', 'message': str(e)}), 500


        @self.blueprint.route('/parqueo/vehiculo/retirar', methods=['POST'])
        def retirar_vehiculo():
            data = request.get_json()
            placa = data.get('placa')
            total_pagado = data.get('totalPagado')
            medio_pago_id = data.get('metodoPagoId')
            es_arrendamiento = data.get('esArrendamiento')

            vehiculo = Vehiculo.query.filter_by(placa=placa).first()
            if not vehiculo:
                return jsonify({'status': 'error', 'message': 'Vehículo no encontrado'}), 404

            parqueo = Parqueo.query.filter_by(vehiculo_id=vehiculo.id, fecha_hora_salida=None).first()
            if not parqueo:
                return jsonify({'status': 'error', 'message': 'Parqueo no encontrado o ya retirado'}), 404

            parqueo.fecha_hora_salida = datetime.now()
            if not es_arrendamiento:
                parqueo.total_pagado = total_pagado
                parqueo.metodo_pago_id = medio_pago_id

            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Vehículo retirado exitosamente'}), 200


        @self.blueprint.route('/usuario/activar-desactivar/<documento>', methods=['PUT'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
        def activar_desactivar_usuario(documento):
            """
            Activa o desactiva un usuario.

            :param documento: Documento del usuario.
            :return: Respuesta JSON.
            """
            usuario = Usuario.query.filter_by(documento=documento).first()
            if not usuario:
                return jsonify({'status': 'error', 'message': 'Usuario no encontrado'}), 404

            usuario.activo = not usuario.activo

            db.session.commit()

            estado = 'activado' if usuario.activo else 'desactivado'
            return jsonify({'status': 'success', 'message': f'Usuario {estado} exitosamente'}), 200


        @self.blueprint.route('/vehiculo/<string:placa>/cliente', methods=['GET'])
        @login_required
        @todos_permiso.require(http_exception=403)
        def buscar_cliente_por_placa(placa):
            """
            Busca un cliente por placa de vehículo.

            :param placa: Placa del vehículo.
            :return: Respuesta JSON.
            """
            vehiculo = Vehiculo.query.filter_by(placa=placa).first()
            if not vehiculo:
                return jsonify({'status': 'error', 'message': 'Vehículo no encontrado'}), 404

            cliente = vehiculo.cliente
            if not cliente:
                return jsonify({'status': 'error', 'message': 'Cliente no encontrado'}), 404

            return jsonify({
                'status': 'success',
                'data': {
                    'documento': cliente.documento,
                    'nombres': cliente.nombres,
                    'apellidos': cliente.apellidos,
                    'email': cliente.email,
                    'telefono': cliente.telefono,
                    'direccion': cliente.direccion,
                    'activo': cliente.activo
                }
            })


        @self.blueprint.route('/vehiculo/<string:placa>', methods=['PUT'])
        @login_required
        @todos_permiso.require(http_exception=403)
        def editar_vehiculo(placa):
            """
            Edita un vehículo.

            :param placa: Placa del vehículo.
            :return: Respuesta JSON.
            """
            data = request.get_json()
            vehiculo = Vehiculo.query.filter_by(placa=placa).first()
            if not vehiculo:
                return jsonify({'status': 'error', 'message': 'Vehículo no encontrado'}), 404

            vehiculo.marca = data.get('marca')
            vehiculo.modelo = data.get('modelo')
            vehiculo.vehiculo_tipo_id = data.get('vehiculoTipoId')

            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Vehículo editado exitosamente'}), 200


        @self.blueprint.route('/generar_ticket/<string:placa>', methods=['GET'])
        def generar_ticket(placa):
            """
            Genera un ticket de parqueadero.
            """
            
            parqueadero = Parqueadero.query.filter_by(usuario_id=current_user.parqueadero_id).first()
            vehiculo = Vehiculo.query.filter_by(placa=placa).first()

            tarifa = vehiculo.tarifa
            tarifa_costo = tarifa.costo
            tarifa_unidad_tiempo = tarifa.tarifa_tipo.nombre

            nombre_parqueadero = parqueadero.nombre
            registro_comercial = f'Registro comercial: {parqueadero.rut}'
            costo_servicio = f'{tarifa_costo} por {tarifa_unidad_tiempo}'
            nombre_atendedor = f'{current_user.nombres} {current_user.apellidos}'
            condiciones_servicio = "Este servicio no se hace responsable por objetos dejados dentro del vehículo."

            ticket_width = 8 * cm
            ticket_height = 12 * cm

            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(ticket_width, ticket_height))
            ancho, alto = ticket_width, ticket_height

            logo_path = os.path.join('app', 'static', 'images', 'logo-generico.png')
            c.drawImage(logo_path, (ancho - 64) / 2, alto - 64, width=64, height=64, mask='auto')

            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(ancho / 2, alto - 85, nombre_parqueadero)

            c.setFont("Helvetica", 9)
            y_position = alto - 100
            line_spacing = 12

            c.drawString(0.5 * cm, y_position, f"Registro Comercial: {registro_comercial}")
            y_position -= line_spacing
            c.drawString(0.5 * cm, y_position, f"Fecha/Hora de Ingreso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            y_position -= line_spacing
            c.drawString(0.5 * cm, y_position, f"Placa del Vehículo: {placa}")

            y_position -= line_spacing * 1.5
            c.setFont("Helvetica-Bold", 9)
            c.drawString(0.5 * cm, y_position, "Detalles del Servicio")
            y_position -= line_spacing
            c.setFont("Helvetica", 9)
            c.drawString(0.5 * cm, y_position, f"Costo: ${costo_servicio}")
            y_position -= line_spacing
            c.drawString(0.5 * cm, y_position, f"Atendido por: {nombre_atendedor}")

            qr_data = f"""
            Nombre del Parqueadero: {nombre_parqueadero}
            Registro Comercial: {registro_comercial}
            Fecha/Hora de Ingreso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Placa del Vehículo: {placa}
            Costo por unidad de tiempo: $ {costo_servicio}
            Atendido por: {nombre_atendedor}
            Condiciones: {condiciones_servicio}
            """
            qr = qrcode.make(qr_data)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_qr_file:
                qr.save(temp_qr_file.name)
                qr_path = temp_qr_file.name

            c.drawImage(qr_path, ancho - 2.5 * cm, alto - 11.5 * cm, width=2 * cm, height=2 * cm)

            # Condiciones del servicio
            y_position -= line_spacing * 2
            c.setFont("Helvetica-Bold", 9)
            c.drawString(0.5 * cm, y_position, "Condiciones del Servicio:")
            y_position -= line_spacing

            styles = getSampleStyleSheet()
            style = styles['Normal']
            style.fontName = 'Helvetica'
            style.fontSize = 7
            style.leading = 10

            paragraph = Paragraph(condiciones_servicio, style)

            width, height = paragraph.wrap(ticket_width - 20, 0)

            c.setFont("Helvetica", 7)
            text = c.beginText(0.5 * cm, y_position)
            text.setTextOrigin(0.5 * cm, y_position)
            text.setLeading(10)
            text.setFont("Helvetica", 7)

            paragraph.drawOn(c, 0.5 * cm, y_position - height)

            c.showPage()
            c.save()

            pdf_buffer.seek(0)
            os.remove(qr_path)

            fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"ticket_parqueadero_{fecha_hora}.pdf"

            return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=nombre_archivo)
