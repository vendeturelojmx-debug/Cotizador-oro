import streamlit as st
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ==========================================
# 1. FUNCIÓN DE SCRAPING MEJORADA
# ==========================================
def obtener_precio_compra_oro():
    url = "https://oroyplata.com.mx/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        respuesta = requests.get(url, headers=headers)
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        tablas = sopa.find_all('table')
        precio_encontrado = None
        
        for tabla in tablas:
            # Buscamos la tabla que tenga la palabra oro
            if 'oro' in tabla.text.lower():
                filas = tabla.find_all('tr')
                for fila in filas:
                    texto_fila = fila.text.lower()
                    
                    # Buscamos ESPECÍFICAMENTE la fila de 24 Quilates
                    if '24 quilates' in texto_fila:
                        celdas = fila.find_all(['td', 'th'])
                        
                        # Nos aseguramos de que tenga suficientes columnas
                        if len(celdas) >= 3:
                            # La columna 3 (índice 2) es la de "Compra"
                            texto_precio = celdas[2].text
                            
                            # Limpiamos letras extrañas, signos y comas
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
            st.warning("No se detectó la tabla de 24 Quilates. Usando precio de respaldo temporal.")
            return 1250.00 * 0.95
            
    except Exception as e:
        st.error(f"Error al conectar con la página: {e}")
        return None

# ==========================================
# 2. GENERADOR DE IMAGEN CORREGIDO
# ==========================================
def generar_imagen_vende_tu_oro(precio_1g):
    fig, ax = plt.subplots(figsize=(8, 10), facecolor='#111111')
    ax.set_facecolor('#111111')
    
    # ESTO EVITA QUE LA IMAGEN SE DEFORME (Bloquea las coordenadas de 0 a 1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off') 

    # Títulos
    ax.text(0.5, 0.9, 'Vende Tu Oro Mx', color='#FFD700', fontsize=38, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.82, 'PRECIOS DE COMPRA AL DÍA', color='#EEEEEE', fontsize=18, ha='center', va='center')
    ax.plot([0.2, 0.8], [0.77, 0.77], color='#FFD700', lw=2)

    # Subtítulo con el precio base (Ej. 24k)
    ax.text(0.5, 0.72, f"Lo podemos comprar a este precio (1g base 24k): ${precio_1g:,.2f} MXN", 
            color='#00FF7F', fontsize=13, fontweight='bold', ha='center', va='center')

    gramajes = [1, 5, 10, 50]
    y_pos = 0.62

    for w in gramajes:
        # Cajas oscuras
        rect = plt.Rectangle((0.15, y_pos-0.03), 0.7, 0.06, color='#222222', zorder=1)
        ax.add_patch(rect)
        
        # Gramos
        texto_gramo = f"{w} Gramo{'s' if w > 1 else ''}"
        ax.text(0.2, y_pos, texto_gramo, color='#FFFFFF', fontsize=20, fontweight='bold', ha='left', va='center', zorder=2)
        
        # Precio Total
        precio_total = precio_1g * w
        ax.text(0.8, y_pos, f"${precio_total:,.2f} MXN", color='#FFD700', fontsize=20, fontweight='bold', ha='right', va='center', zorder=2)
        
        y_pos -= 0.1

    # Textos finales
    ax.text(0.5, 0.15, '* El precio del oro puede variar dependiendo el día.', 
            color='#AAAAAA', fontsize=12, style='italic', ha='center', va='center')
    ax.text(0.5, 0.08, '¡Cotiza tu pieza sin compromiso!', 
            color='#FFFFFF', fontsize=14, ha='center', va='center')

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
st.write("Presiona el botón para leer el precio de 24 Quilates, restar el 5% y generar la imagen.")

if st.button("Consultar y Generar Imagen", type="primary"):
    with st.spinner('Conectando con la página web...'):
        precio_calculado = obtener_precio_compra_oro()
        
        if precio_calculado:
            st.success(f"¡Precio extraído con éxito! Lo pagaremos a: **${precio_calculado:,.2f} MXN** por gramo.")
            
            imagen_bytes = generar_imagen_vende_tu_oro(precio_calculado)
            
            st.image(imagen_bytes, caption="Imagen generada y lista.", use_column_width=True)
            
            nombre_archivo = f"VendeTuOroMx_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            st.download_button(
                label="📥 Descargar Imagen",
                data=imagen_bytes,
                file_name=nombre_archivo,
                mime="image/png"
            )
