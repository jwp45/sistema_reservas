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
