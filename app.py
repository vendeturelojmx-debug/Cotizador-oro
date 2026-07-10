import streamlit as st
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ==========================================
# 1. FUNCIÓN DE SCRAPING (A PRUEBA DE FALLOS)
# ==========================================
def obtener_precios_oro():
    url = "https://oroyplata.com.mx/"
    # Simulamos ser un navegador real de forma avanzada
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    precios = {}
    
    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Buscamos en todas las filas de la página
        filas = sopa.find_all('tr')
        for fila in filas:
            if 'quilates' in fila.text.lower():
                celdas = fila.find_all(['td', 'th'])
                
                nombre_kilataje = ""
                precio_texto = ""
                
                # Buscamos la celda del nombre y la del primer precio (Compra)
                for celda in celdas:
                    texto_celda = celda.text.strip()
                    if 'quilates' in texto_celda.lower():
                        nombre_kilataje = texto_celda
                    elif '$' in texto_celda and precio_texto == "":
                        precio_texto = texto_celda
                        
                # Si encontramos ambos, lo limpiamos y guardamos
                if nombre_kilataje and precio_texto:
                    str_precio = precio_texto.replace('$', '').replace(',', '').replace('por gr.', '').strip()
                    try:
                        precio_float = float(str_precio)
                        # Aplicamos el descuento del 5%
                        precios[nombre_kilataje] = precio_float * 0.95
                    except ValueError:
                        pass

    except Exception as e:
        pass # Si hay error, pasamos directo al sistema de respaldo

    # SISTEMA DE RESPALDO (Por si la página bloquea a Streamlit)
    if not precios:
        st.warning("⚠️ No se pudo conectar en vivo (la página bloqueó la conexión). Usando precios de respaldo.")
        precios = {
            "10 Quilates": 908.00 * 0.95,
            "14 Quilates": 1269.00 * 0.95,
            "18 Quilates": 1621.00 * 0.95,
            "21,6 Quilates": 2022.00 * 0.95,
            "24 Quilates": 2247.00 * 0.95
        }
        
    return precios

# ==========================================
# 2. GENERADOR DE IMAGEN (LISTA DE QUILATES)
# ==========================================
def generar_imagen_vende_tu_oro(precios):
    fig, ax = plt.subplots(figsize=(8, 10), facecolor='#111111')
    ax.set_facecolor('#111111')
    
    # Bloqueamos coordenadas para evitar deformaciones
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off') 

    # Títulos
    ax.text(0.5, 0.9, 'Vende Tu Oro Mx', color='#FFD700', fontsize=40, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.82, 'PRECIOS DE COMPRA AL DÍA (POR GRAMO)', color='#EEEEEE', fontsize=15, ha='center', va='center')
    ax.plot([0.15, 0.85], [0.77, 0.77], color='#FFD700', lw=2)

    # Coordenada inicial para empezar a dibujar la lista
    y_pos = 0.67
    
    # Dibujamos cada kilataje encontrado
    for kilataje, precio in precios.items():
        # Cajas oscuras de fondo
        rect = plt.Rectangle((0.15, y_pos-0.035), 0.7, 0.07, color='#222222', zorder=1)
        ax.add_patch(rect)
        
        # Nombre del kilataje (Izquierda)
        ax.text(0.2, y_pos, kilataje, color='#FFFFFF', fontsize=20, fontweight='bold', ha='left', va='center', zorder=2)
        
        # Precio ya con descuento (Derecha)
        ax.text(0.8, y_pos, f"${precio:,.2f} MXN", color='#00FF7F', fontsize=20, fontweight='bold', ha='right', va='center', zorder=2)
        
        # Bajamos el espacio para el siguiente renglón
        y_pos -= 0.11

    # Textos finales
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
# 3. PANEL WEB
# ==========================================
st.set_page_config(page_title="Generador Precios Oro", page_icon="🥇")

st.title("🥇 Cotizador: Vende Tu Oro Mx")
st.write("Presiona el botón para leer los precios de todos los quilates, restar el 5% y generar la imagen.")

if st.button("Consultar y Generar Imagen", type="primary"):
    with st.spinner('Conectando con la página web...'):
        precios_calculados = obtener_precios_oro()
        
        if precios_calculados:
            st.success("¡Precios procesados con éxito!")
            
            # Generamos la imagen
            imagen_bytes = generar_imagen_vende_tu_oro(precios_calculados)
            
            # Mostramos la imagen
            st.image(imagen_bytes, caption="Imagen lista para descargar.", use_column_width=True)
            
            nombre_archivo = f"VendeTuOroMx_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            st.download_button(
                label="📥 Descargar Imagen",
                data=imagen_bytes,
                file_name=nombre_archivo,
                mime="image/png"
            )
