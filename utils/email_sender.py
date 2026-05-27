import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from controllers.database import Database

def get_smtp_config():
    db = Database()
    config = None
    if db.connect():
        config = db.get_config()
        if db.connection:
            db.connection.close()
    
    if config:
        return config
    # Fallback a variables de entorno o valores por defecto
    return {
        "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
        "smtp_user": os.environ.get("SMTP_USER", "wolf10dra@gmail.com"),
        "smtp_password": os.environ.get("SMTP_PASSWORD", "xsyy xbcl rkoq esud"),
        "from_email": os.environ.get("FROM_EMAIL", "wolf10dra@gmail.com"),
        "business_name": "Sistema de Reservas",
        "whatsapp_number": "5492236689548"
    }

def send_reservation_email(client_email, client_name, data):
    config = get_smtp_config()
    smtp_user = config.get("smtp_user")
    smtp_password = config.get("smtp_password")
    smtp_server = config.get("smtp_server")
    smtp_port = config.get("smtp_port")
    from_email = config.get("from_email")

    if not smtp_user or not smtp_password:
        print("Email SMTP no configurado. No se envió el correo.")
        return False

    res_id = data.get('id_reserva', '—')
    res_code = f"R-{str(res_id).zfill(5)}" if str(res_id).isdigit() else res_id

    subject = f"Confirmación de Reserva {res_code} - {data.get('inmueble', '')}"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2e7d32;">¡Reserva Confirmada!</h2>
        <p style="color: #555;">Código de Reserva: <strong>{res_code}</strong></p>
        <p>Hola <strong>{client_name}</strong>,</p>
        <p>Te confirmamos los detalles de tu reserva en <strong>{config.get('business_name')}</strong>:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Fecha Ingreso:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('fecha_ingreso', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Fecha Egreso:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('fecha_egreso', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Noches:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('noches', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Inmueble:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('inmueble', '')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Ubicación:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('ubicacion', 'Consultar')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Servicios:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{data.get('servicios', 'No especificados')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Valor por Día:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('valor_dia', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Costo Total:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('costo_total', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Costo con Descuento:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('costo_con_descuento', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Adelanto:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">${data.get('adelanto', 0):,.2f}</td></tr>
            <tr><td style="padding: 8px;"><strong>Pago Pendiente:</strong></td><td style="padding: 8px;">${data.get('pago_pendiente', 0):,.2f}</td></tr>
        </table>
        <br>
        <p style="color: #555;">Gracias por confiar en <strong>{config.get('business_name')}</strong>.</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = client_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, client_email, msg.as_string())
        print(f"Correo enviado a {client_email}")
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False


def send_quotation_email(client_email, client_name, data):
    """Envía un correo de cotización formal."""
    config = get_smtp_config()
    smtp_user = config.get("smtp_user")
    smtp_password = config.get("smtp_password")
    smtp_server = config.get("smtp_server")
    smtp_port = config.get("smtp_port")
    from_email = config.get("from_email")
    business_name = config.get("business_name")
    whatsapp = config.get("whatsapp_number")

    if not smtp_user or not smtp_password:
        return False

    quot_id = data.get('id', '—')
    quot_code = f"Q-{str(quot_id).zfill(5)}" if str(quot_id).isdigit() else quot_id
    
    subject = f"🏨 Presupuesto de Estadía {quot_code} - {data.get('inmueble', '')}"

    body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">{business_name}</h1>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.8;">Presupuesto de Estadía - Código: {quot_code}</p>
            </div>
            <div style="padding: 30px;">
                <p>Hola <strong>{client_name}</strong>,</p>
                <p>Es un gusto saludarte. Tal como lo conversamos, te adjunto el presupuesto detallado para tu estadía:</p>
                
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;">📅 <strong>Periodo:</strong> Del {data.get('fecha_ingreso', '')} al {data.get('fecha_egreso', '')}</p>
                    <p style="margin: 5px 0;">🌙 <strong>Noches:</strong> {data.get('noches', '')}</p>
                    <p style="margin: 5px 0;">📍 <strong>Ubicación:</strong> {data.get('ubicacion', 'Consultar')}</p>
                    <h3 style="margin-top: 15px; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">🏠 {data.get('inmueble', '')}</h3>
                    <p style="margin: 5px 0;">✨ <strong>Servicios:</strong> {data.get('servicios', 'No especificados')}</p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 18px; margin-bottom: 5px; color: #7f8c8d; text-decoration: line-through;">Total: {data.get('costo_total', '$0,00')}</p>
                    <p style="font-size: 28px; font-weight: bold; margin-top: 0; color: #e67e22;">Precio Final: {data.get('final_price', '$0,00')}</p>
                    <p style="font-size: 14px; color: #95a5a6;">(Promedio por noche: {data.get('final_per_night', '$0,00')})</p>
                </div>

                <p style="text-align: center; margin-top: 40px;">
                    <a href="https://wa.me/{whatsapp}?text=Hola!%20Quiero%20confirmar%20la%20reserva%20{quot_code}%20de%20{data.get('inmueble', '').replace(' ', '%20')}%20para%20las%20fechas%20{data.get('fecha_ingreso', '')}%20al%20{data.get('fecha_egreso', '')}" 
                       style="background-color: #27ae60; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">RESERVAR AHORA</a>
                </p>
                
                <p style="font-size: 13px; color: #95a5a6; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
                    * Este presupuesto tiene validez por 15 días y está sujeto a disponibilidad al momento de confirmar. Por favor, mencione el código <strong>{quot_code}</strong> al contactarnos.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = client_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, client_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def send_marketing_offer_email(client_email, client_name, data):
    """Envía un correo de marketing mejorando la oferta original."""
    config = get_smtp_config()
    smtp_user = config.get("smtp_user")
    smtp_password = config.get("smtp_password")
    smtp_server = config.get("smtp_server")
    smtp_port = config.get("smtp_port")
    from_email = config.get("from_email")
    business_name = config.get("business_name")
    whatsapp = config.get("whatsapp_number")

    if not smtp_user or not smtp_password:
        return False

    quot_id = data.get('id', '—')
    quot_code = f"Q-{str(quot_id).zfill(5)}" if str(quot_id).isdigit() else quot_id
    
    subject = f"🎁 ¡Última Oportunidad! Mejoramos tu oferta para {data.get('inmueble', '')}"

    body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; border: 2px solid #27ae60; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #27ae60; color: white; padding: 25px; text-align: center;">
                <h1 style="margin: 0;">🎁 {business_name} - ¡Regalo Especial!</h1>
                <p style="margin: 5px 0; font-size: 16px;">Vemos que tu presupuesto {quot_code} está por vencer</p>
            </div>
            <div style="padding: 30px;">
                <p>Hola <strong>{client_name}</strong>,</p>
                <p>Te escribimos porque las fechas que consultaste para <strong>{data.get('inmueble', '')}</strong> siguen disponibles, ¡y no queremos que te las pierdas!</p>
                
                <p>Como tu presupuesto vence pronto, hemos decidido aplicarte un <strong>descuento adicional exclusivo</strong> si reservas en las próximas 24 horas:</p>

                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 25px 0; text-align: center; border: 1px dashed #27ae60;">
                    <p style="font-size: 18px; margin-bottom: 5px; color: #7f8c8d; text-decoration: line-through;">Precio Anterior: {data.get('old_price', '$0,00')}</p>
                    <p style="font-size: 32px; font-weight: bold; margin-top: 0; color: #27ae60;">NUEVO PRECIO: {data.get('new_price', '$0,00')}</p>
                    <p style="font-size: 14px; color: #34495e;">(Válido únicamente para las fechas: {data.get('fecha_ingreso', '')} al {data.get('fecha_egreso', '')})</p>
                </div>

                <p style="text-align: center; margin-top: 30px;">
                    <a href="https://wa.me/{whatsapp}?text=Hola!%20Recibí%20la%20oferta%20especial%20{quot_code}%20y%20quiero%20confirmar%20mi%20reserva%20de%20{data.get('inmueble', '').replace(' ', '%20')}" 
                       style="background-color: #2c3e50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">¡QUIERO EL DESCUENTO!</a>
                </p>
                
                <p style="font-size: 13px; color: #95a5a6; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; text-align: center;">
                    * Esta oferta es limitada y caducará automáticamente junto con tu presupuesto original.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = client_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, client_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
