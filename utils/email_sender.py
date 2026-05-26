import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "wolf10dra@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "xsyy xbcl rkoq esud")
FROM_EMAIL = os.environ.get("wolf10dra@gmail.com", SMTP_USER)


def send_reservation_email(client_email, client_name, data):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("Email SMTP no configurado. No se envió el correo.")
        return False

    subject = f"Confirmación de Reserva - {data.get('inmueble', '')}"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2e7d32;">¡Reserva Confirmada!</h2>
        <p>Hola <strong>{client_name}</strong>,</p>
        <p>Te confirmamos los detalles de tu reserva:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Inmueble:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('inmueble', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Fecha Ingreso:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('fecha_ingreso', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Fecha Egreso:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('fecha_egreso', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Noches:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('noches', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Valor por Día:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('valor_dia', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Costo Total:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('costo_total', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Costo con Descuento:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('costo_con_descuento', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Adelanto:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('adelanto', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px;"><strong>Pago Pendiente:</strong></td><td style="padding: 8px;">${data.get('pago_pendiente', 0):,.2f}</td></tr>
        </table>
        <br>
        <p style="color: #555;">Gracias por confiar en nosotros.</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = client_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, client_email, msg.as_string())
        print(f"Correo enviado a {client_email}")
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False


def send_quotation_email(client_email, client_name, data):
    """Envía un correo de cotización formal."""
    if not SMTP_USER or not SMTP_PASSWORD:
        return False

    subject = f"🏨 Presupuesto de Estadía - {data.get('inmueble', '')}"

    body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">Presupuesto de Estadía</h1>
            </div>
            <div style="padding: 30px;">
                <p>Hola <strong>{client_name}</strong>,</p>
                <p>Es un gusto saludarte. Tal como lo conversamos, te adjunto el presupuesto detallado para tu estadía:</p>
                
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">🏠 {data.get('inmueble', '')}</h3>
                    <p style="margin: 5px 0;">📅 <strong>Periodo:</strong> Del {data.get('fecha_ingreso', '')} al {data.get('fecha_egreso', '')}</p>
                    <p style="margin: 5px 0;">🌙 <strong>Noches:</strong> {data.get('noches', '')}</p>
                    <p style="margin: 5px 0;">📍 <strong>Ubicación:</strong> {data.get('ubicacion', 'Consultar')}</p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 18px; margin-bottom: 5px; color: #7f8c8d; text-decoration: line-through;">Total: {data.get('costo_total', '$0,00')}</p>
                    <p style="font-size: 28px; font-weight: bold; margin-top: 0; color: #e67e22;">Precio Final: {data.get('final_price', '$0,00')}</p>
                    <p style="font-size: 14px; color: #95a5a6;">(Promedio por noche: {data.get('final_per_night', '$0,00')})</p>
                </div>

                <p style="text-align: center; margin-top: 40px;">
                    <a href="https://wa.me/5492236689548?text=Hola!%20Quiero%20confirmar%20la%20reserva%20de%20{data.get('inmueble', '').replace(' ', '%20')}%20para%20las%20fechas%20{data.get('fecha_ingreso', '')}%20al%20{data.get('fecha_egreso', '')}" 
                       style="background-color: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">RESERVAR AHORA</a>
                </p>
                
                <p style="font-size: 13px; color: #95a5a6; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
                    * Este presupuesto tiene validez por 72 horas y está sujeto a disponibilidad al momento de confirmar.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = client_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, client_email, msg.as_string())
        return True
    except:
        return False
