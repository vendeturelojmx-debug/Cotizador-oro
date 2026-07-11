import streamlit as st
from curl_cffi import requests as cureq
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ==========================================
# 1. FUNCIÓN ANTI-BLOQUEOS DEFINITIVA
# ==========================================
def obtener_precio_compra_oro():
    url = "https://oroyplata.com.mx/"
    
    try:
        # Usamos curl_cffi para imitar la huella digital exacta de Chrome al 100%
        respuesta = cureq.get(url, impersonate="chrome", timeout=15)
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        tablas = sopa.find_all('table')
        precio_encontrado = None
        
        for tabla in tablas:
            if 'oro' in tabla.text.lower():
                filas = tabla.find_all('tr')
                for fila in filas:
                    texto_fila = fila.text.lower()
                    
                    # Buscamos la fila de 24 Quilates
                    if '24 quilates' in texto_fila:
                        celdas = fila.find_all(['td', 'th'])
                        
                        if len(celdas) >= 3:
                            texto_precio = celdas[2].text
                            str_precio = texto_precio.replace('$', '').replace(',', '').replace('por gr.', '').strip()
                            
                            try:
                                precio_encontrado = float(str_precio)
                                break
                            except ValueError:
                                continue
                if precio_encontrado:
                    break
                    
        # Aplicamos el descuento del 5%
        if precio_encontrado:
            return precio_encontrado * 0.95
        else:
            return None
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# ==========================================
# 2. GENERADOR DE IMAGEN (Diseño 1g, 5g, 10g, 50g)
# ==========================================
def generar_imagen_vende_tu_oro(precio_1g):
    fig, ax = plt.subplots(figsize=(8, 10), facecolor='#111111')
    ax.set_facecolor('#111111')
    
    # Bloqueamos coordenadas
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off') 

    # Títulos
    ax.text(0.5, 0.9, 'Vende Tu Oro Mx', color='#FFD700', fontsize=40, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.82, 'PRECIOS DE COMPRA AL DÍA', color='#EEEEEE', fontsize=18, ha='center', va='center')
    ax.plot([0.15, 0.85], [0.77, 0.77], color='#FFD700', lw=2)

    # Subtítulo verde
    ax.text(0.5, 0.72, f"Lo podemos comprar a este precio (1g base 24k): ${precio_1g:,.2f} MXN", 
            color='#00FF7F', fontsize=14, fontweight='bold', ha='center', va='center')

    # Cajas de gramos
    gramajes = [1, 5, 10, 50]
    y_pos = 0.60

    for w in gramajes:
        rect = plt.Rectangle((0.15, y_pos-0.035), 0.7, 0.07, color='#222222', zorder=1)
        ax.add_patch(rect)
        
        texto_gramo = f"{w} Gramo{'s' if w > 1 else ''}"
        ax.text(0.2, y_pos, texto_gramo, color='#FFFFFF', fontsize=22, fontweight='bold', ha='left', va='center', zorder=2)
        
        precio_total = precio_1g * w
        ax.text(0.8, y_pos, f"${precio_total:,.2f} MXN", color='#FFD700', fontsize=22, fontweight='bold', ha='right', va='center', zorder=2)
        
        y_pos -= 0.11

    # Footer
    ax.text(0.5, 0.12, '* El precio del oro puede variar dependiendo el día.', 
            color='#AAAAAA', fontsize=12, style='italic', ha='center', va='center')

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
st.write("Presiona el botón para consultar el precio base de 24k, restar el 5% y generar la imagen.")

if st.button("Consultar y Generar Imagen", type="primary"):
    with st.spinner('Conectando de forma segura...'):
        precio_calculado = obtener_precio_compra_oro()
        
        if precio_calculado:
            st.success("¡Conexión exitosa! Precio extraído correctamente.")
            imagen_bytes = generar_imagen_vende_tu_oro(precio_calculado)
            st.image(imagen_bytes, caption="Imagen lista para descargar.", use_column_width=True)
            
            nombre_archivo = f"VendeTuOroMx_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            st.download_button(label="📥 Descargar Imagen", data=imagen_bytes, file_name=nombre_archivo, mime="image/png")
        else:
            st.error("No se pudo extraer el precio. La estructura de la página o la conexión fallaron.")
