# app.py

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# Importar módulos propios
from config import ELEMENT_TYPES, FORM_CONFIGS, DEFAULT_LAT, DEFAULT_LON
from utils import get_next_element_code, image_to_base64, create_kml
from map_utils import create_map
from data_manager import create_automatic_connections, delete_element, delete_connection

# Inicialización de session state
defaults = {
    'elements': [],
    'connections': [],
    'element_counter': {k: 0 for k in ELEMENT_TYPES.keys()},
    'clicked_coords': None,
    'selected_element_type': 'poste',
    'map_center': [DEFAULT_LAT, DEFAULT_LON],
    'map_zoom': 15
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# CSS personalizado
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; font-weight: bold; }
    .section-header { font-size: 1.5rem; color: #2e86ab; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #2e86ab; }
    .element-card { background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #2e86ab; margin-bottom: 1rem; }
    .coordinates-card { background-color: #e8f4fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2e86ab; margin-bottom: 1rem; }
    .photo-option { background-color: #e8f4fd; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<div class="main-header">📡 Site Survey - Telecomunicaciones</div>', unsafe_allow_html=True)

# Proyecto y tarea
st.markdown('<div class="section-header">📋 Información del Proyecto</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
proyecto = col1.text_input("**Nombre del Proyecto**", placeholder="Ingrese el nombre del proyecto")
tarea = col2.text_input("**Nombre de la Tarea**", placeholder="Ingrese el nombre de la tarea")

# Selección de tipo de elemento
st.markdown('<div class="section-header">📍 Seleccionar Tipo de Elemento</div>', unsafe_allow_html=True)
cols = st.columns(4)
for i, (tipo, config) in enumerate(ELEMENT_TYPES.items()):
    with cols[i]:
        if st.button(
            f"**{config['icon']} {config['name']}**",
            use_container_width=True,
            type="primary" if st.session_state.selected_element_type == tipo else "secondary"
        ):
            st.session_state.selected_element_type = tipo
            st.rerun()

if st.session_state.selected_element_type:
    st.success(f"✅ **Elemento seleccionado:** {ELEMENT_TYPES[st.session_state.selected_element_type]['name']} - Haz clic en el mapa para ubicarlo")

# Mapa y formulario
col_map, col_form = st.columns([2, 1])

with col_map:
    st.markdown('<div class="section-header">🗺️ Mapa Interactivo</div>', unsafe_allow_html=True)
    mapa = create_map(
        st.session_state.map_center,
        st.session_state.map_zoom,
        st.session_state.clicked_coords,
        st.session_state.elements,
        st.session_state.connections
    )
    map_data = st_folium(mapa, width=700, height=500, returned_objects=["last_clicked"], key="main_map")
    
    if map_data and map_data.get("last_clicked"):
        st.session_state.clicked_coords = map_data["last_clicked"]
        st.success(f"📍 Coordenadas capturadas: {st.session_state.clicked_coords['lat']:.6f}, {st.session_state.clicked_coords['lng']:.6f}")

with col_form:
    st.markdown('<div class="section-header">📝 Capturar Elemento</div>', unsafe_allow_html=True)
    
    if st.session_state.clicked_coords:
        lat = st.session_state.clicked_coords['lat']
        lon = st.session_state.clicked_coords['lng']
        st.markdown('<div class="coordinates-card">', unsafe_allow_html=True)
        st.subheader("📍 Coordenadas Capturadas")
        st.write(f"**Latitud:** {lat:.6f}")
        st.write(f"**Longitud:** {lon:.6f}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ **Haz clic en el mapa** para seleccionar la ubicación")
        lat, lon = DEFAULT_LAT, DEFAULT_LON

    # Mostrar formulario si todo está listo
    show_form = st.session_state.selected_element_type and st.session_state.clicked_coords and proyecto and tarea
    if show_form:
        tipo = st.session_state.selected_element_type
        config = ELEMENT_TYPES[tipo]
        with st.form(f"form_{tipo}", clear_on_submit=True):
            st.markdown('<div class="element-card">', unsafe_allow_html=True)
            st.subheader(f"{config['icon']} Datos del {config['name']}")
            
            nombre = get_next_element_code(proyecto, tipo, st.session_state.element_counter)
            st.text_input("**Nombre**", value=nombre, disabled=True)
            
            # Campos dinámicos
            form_data = {}
            for field_type, label, key, options in FORM_CONFIGS[tipo]['fields']:
                if field_type == 'select':
                    form_data[key] = st.selectbox(f"**{label}**", options)
                elif field_type == 'text':
                    form_data[key] = st.text_input(f"**{label}**")
                elif field_type == 'textarea':
                    form_data[key] = st.text_area(f"**{label}**")
            
            # Foto
            st.markdown('<div class="photo-option">', unsafe_allow_html=True)
            st.write("**📸 Agregar Foto**")
            foto_option = st.radio("Selecciona opción:", ["Tomar foto con cámara", "Subir imagen existente"], key=f"foto_{tipo}")
            if foto_option == "Tomar foto con cámara":
                foto = st.camera_input("**Tomar foto**", key=f"camera_{tipo}")
            else:
                foto = st.file_uploader("**Subir imagen**", type=['jpg', 'jpeg', 'png'], key=f"upload_{tipo}")
            foto_data = image_to_base64(foto) if foto else None
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.form_submit_button("💾 Guardar", use_container_width=True):
                nuevo_elemento = {
                    'id': str(uuid.uuid4()),
                    'nombre': nombre,
                    'tipo': tipo,
                    'proyecto': proyecto,
                    'tarea': tarea,
                    'latitud': lat,
                    'longitud': lon,
                    'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'foto': foto is not None,
                    'foto_data': foto_data,
                    **form_data
                }
                st.session_state.elements.append(nuevo_elemento)
                st.session_state.connections = create_automatic_connections(st.session_state.elements, st.session_state.connections)
                st.session_state.clicked_coords = None
                st.success(f"✅ **{config['name']} guardado exitosamente!**")
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if not proyecto or not tarea:
            st.error("⚠️ **Completa el nombre del proyecto y la tarea**")
        elif not st.session_state.clicked_coords:
            st.info("👆 **Selecciona un tipo de elemento y haz clic en el mapa para comenzar**")

# Gestión de datos
st.markdown('<div class="section-header">📊 Gestión de Datos</div>', unsafe_allow_html=True)

# Elementos
st.subheader("📋 Elementos Registrados")
if st.session_state.elements:
    df_elements = pd.DataFrame(st.session_state.elements)
    st.dataframe(df_elements, use_container_width=True, height=300)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🗑️ Limpiar Todos", use_container_width=True):
            st.session_state.elements.clear()
            st.session_state.connections.clear()
            st.session_state.element_counter = {k: 0 for k in ELEMENT_TYPES.keys()}
            st.session_state.clicked_coords = None
            st.rerun()
    with col2:
        if st.button("📥 Descargar CSV Elementos", use_container_width=True):
            csv = df_elements.to_csv(index=False)
            st.download_button(
                label="📥 Descargar",
                data=csv,
                file_name=f"elementos_{proyecto}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="download_elements"
            )
    with col3:
        # Eliminar elemento individual
        nombres = [e['nombre'] for e in st.session_state.elements]
        if nombres:
            selected = st.selectbox("Selecciona elemento", nombres, key="del_elem_select")
            if st.button("❌ Eliminar", key="del_elem_btn"):
                st.session_state.elements, st.session_state.connections = delete_element(
                    st.session_state.elements, st.session_state.connections, selected
                )
                st.rerun()
else:
    st.info("📝 No hay elementos registrados aún")

# Conexiones
st.subheader("🔗 Conexiones")
if st.session_state.connections:
    df_connections = pd.DataFrame(st.session_state.connections)
    st.dataframe(df_connections, use_container_width=True, height=300)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🗑️ Limpiar Conexiones", use_container_width=True, key="clear_conn"):
            st.session_state.connections.clear()
            st.rerun()
    with col2:
        csv_conn = df_connections.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV Conexiones",
            data=csv_conn,
            file_name=f"conexiones_{proyecto}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_conn"
        )
    with col3:
        # Eliminar conexión individual
        conn_list = [f"{c['elemento_a']} - {c['elemento_b']}" for c in st.session_state.connections]
        if conn_list:
            selected_conn = st.selectbox("Selecciona conexión", conn_list, key="del_conn_select")
            idx = conn_list.index(selected_conn)
            conn_id = st.session_state.connections[idx]['id']
            if st.button("❌ Eliminar", key="del_conn_btn"):
                st.session_state.connections = delete_connection(st.session_state.connections, conn_id)
                st.rerun()
else:
    st.info("🔗 No hay conexiones registradas aún")

# Exportar KML
st.markdown('<div class="section-header">📤 Exportar KML</div>', unsafe_allow_html=True)
if st.session_state.elements:
    if st.button("🗺️ Generar KML", use_container_width=True):
        kml = create_kml(st.session_state.elements, st.session_state.connections)
        kml_bytes = kml.kml().encode('utf-8')
        st.download_button(
            label="⬇️ Descargar KML",
            data=kml_bytes,
            file_name=f"site_survey_{proyecto}_{datetime.now().strftime('%Y%m%d_%H%M')}.kml",
            mime="application/vnd.google-earth.kml+xml",
            use_container_width=True
        )
        st.success("✅ KML generado correctamente")
else:
    st.warning("⚠️ No hay elementos para exportar")

# Sidebar con estadísticas
st.sidebar.markdown('<div class="section-header">📈 Resumen</div>', unsafe_allow_html=True)
if st.session_state.elements:
    total = len(st.session_state.elements)
    st.sidebar.markdown(f'<div class="stats-card"><h3>{total}</h3><p>Elementos</p></div>', unsafe_allow_html=True)
    for tipo in ELEMENT_TYPES.keys():
        count = sum(1 for e in st.session_state.elements if e['tipo'] == tipo)
        st.sidebar.write(f"{ELEMENT_TYPES[tipo]['icon']} {ELEMENT_TYPES[tipo]['name']}: {count}")
if st.session_state.connections:
    total_conn = len(st.session_state.connections)
    dist_total = sum(c['distancia_metros'] for c in st.session_state.connections)
    st.sidebar.markdown(f'<div class="stats-card"><h3>{total_conn}</h3><p>Conexiones</p></div>', unsafe_allow_html=True)
    st.sidebar.write(f"📏 Distancia total: {dist_total:.2f} m")