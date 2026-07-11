import streamlit as st
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ==========================================
# 1. FUNCIÓN DE SCRAPING AUTOMÁTICO VÍA PUENTE
# ==========================================
def obtener_precios_oro_automatico():
    # Tu API Key privada para saltar el bloqueo de Cloudflare
    API_KEY = "7d00dc2f7af69c8ce194a1540dee69fe"
    url_destino = "https://oroyplata.com.mx/"
    
    # Construimos la URL usando el puente de ScraperAPI
    url_puente = f"http://api.scraperapi.com?api_key={API_KEY}&url={url_destino}"
    
    precios = {}
    
    try:
        # Hacemos la consulta a través del puente autorizado
        respuesta = requests.get(url_puente, timeout=30)
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Analizamos las filas de la tabla extraída
        filas = sopa.find_all('tr')
        for fila in filas:
            if 'quilates' in fila.text.lower():
                celdas = fila.find_all(['td', 'th'])
                
                nombre_kilataje = ""
                precio_texto = ""
                
                # Buscamos la celda del nombre y la del precio de Compra
                for celda in celdas:
                    texto_celda = celda.text.strip()
                    if 'quilates' in texto_celda.lower():
                        nombre_kilataje = texto_celda
                    elif '$' in texto_celda and precio_texto == "":
                        precio_texto = texto_celda
                        
                # Si encontramos ambos datos, los limpiamos y guardamos con el -5%
                if nombre_kilataje and precio_texto:
                    str_precio = precio_texto.replace('$', '').replace(',', '').replace('por gr.', '').strip()
                    try:
                        precio_float = float(str_precio)
                        # Aplicamos la fórmula matemática solicitada (-5%)
                        precios[nombre_kilataje] = precio_float * 0.95
                    except ValueError:
                        pass
                        
    except Exception as e:
        st.error(f"Error al conectar con el puente de extracción: {e}")
        
    return precios

# ==========================================
# 2. GENERADOR DE IMAGEN (TODOS LOS QUILATES)
# ==========================================
def generar_imagen_vende_tu_oro(precios_dict):
    fig, ax = plt.subplots(figsize=(8, 10), facecolor='#111111')
    ax.set_facecolor('#111111')
    
    # Bloqueamos coordenadas para evitar deformaciones en la web
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off') 

    # Títulos principales del Banner
    ax.text(0.5, 0.9, 'Vende Tu Oro Mx', color='#FFD700', fontsize=40, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.82, 'PRECIOS DE COMPRA AL DÍA (POR GRAMO)', color='#EEEEEE', fontsize=15, ha='center', va='center')
    ax.plot([0.15, 0.85], [0.77, 0.77], color='#FFD700', lw=2)

    # Coordenada inicial para el primer bloque
    y_pos = 0.67
    
    # Dibujamos dinámicamente cada categoría de oro de la tabla
    for kilataje, precio in precios_dict.items():
        # Cajas oscuras de fondo para resaltar
        rect = plt.Rectangle((0.15, y_pos-0.035), 0.7, 0.07, color='#222222', zorder=1)
        ax.add_patch(rect)
        
        # Nombre del kilataje (Izquierda)
        ax.text(0.2, y_pos, kilataje, color='#FFFFFF', fontsize=22, fontweight='bold', ha='left', va='center', zorder=2)
        
        # Precio final ya con descuento (Derecha)
        ax.text(0.8, y_pos, f"${precio:,.2f} MXN", color='#00FF7F', fontsize=22, fontweight='bold', ha='right', va='center', zorder=2)
        
        # Espaciado hacia abajo para el siguiente renglón
        y_pos -= 0.11

    # Leyenda requerida sobre la variación de precio
    ax.text(0.5, 0.12, '* El precio del oro puede variar dependiendo el día.', 
            color='#AAAAAA', fontsize=12, style='italic', ha='center', va='center')
    ax.text(0.5, 0.06, '¡Cotiza tu pieza sin compromiso!', 
            color='#FFFFFF', fontsize=15, ha='center', va='center')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()

# ==========================================
# 3. INTERFAZ GRÁFICA DEL PANEL WEB
# ==========================================
st.set_page_config(page_title="Generador Precios Oro", page_icon="🥇")

st.title("🥇 Cotizador Inteligente: Vende Tu Oro Mx")
st.write("El sistema extraerá los precios en vivo de la tabla de la competencia usando un túnel seguro, aplicará tu margen del -5% y diseñará tu imagen corporativa.")

if st.button("Consultar y Generar Imagen Automáticamente", type="primary"):
    with st.spinner('Extrayendo datos de forma segura a través de ScraperAPI...'):
        precios_finales = obtener_precios_oro_automatico()
        
        if precios_finales:
            st.success("¡Datos extraídos con éxito! Aplicando fórmulas y generando banner corporativo...")
            
            # Generamos la imagen procesando el diccionario con todos los kilatajes
            imagen_bytes = generar_imagen_vende_tu_oro(precios_finales)
            
            # Desplegamos la imagen final en pantalla
            st.image(imagen_bytes, caption="Imagen Corporativa Generada Correctamente.", use_column_width=True)
            
            # Botón para descargarla a tu PC o Móvil
            nombre_archivo = f"VendeTuOroMx_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            st.download_button(
                label="📥 Descargar Imagen para Redes Sociales",
                data=imagen_bytes,
                file_name=nombre_archivo,
                mime="image/png"
            )
        else:
            st.error("No se pudo extraer la información. Revisa que tu cuenta de ScraperAPI tenga créditos activos.")
