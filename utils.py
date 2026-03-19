# utils.py

import uuid
import math
import io
import base64
from datetime import datetime
from PIL import Image
import simplekml
import streamlit as st

def get_next_element_code(project_name, element_type, counter_dict):
    """Genera el siguiente código para un tipo de elemento."""
    counter_dict[element_type] += 1
    from config import ELEMENT_TYPES
    return f"{project_name}{ELEMENT_TYPES[element_type]['code']}{counter_dict[element_type]:03d}"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcula la distancia en metros entre dos puntos geográficos."""
    R = 6371000
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def image_to_base64(image):
    """Convierte una imagen a base64 para incluir en KML."""
    if not image:
        return None
    try:
        pil_image = Image.open(image) if hasattr(image, 'read') else image
        target_size = (600, 500)
        ratio = min(target_size[0]/pil_image.size[0], target_size[1]/pil_image.size[1])
        new_size = (int(pil_image.size[0] * ratio), int(pil_image.size[1] * ratio))
        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=90)
        return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return None

def create_kml(elements, connections):
    """Genera un archivo KML con todos los elementos y conexiones."""
    kml = simplekml.Kml()
    from config import ELEMENT_TYPES

    # Elementos
    for element in elements:
        point = kml.newpoint(name=element['nombre'])
        point.coords = [(element['longitud'], element['latitud'])]
        
        desc = f"""<![CDATA[<div style="font-family: Arial; max-width:650px">
            <h3 style="color:#2e86ab;margin-bottom:15px;font-size:28px">{element['nombre']}</h3>
            <table style="width:100%;border-collapse:collapse;font-size:20px">
            <tr><td style="padding:8px;border-bottom:1px solid #eee"><strong>Tipo:</strong></td><td style="padding:8px;border-bottom:1px solid #eee">{element['tipo']}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #eee"><strong>Proyecto:</strong></td><td style="padding:8px;border-bottom:1px solid #eee">{element['proyecto']}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #eee"><strong>Tarea:</strong></td><td style="padding:8px;border-bottom:1px solid #eee">{element['tarea']}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #eee"><strong>Fecha:</strong></td><td style="padding:8px;border-bottom:1px solid #eee">{element['fecha']}</td></tr>
            <tr><td style="padding:8px;border-bottom:1px solid #eee"><strong>Coordenadas:</strong></td><td style="padding:8px;border-bottom:1px solid #eee">{element['latitud']:.6f}, {element['longitud']:.6f}</td></tr>
        """
        
        # Campos específicos por tipo
        specific_fields = {
            'poste': ['dueno', 'usado_por', 'altura', 'material', 'id_cfe', 'tipo_construccion'],
            'handhole': ['dueno', 'usado_por', 'dimensiones', 'instalado_en'],
            'cierre': ['tipo_cierre', 'nombre_cierre'],
            'edificio': ['direccion', 'nombre_edificio', 'piso_cliente', 'suite_cliente', 'datos_adicionales']
        }
        
        for field in specific_fields.get(element['tipo'], []):
            desc += f"<tr><td style='padding:8px;border-bottom:1px solid #eee'><strong>{field.replace('_', ' ').title()}:</strong></td><td style='padding:8px;border-bottom:1px solid #eee'>{element.get(field, '')}</td></tr>"
        
        if element.get('foto_data'):
            desc += f"""<tr><td colspan="2" style="padding:15px;text-align:center">
                <h4 style="font-size:22px;margin-bottom:10px">Foto del Elemento</h4>
                <img src="{element['foto_data']}" style="max-width:600px;max-height:500px;width:auto;height:auto;border-radius:8px;border:2px solid #ddd">
            </td></tr>"""
        
        point.description = desc + "</table></div>]]>"
        
        # Color del icono
        colors = {
            'poste': 'ff0000ff',
            'handhole': 'ff00ff00',
            'cierre': 'ffff0000',
            'edificio': 'ff00ffff'
        }
        point.style.iconstyle.color = colors.get(element['tipo'], 'ffffffff')

    # Conexiones
    for conn in connections:
        elem_a = next((e for e in elements if e['nombre'] == conn['elemento_a']), None)
        elem_b = next((e for e in elements if e['nombre'] == conn['elemento_b']), None)
        if elem_a and elem_b:
            line = kml.newlinestring(name=f"Conexión {conn['elemento_a']} - {conn['elemento_b']}")
            line.coords = [(elem_a['longitud'], elem_a['latitud']), (elem_b['longitud'], elem_b['latitud'])]
            color_map = {
                "Aerial Route": "ff0000ff",
                "ADSS": "ffff0000",
                "Ducto": "ff0000ff"
            }
            line.style.linestyle.color = color_map.get(conn['tipo_construccion'], 'ff0000ff')
            line.style.linestyle.width = 4
    return kml