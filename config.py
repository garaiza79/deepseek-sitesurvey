# config.py

# Tipos de elementos con sus códigos e íconos
ELEMENT_TYPES = {
    'poste': {'icon': '📏', 'name': 'Poste', 'code': 'P', 'color': 'red'},
    'handhole': {'icon': '🕳️', 'name': 'Handhole', 'code': 'HH', 'color': 'green'},
    'cierre': {'icon': '🔗', 'name': 'Cierre de Empalme', 'code': 'CE', 'color': 'blue'},
    'edificio': {'icon': '🏢', 'name': 'Edificio', 'code': 'BLD', 'color': 'orange'}
}

# Colores para conexiones
CONNECTION_COLORS = {
    'Aerial Route': 'red',
    'ADSS': 'blue',
    'Ducto': 'blue'
}

# Configuración de formularios para cada tipo de elemento
FORM_CONFIGS = {
    'poste': {
        'fields': [
            ('select', 'Dueño del Poste', 'dueno', ["CFE", "ATC", "Flo Networks", "Maxcom", "XC Networks", "Municipio", "Parque Industrial", "Privado"]),
            ('select', 'Usado por', 'usado_por', ["ATC", "Flo Networks", "Maxcom", "XC Networks", "Otro"]),
            ('select', 'Altura del Poste (m)', 'altura', list(range(6, 16))),
            ('select', 'Material del Poste', 'material', ["Concreto", "Madera", "Metal"]),
            ('text', 'ID de CFE', 'id_cfe', None),
            ('select', 'Tipo de construcción', 'tipo_construccion', ["Poste nuevo", "Poste ya utilizado por Infra", "Poste sin utilizar por nuestra Infra"])
        ]
    },
    'handhole': {
        'fields': [
            ('select', 'Dueño del Handhole', 'dueno', ["CFE", "ATC", "Flo Networks", "Maxcom", "XC Networks", "Municipio", "Parque Industrial", "Privado"]),
            ('select', 'Usado por', 'usado_por', ["ATC", "Flo Networks", "Maxcom", "XC Networks", "Otro"]),
            ('select', 'Dimensiones de Handhole', 'dimensiones', ["24x24x24", "24x36x24", "48x48x48", "otro"]),
            ('select', 'Instalado en', 'instalado_en', ["Banqueta", "Arroyo", "Propiedad Privada"])
        ]
    },
    'cierre': {
        'fields': [
            ('select', 'Cierre nuevo o existente', 'tipo_cierre', ["Nuevo", "Existente"]),
            ('text', 'Nombre del Cierre', 'nombre_cierre', None)
        ]
    },
    'edificio': {
        'fields': [
            ('text', 'Dirección Completa', 'direccion', None),
            ('text', 'Nombre de Edificio', 'nombre_edificio', None),
            ('text', 'Piso del cliente', 'piso_cliente', None),
            ('text', 'Suite del Cliente', 'suite_cliente', None),
            ('textarea', 'Datos Adicionales', 'datos_adicionales', None)
        ]
    }
}

# Coordenadas por defecto (CDMX)
DEFAULT_LAT, DEFAULT_LON = 19.4326, -99.1332