from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import qrcode
from datetime import datetime

def generar_ticket(nombre_parqueadero, registro_comercial, placa, costo_servicio, nombre_atendedor, condiciones_servicio):
    # Configuración del PDF
    nombre_archivo = "ticket_parqueadero.pdf"
    c = canvas.Canvas(nombre_archivo, pagesize=A4)
    ancho, alto = A4

    # Logo del parqueadero (ejemplo: asegúrate de tener el logo en la misma carpeta o proporciona una ruta correcta)
    c.drawImage("app/static/images/logo-generico.png", 2 * cm, alto - 3 * cm, width=4 * cm, height=4 * cm)  # Ajusta la ruta y el tamaño según necesites

    # Información del parqueadero
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, alto - 4.5 * cm, nombre_parqueadero)
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, alto - 5.5 * cm, f"Registro Comercial: {registro_comercial}")
    c.drawString(2 * cm, alto - 6.5 * cm, f"Fecha/Hora de Ingreso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(2 * cm, alto - 7.5 * cm, f"Placa del Vehículo: {placa}")

    # Detalles del servicio
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, alto - 9 * cm, "Detalles del Servicio")
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, alto - 10 * cm, f"Costo por unidad de tiempo: S/ {costo_servicio}")
    c.drawString(2 * cm, alto - 11 * cm, f"Atendido por: {nombre_atendedor}")

    # Condiciones del servicio
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, alto - 12.5 * cm, "Condiciones del Servicio:")
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, alto - 13.5 * cm, condiciones_servicio)

    # Generar el código QR con la información sin el logo
    qr_data = f"""
    Nombre del Parqueadero: {nombre_parqueadero}
    Registro Comercial: {registro_comercial}
    Fecha/Hora de Ingreso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Placa del Vehículo: {placa}
    Costo por unidad de tiempo: S/ {costo_servicio}
    Atendido por: {nombre_atendedor}
    Condiciones: {condiciones_servicio}
    """
    qr = qrcode.make(qr_data)
    qr.save("codigo_qr.png")

    # Agregar el código QR al PDF
    c.drawImage("codigo_qr.png", 14 * cm, alto - 15 * cm, width=5 * cm, height=5 * cm)

    # Finalizar y guardar el PDF
    c.showPage()
    c.save()
    print(f"Ticket guardado como {nombre_archivo}")

# Datos de ejemplo
nombre_parqueadero = "Parqueadero Central"
registro_comercial = "RUC: 20600431065"
placa = "ABC-123"
costo_servicio = "5.00"
nombre_atendedor = "Juan Pérez"
condiciones_servicio = "Este servicio no se hace responsable por objetos dejados dentro del vehículo."

generar_ticket(nombre_parqueadero, registro_comercial, placa, costo_servicio, nombre_atendedor, condiciones_servicio)
