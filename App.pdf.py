import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Proformas - Alaska Bar Restaurante",
    page_icon="🏔️",
    layout="centered"
)

# Estilos visuales
st.markdown("""
    <style>
    .stApp { background-color: #F4F1EA; }
    .main-title { color: #1E2D4A; text-align: center; font-weight: bold; margin-bottom: 0px; }
    .sub-title { color: #555555; text-align: center; font-weight: bold; margin-top: 0px; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.markdown("<h1 class='main-title'>🏔️ ALASKA</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>BAR RESTAURANTE</h3>", unsafe_allow_html=True)
st.caption("📍 Cotizaciones y Proformas | 📞 7066 8903 / 8521 3829")
st.divider()

# --- VALIDACIÓN ROBUSTA DEL ESTADO DE LA SESIÓN ---
# Si "items" no existe o fue guardado con un tipo incorrecto por errores previos, se reinicia como lista limpia.
if "items" not in st.session_state or not isinstance(st.session_state.items, list):
    st.session_state.items = []

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

col_i1, col_i2, col_i3 = st.columns([3, 1, 1])

with col_i1:
    descripcion = st.text_input("Descripción del Producto/Servicio:", placeholder="Ej. Plato Fuerte: Corte de Carne")
with col_i2:
    cantidad = st.number_input("Cantidad:", min_value=1, value=1, step=1)
with col_i3:
    precio = st.number_input("Precio Unit. (₡):", min_value=0.0, value=0.0, step=500.0)

if st.button("➕ Agregar Ítem", use_container_width=True):
    if descripcion.strip() != "" and precio > 0:
        st.session_state.items.append({
            "Descripción": descripcion,
            "Cantidad": cantidad,
            "Precio Unitario (₡)": precio,
            "Total (₡)": cantidad * precio
        })
        st.success(f"¡'{descripcion}' agregado correctamente!")
        st.rerun()
    else:
        st.warning("Por favor ingresa una descripción y un precio mayor a 0.")

# --- TABLA Y TOTALES ---
st.divider()
st.subheader("📄 Resumen de Proforma")

if st.session_state.items:
    # Convertimos la lista a DataFrame
    df = pd.DataFrame(st.session_state.items)
    
    # Formato para la vista en pantalla
    df_display = df.copy()
    df_display["Precio Unitario (₡)"] = df_display["Precio Unitario (₡)"].apply(lambda x: f"₡{x:,.2f}")
    df_display["Total (₡)"] = df_display["Total (₡)"].apply(lambda x: f"₡{x:,.2f}")
    
    st.dataframe(df_display, use_container_width=True)

    # Cálculo de Totales
    subtotal = df["Total (₡)"].sum()
    st.markdown(f"### **Total General: ₡{subtotal:,.2f}**")

    # Botón para limpiar proforma
    if st.button("🗑️ Vaciar Proforma"):
        st.session_state.items = []
        st.rerun()

    # --- GENERADOR DE PDF ---
    def generar_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, leading=22, textColor=colors.HexColor('#1E2D4A'), alignment=1)
        sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#555555'), alignment=1)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=12)

        # Encabezado PDF
        elements.append(Paragraph("ALASKA BAR RESTAURANTE", title_style))
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

        # Tabla de Detalles
        table_data = [["Cant.", "Descripción", "P. Unitario", "Total"]]
        for item in st.session_state.items:
            table_data.append([
                str(item['Cantidad']),
                item['Descripción'],
                f"₡{item['Precio Unitario (₡)']:,.2f}",
                f"₡{item['Total (₡)']:,.2f}"
            ])
        
        table_data.append(["", "", "TOTAL:", f"₡{subtotal:,.2f}"])

        t = Table(table_data, colWidths=[40, 300, 100, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E2D4A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-2), 0.5, colors.lightgrey),
            ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
            ('BACKGROUND', (-2,-1), (-1,-1), colors.HexColor('#F4F1EA')),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("<i>Gracias por preferir a Alaska Bar Restaurante. ¡Estamos para servirle!</i>", sub_style))

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
    st.info("💡 Aún no has agregado ítems a esta proforma. Llena los datos arriba y presiona '+ Agregar Ítem'.")
