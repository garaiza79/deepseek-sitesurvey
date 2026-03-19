# map_utils.py

import folium
from streamlit_folium import st_folium
import streamlit as st
from config import ELEMENT_TYPES, CONNECTION_COLORS

def create_map(center, zoom, clicked_coords, elements, connections):
    """Crea un mapa de Folium con todos los elementos."""
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True)
    
    # Capas base
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        attr='OpenStreetMap contributors'
    ).add_to(m)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        name='OpenTopoMap',
        attr='OpenTopoMap contributors'
    ).add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Satélite',
        attr='Esri'
    ).add_to(m)
    
    # Marcador temporal (clic del usuario)
    if clicked_coords:
        folium.Marker(
            [clicked_coords['lat'], clicked_coords['lng']],
            popup="📍 Ubicación seleccionada",
            tooltip="Haz clic aquí para confirmar",
            icon=folium.Icon(color='purple', icon='star', prefix='fa')
        ).add_to(m)
    
    # Elementos existentes
    for element in elements:
        tipo = element['tipo']
        config = ELEMENT_TYPES.get(tipo, {})
        color = config.get('color', 'gray')
        icon_name = {
            'poste': 'flag',
            'handhole': 'info-circle',
            'cierre': 'link',
            'edificio': 'building'
        }.get(tipo, 'question')
        
        popup_html = f"""
        <div style="font-family:Arial;max-width:400px">
            <h4 style="color:#2e86ab;margin-bottom:10px;font-size:18px">{element['nombre']}</h4>
            <p><strong>Tipo:</strong> {element['tipo']}</p>
            <p><strong>Proyecto:</strong> {element['proyecto']}</p>
            <p><strong>Fecha:</strong> {element['fecha']}</p>
        """
        if element.get('foto_data'):
            popup_html += f'<img src="{element["foto_data"]}" style="max-width:100%;height:auto;border-radius:5px;margin-top:10px">'
        popup_html += "</div>"
        
        folium.Marker(
            [element['latitud'], element['longitud']],
            popup=folium.Popup(popup_html, max_width=500),
            tooltip=f"📌 {element['nombre']} - {element['tipo']}",
            icon=folium.Icon(color=color, icon=icon_name, prefix='fa')
        ).add_to(m)
    
    # Conexiones
    for conn in connections:
        elem_a = next((e for e in elements if e['nombre'] == conn['elemento_a']), None)
        elem_b = next((e for e in elements if e['nombre'] == conn['elemento_b']), None)
        if elem_a and elem_b:
            folium.PolyLine(
                locations=[[elem_a['latitud'], elem_a['longitud']], [elem_b['latitud'], elem_b['longitud']]],
                color=CONNECTION_COLORS.get(conn['tipo_construccion'], 'blue'),
                weight=4, opacity=0.8,
                popup=f"<b>Conexión:</b> {conn['elemento_a']} - {conn['elemento_b']}<br><b>Tipo:</b> {conn['tipo_construccion']}<br><b>Distancia:</b> {conn['distancia_metros']} m"
            ).add_to(m)
    
    folium.LayerControl().add_to(m)
    return m