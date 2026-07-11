import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ==========================================
# 1. GENERADOR DE IMAGEN (TODOS LOS QUILATES)
# ==========================================
def generar_imagen_todos_los_quilates(precios_dict):
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
    
    # Dibujamos cada kilataje 
    for kilataje, precio in precios_dict.items():
        # Cajas oscuras de fondo
        rect = plt.Rectangle((0.15, y_pos-0.035), 0.7, 0.07, color='#222222', zorder=1)
        ax.add_patch(rect)
        
        # Nombre del kilataje (Izquierda)
        ax.text(0.2, y_pos, kilataje, color='#FFFFFF', fontsize=22, fontweight='bold', ha='left', va='center', zorder=2)
        
        # Precio ya con descuento (Derecha)
        ax.text(0.8, y_pos, f"${precio:,.2f} MXN", color='#00FF7F', fontsize=22, fontweight='bold', ha='right', va='center', zorder=2)
        
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
# 2. PANEL WEB (SEMI-AUTOMÁTICO)
# ==========================================
st.set_page_config(page_title="Generador Precios Oro", page_icon="🥇")

st.title("🥇 Cotizador: Vende Tu Oro Mx")
st.write("Verifica o actualiza los precios base de hoy. El sistema **restará automáticamente el 5%** a cada categoría y dibujará la imagen.")

# Creamos dos columnas para que se vea ordenado
col1, col2 = st.columns(2)

with col1:
    p_10k = st.number_input("Precio 10 Quilates (Base)", value=908.0)
    p_14k = st.number_input("Precio 14 Quilates (Base)", value=1269.0)
    p_18k = st.number_input("Precio 18 Quilates (Base)", value=1621.0)

with col2:
    p_21k = st.number_input("Precio 21.6 Quilates (Base)", value=2022.0)
    p_24k = st.number_input("Precio 24 Quilates (Base)", value=2247.0)

st.write("---")

if st.button("Aplicar 5% de descuento y Generar Imagen", type="primary"):
    # Aplicamos la fórmula matemática a lo que hayas escrito arriba
    precios_con_descuento = {
        "10 Quilates": p_10k * 0.95,
        "14 Quilates": p_14k * 0.95,
        "18 Quilates": p_18k * 0.95,
        "21.6 Quilates": p_21k * 0.95,
        "24 Quilates": p_24k * 0.95
    }
    
    # Generamos la imagen
    imagen_bytes = generar_imagen_todos_los_quilates(precios_con_descuento)
    
    st.success("¡Cálculos aplicados e Imagen generada con éxito!")
    st.image(imagen_bytes, caption="Imagen lista para descargar.", use_column_width=True)
    
    nombre_archivo = f"VendeTuOroMx_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    st.download_button(
        label="📥 Descargar Imagen",
        data=imagen_bytes,
        file_name=nombre_archivo,
        mime="image/png"
    )
