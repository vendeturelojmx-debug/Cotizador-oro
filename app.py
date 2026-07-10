import streamlit as st
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ==========================================
# 1. FUNCIÓN DE SCRAPING Y CÁLCULO
# ==========================================
def obtener_precio_compra_oro():
    url = "https://oroyplata.com.mx/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        respuesta = requests.get(url, headers=headers)
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Como oroyplata.com.mx tiene tablas de precios, buscamos todas las tablas
        tablas = sopa.find_all('table')
        
        precio_encontrado = None
        
        for tabla in tablas:
            texto_tabla = tabla.text.lower()
            # Buscamos la tabla que diga "oro" y "compra"
            if 'oro' in texto_tabla and 'compra' in texto_tabla:
                # Extraemos todas las filas
                filas = tabla.find_all('tr')
                for fila in filas:
                    celdas = fila.find_all(['td', 'th'])
                    textos = [celda.text.strip().lower() for celda in celdas]
                    
                    # Si la fila tiene precios (contiene el signo $)
                    if any('$' in t for t in textos):
                        for texto in textos:
                            if '$' in texto:
                                # Limpiamos el texto para convertirlo en número flotante
                                str_precio = texto.replace('$', '').replace(',', '').strip()
                                # Tomamos el primer precio válido que encontremos
                                try:
                                    precio_encontrado = float(str_precio)
                                    break
                                except ValueError:
                                    continue
                        if precio_encontrado:
                            break
            if precio_encontrado:
                break
                
        # Si logramos extraer un precio de la página (ej. 1300), le quitamos el 5%
        if precio_encontrado:
            precio_con_descuento = precio_encontrado * 0.95
            return precio_con_descuento
        else:
            # Precio de respaldo en caso de que cambien el diseño de la web
            st.warning("No se detectó la tabla en la página. Usando precio de respaldo temporal.")
            return 1250.00 * 0.95
            
    except Exception as e:
        st.error(f"Error al conectar con oroyplata.com.mx: {e}")
        return None

# ==========================================
# 2. GENERADOR DE LA IMAGEN PROFESIONAL
# ==========================================
def generar_imagen_vende_tu_oro(precio_1g):
    # Creamos un lienzo oscuro y elegante con Matplotlib
    fig, ax = plt.subplots(figsize=(8, 10), facecolor='#111111')
    ax.set_facecolor('#111111')
    ax.axis('off') # Quitamos los bordes del gráfico

    # Títulos principales
    ax.text(0.5, 0.9, 'Vende Tu Oro Mx', color='#FFD700', fontsize=38, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.82, 'PRECIOS DE COMPRA AL DÍA', color='#EEEEEE', fontsize=18, ha='center', va='center')

    # Línea separadora dorada
    ax.plot([0.2, 0.8], [0.77, 0.77], color='#FFD700', lw=2)

    # Mensaje de confirmación del precio
    ax.text(0.5, 0.72, f"Lo podemos comprar a este precio (1g): ${precio_1g:,.2f} MXN", 
            color='#00FF7F', fontsize=15, fontweight='bold', ha='center', va='center')

    # Lista de precios (1g, 5g, 10g, 50g)
    gramajes = [1, 5, 10, 50]
    y_pos = 0.62

    for w in gramajes:
        # Dibujar una caja de fondo para cada fila
        rect = plt.Rectangle((0.15, y_pos-0.03), 0.7, 0.06, color='#222222', zorder=1, transform=ax.transAxes)
        ax.add_patch(rect)
        
        # Texto del gramaje (Izquierda)
        texto_gramo = f"{w} Gramo{'s' if w > 1 else ''}"
        ax.text(0.2, y_pos, texto_gramo, color='#FFFFFF', fontsize=20, fontweight='bold', ha='left', va='center', zorder=2)
        
        # Texto del precio total (Derecha)
        precio_total = precio_1g * w
        ax.text(0.8, y_pos, f"${precio_total:,.2f} MXN", color='#FFD700', fontsize=20, fontweight='bold', ha='right', va='center', zorder=2)
        
        y_pos -= 0.1

    # Leyenda final requerida
    ax.text(0.5, 0.15, '* El precio del oro puede variar dependiendo el día.', 
            color='#AAAAAA', fontsize=12, style='italic', ha='center', va='center')
    ax.text(0.5, 0.08, '¡Cotiza tu pieza sin compromiso!', 
            color='#FFFFFF', fontsize=14, ha='center', va='center')

    # Guardamos la imagen en la memoria RAM para enviarla a la web
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()

# ==========================================
# 3. INTERFAZ DE USUARIO (PANEL WEB)
# ==========================================
st.set_page_config(page_title="Generador Precios Oro", page_icon="🥇")

st.title("🥇 Cotizador: Vende Tu Oro Mx")
st.write("Presiona el botón para leer el precio de *oroyplata.com.mx*, restar el 5% y generar la imagen.")

if st.button("Consultar y Generar Imagen", type="primary"):
    with st.spinner('Conectando con la página web...'):
        precio_calculado = obtener_precio_compra_oro()
        
        if precio_calculado:
            st.success(f"¡Precio procesado exitosamente! Lo podemos comprar a este precio: **${precio_calculado:,.2f} MXN** por gramo.")
            
            # Generamos la imagen
            imagen_bytes = generar_imagen_vende_tu_oro(precio_calculado)
            
            # Mostramos la imagen en pantalla
            st.image(imagen_bytes, caption="Imagen generada, lista para compartir.", use_column_width=True)
            
            # Botón de descarga
            nombre_archivo = f"VendeTuOroMx_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            st.download_button(
                label="📥 Descargar Imagen",
                data=imagen_bytes,
                file_name=nombre_archivo,
                mime="image/png"
            )
        else:
            st.error("No se pudo obtener el precio en este momento.")
