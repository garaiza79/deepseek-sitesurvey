# data_manager.py

import uuid
from datetime import datetime
import streamlit as st
from utils import calculate_distance

def create_automatic_connections(elements, connections):
    """Crea conexiones automáticas entre elementos consecutivos."""
    if len(elements) < 2:
        return connections
    
    sorted_elements = sorted(elements, key=lambda x: x['fecha'])
    new_connections = connections.copy()
    
    for i in range(len(sorted_elements) - 1):
        elem_a = sorted_elements[i]
        elem_b = sorted_elements[i + 1]
        
        # Verificar si ya existe la conexión
        exists = any(
            (c['elemento_a'] == elem_a['nombre'] and c['elemento_b'] == elem_b['nombre']) or
            (c['elemento_a'] == elem_b['nombre'] and c['elemento_b'] == elem_a['nombre'])
            for c in connections
        )
        if exists:
            continue
        
        tipos = [elem_a['tipo'], elem_b['tipo']]
        if 'handhole' in tipos or ('edificio' in tipos and 'handhole' in tipos):
            tipo_construccion = "Ducto"
        else:
            tipo_construccion = "Aerial Route"
        
        distancia = calculate_distance(
            elem_a['latitud'], elem_a['longitud'],
            elem_b['latitud'], elem_b['longitud']
        )
        
        new_connections.append({
            'id': str(uuid.uuid4()),
            'elemento_a': elem_a['nombre'],
            'elemento_b': elem_b['nombre'],
            'tipo_construccion': tipo_construccion,
            'infraestructura': 'existente',
            'distancia_metros': round(distancia, 2),
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'automatica': True
        })
    return new_connections

def delete_element(elements, connections, element_name):
    """Elimina un elemento y sus conexiones relacionadas."""
    new_elements = [e for e in elements if e['nombre'] != element_name]
    new_connections = [c for c in connections 
                      if c['elemento_a'] != element_name and c['elemento_b'] != element_name]
    return new_elements, new_connections

def delete_connection(connections, connection_id):
    """Elimina una conexión por su ID."""
    return [c for c in connections if c['id'] != connection_id]