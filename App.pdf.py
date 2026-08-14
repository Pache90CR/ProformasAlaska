import streamlit as st
import os
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Proformas - Alaska Bar Restaurante",
    page_icon="🏔️",
    layout="centered"
)

# Estilos adaptables automáticamente al Modo Claro y Modo Oscuro
st.markdown("""
    <style>
    .main-title {
        color: var(--text-color);
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0px;
        letter-spacing: 2px;
    }
    .sub-title {
        color: var(--text-color);
        opacity: 0.8;
        text-align: center;
        font-weight: 600;
        margin-top: 0px;
        letter-spacing: 1px;
    }
    .contact-info {
        text-align: center;
        font-size: 0.9rem;
        opacity: 0.7;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO PANTALLA PRINCIPAL ---
st.markdown("<h1 class='main-title'>ALASKA</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>BAR RESTAURANTE</h3>", unsafe_allow_html=True)
st.markdown("<div class='contact-info'>📍 Cotizaciones y Proformas | 📞 7066 8903 / 8521 3829</div>", unsafe_allow_html=True)
st.divider()

# --- BLINDAJE DE SESIÓN ---
if "items" not in st.session_state or not isinstance(st.session_state["items"], list):
    st.session_state["items"] = []

# --- DATOS DEL CLIENTE ---
st.subheader("📋 Datos del Cliente y Evento")
col_c1, col_c2 = st.columns(2)

with col_c1:
    cliente = st.text_input("Nombre del Cliente / Empresa:", placeholder="Ej. María Rodríguez")
    telefono_cliente = st.text_input("Teléfono del Cliente:", placeholder="Ej. 8888 8888")

with col_c2:
    fecha_evento = st.date_input("Fecha del Evento:", value=date.today())
    tipo_evento = st.selectbox("Tipo de Evento:", ["Cumpleaños", "Corporativo", "Reserva Especial", "Catering", "Otro"])

st.divider()

# --- AGREGAR ÍTEMS ---
st.subheader("🛒 Agregar Platillos / Servicios")

descripcion = st.text_input("Descripción del Producto/Servicio:", placeholder="Ej. Plato Fuerte: Corte de Carne")

col_i1, col_i2 = st.columns(2)
with col_i1:
    cantidad = st.number_input("Cantidad:", min_value=1, value=1, step=1)
with col_i2:
    precio = st.number_input("Precio Unitario (₡):", min_value=0.0, value=0.0, step=500.0)

# BOTÓN CON VERIFICACIÓN SEGURA
if st.button("➕ Agregar a la Proforma", use_container_width=True):
    if descripcion.strip() != "" and precio > 0:
        if not isinstance(st.session_state["items"], list):
            st.session_state["items"] = []
            
        st.session_state["items"].append({
            "desc": descripcion.strip(),
            "cant": int(cantidad),
            "precio": float(precio),
            "total": float(cantidad * precio)
        })
        st.success(f"¡'{descripcion}' agregado correctamente!")
        st.rerun()
    else:
        st.warning("⚠️ Ingresa una descripción y un precio mayor a ₡0.")

# --- TABLA Y TOTALES ---
st.divider()
st.subheader("📄 Resumen de Proforma")

if isinstance(st.session_state["items"], list) and len(st.session_state["items"]) > 0:
    tabla_mostrar = []
    subtotal = 0.0
    
    for item in st.session_state["items"]:
        subtotal += item["total"]
        tabla_mostrar.append({
            "Cant.": item["cant"],
            "Descripción": item["desc"],
            "P. Unitario": f"₡{item['precio']:,.2f}",
            "Total": f"₡{item['total']:,.2f}"
        })
    
    st.table(tabla_mostrar)
    st.markdown(f"### **Total General: ₡{subtotal:,.2f}**")

    # --- CAMPO DE OBSERVACIONES ---
    observaciones = st.text_area(
        "📝 Observaciones o Condiciones Especiales:",
        value="Se requiere un depósito del 50% para confirmar la reservación. Cotización válida por 15 días.",
        help="Este texto aparecerá en el recuadro de observaciones en la parte inferior del PDF."
    )

    # Botón para vaciar proforma
    if st.button("🗑️ Vaciar Proforma", use_container_width=True):
        st.session_state["items"] = []
        st.rerun()

    # --- GENERADOR DE PDF ---
    def generar_pdf():
        # Registrar fuente con soporte Unicode garantizado usando matplotlib
        font_regular = "Helvetica"
        font_bold = "Helvetica-Bold"

        try:
            import matplotlib
            mpl_ttf = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', 'DejaVuSans.ttf')
            mpl_ttf_bold = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', 'DejaVuSans-Bold.ttf')
            
            if os.path.exists(mpl_ttf):
                pdfmetrics.registerFont(TTFont('UnicodeSans', mpl_ttf))
                font_regular = 'UnicodeSans'
                
            if os.path.exists(mpl_ttf_bold):
                pdfmetrics.registerFont(TTFont('UnicodeSans-Bold', mpl_ttf_bold))
                font_bold = 'UnicodeSans-Bold'
        except Exception:
            pass

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName=font_bold, fontSize=20, leading=22, textColor=colors.HexColor('#1E2D4A'), alignment=1)
        sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName=font_bold, fontSize=12, leading=14, textColor=colors.HexColor('#555555'), alignment=1)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName=font_regular, fontSize=10, leading=12)

        # Logo en el PDF impreso
        if os.path.exists("logo.png"):
            try:
                img_logo = Image("logo.png", width=90, height=90)
                img_logo.hAlign = 'CENTER'
                elements.append(img_logo)
                elements.append(Spacer(1, 10))
            except Exception:
                pass

        # Encabezado PDF
        elements.append(Paragraph("BAR RESTAURANTE ALASKA", title_style))
        elements.append(Paragraph("Cotización / Proforma", sub_style))
        elements.append(Paragraph("Teléfonos: 7066 8903 / 8521 3829", sub_style))
        elements.append(Spacer(1, 15))

        # Información del Cliente
        data_info = [
            [Paragraph(f"<b>Cliente:</b> {cliente}", body_style), Paragraph(f"<b>Fecha Evento:</b> {fecha_evento.strftime('%d/%m/%Y')}", body_style)],
            [Paragraph(f"<b>Teléfono:</b> {telefono_cliente}", body_style), Paragraph(f"<b>Tipo Evento:</b> {tipo_evento}", body_style)]
        ]
        info_table = Table(data_info, colWidths=[270, 270])
        info_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        # Tabla de Detalles con el símbolo de colones ₡
        table_data = [["Cant.", "Descripción", "P. Unitario", "Total"]]
        for item in st.session_state["items"]:
            table_data.append([
                str(item['cant']),
                item['desc'],
                f"₡{item['precio']:,.2f}",
                f"₡{item['total']:,.2f}"
            ])
        
        table_data.append(["", "", "TOTAL:", f"₡{subtotal:,.2f}"])

        t = Table(table_data, colWidths=[40, 300, 100, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E2D4A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), font_bold),
            ('FONTNAME', (0,1), (-1,-1), font_regular),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-2), 0.5, colors.lightgrey),
            ('FONTNAME', (-2,-1), (-1,-1), font_bold),
            ('BACKGROUND', (-2,-1), (-1,-1), colors.HexColor('#F4F1EA')),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 20))

        # --- RECUADRO DE OBSERVACIONES ESTILIZADO (IGUAL A LA IMAGEN) ---
        if observaciones.strip():
            obs_header_style = ParagraphStyle('ObsHeader', fontName=font_bold, fontSize=9, textColor=colors.white, alignment=1)
            obs_text_style = ParagraphStyle('ObsText', fontName=font_regular, fontSize=9, textColor=colors.HexColor('#2B2B2B'), leading=11)

            obs_table_data = [
                [Paragraph("OBSERVACIONES", obs_header_style), Paragraph(observaciones.strip(), obs_text_style)]
            ]

            obs_table = Table(obs_table_data, colWidths=[120, 420])
            obs_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), colors.HexColor('#1E2D4A')), # Color corporativo azul marino
                ('BACKGROUND', (1,0), (1,0), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (0,0), 'CENTER'),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1E2D4A')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#1E2D4A')),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (1,0), (1,0), 10),
                ('RIGHTPADDING', (1,0), (1,0), 10),
            ]))
            elements.append(obs_table)
            elements.append(Spacer(1, 20))

        elements.append(Paragraph("<i>Gracias por preferirnos. ¡Estamos para servirle!</i>", sub_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    # Botón de Descarga PDF
    st.divider()
    pdf_bytes = generar_pdf()
    nombre_archivo = cliente.strip().replace(" ", "_") if cliente.strip() else "Cliente"
    
    st.download_button(
        label="📥 Descargar Proforma en PDF",
        data=pdf_bytes,
        file_name=f"Proforma_Alaska_{nombre_archivo}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

else:
    st.info("💡 Aún no has agregado ítems a esta proforma. Escribe la descripción y el precio arriba, y presiona '➕ Agregar a la Proforma'.")
