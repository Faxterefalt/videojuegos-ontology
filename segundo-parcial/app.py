from flask import Flask, render_template, request, jsonify
from buscador_semantico import BuscadorSemantico
import os
import socket

app = Flask(__name__)

# Configuración
OWL_PATH = r"c:\Users\FABIAN\Desktop\GALLETAS\WEB SEMÁNTICAS\videojuegos-ontology\segundo-parcial\videojuegos.owl"
buscador = BuscadorSemantico(OWL_PATH)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/poblar', methods=['POST'])
def poblar():
    """Endpoint para poblar la ontología"""
    try:
        data = request.get_json()
        limite = int(data.get('limite', 10))
        buscador.poblar_ontologia(limite)
        return jsonify({'success': True, 'message': f'{limite} videojuegos agregados'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/buscar/titulo', methods=['GET'])
def buscar_titulo():
    """Buscar por título"""
    termino = request.args.get('q', '')
    resultados = buscador.buscar_por_titulo(termino)
    return jsonify(_formatear_resultados(resultados))

@app.route('/api/buscar/anio', methods=['GET'])
def buscar_anio():
    """Buscar por año"""
    anio = request.args.get('anio', type=int)
    resultados = buscador.buscar_por_anio(anio)
    return jsonify(_formatear_resultados(resultados))

@app.route('/api/buscar/general', methods=['GET'])
def buscar_general():
    """Búsqueda general en todos los campos"""
    termino = request.args.get('q', '')
    if not termino:
        return jsonify({'success': False, 'error': 'Término vacío'}), 400
    resultados = buscador.buscar_general(termino)
    return jsonify(_formatear_resultados(resultados))

@app.route('/api/buscar/desarrollador', methods=['GET'])
def buscar_desarrollador():
    """Buscar por desarrollador"""
    termino = request.args.get('q', '')
    resultados = buscador.buscar_por_desarrollador(termino)
    return jsonify(_formatear_resultados(resultados))

@app.route('/api/listar', methods=['GET'])
def listar_todos():
    """Listar todos los videojuegos"""
    resultados = buscador.listar_todos()
    return jsonify(_formatear_resultados(resultados))

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """Obtener estadísticas generales"""
    query = """
    SELECT (COUNT(?game) as ?total) 
    WHERE { ?game rdf:type vg:Videojuego }
    """
    total = list(buscador.graph.query(query))[0][0]
    
    query_generos = """
    SELECT ?genero (COUNT(?game) as ?count)
    WHERE {
        ?game vg:tieneGenero ?gen .
        ?gen rdfs:label ?genero
    }
    GROUP BY ?genero
    ORDER BY DESC(?count)
    LIMIT 5
    """
    generos = [{'nombre': str(row[0]), 'count': int(row[1])} 
               for row in buscador.graph.query(query_generos)]
    
    return jsonify({
        'total': int(total),
        'generos_populares': generos
    })

def _formatear_resultados(resultados):
    """Convierte resultados SPARQL a formato JSON"""
    data = []
    for row in resultados:
        # Procesar años (pueden ser múltiples separados por coma)
        anios = None
        if hasattr(row, 'anios') and row.anios:
            anios_str = str(row.anios)
            anios = sorted([int(a.strip()) for a in anios_str.split(',') if a.strip().isdigit()])
        
        # Procesar géneros (pueden ser múltiples separados por coma)
        generos = None
        if hasattr(row, 'generos') and row.generos:
            generos_str = str(row.generos)
            generos = [g.strip() for g in generos_str.split(',') if g.strip()]
        
        # Procesar desarrollador
        desarrollador = None
        if hasattr(row, 'dev') and row.dev:
            desarrollador = str(row.dev)
        
        item = {
            'titulo': str(row.titulo) if hasattr(row, 'titulo') else '',
            'anios': anios,  # Array de años
            'desarrollador': desarrollador,
            'generos': generos,  # Array de géneros
            'uri': str(row.game) if hasattr(row, 'game') else ''
        }
        data.append(item)
    return {'success': True, 'data': data, 'count': len(data)}

if __name__ == '__main__':
    def encontrar_puerto(puerto_inicial=5001, max_intentos=10):
        for puerto in range(puerto_inicial, puerto_inicial + max_intentos):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('127.0.0.1', puerto))
                sock.close()
                return puerto
            except OSError:
                continue
        return None
    
    puerto = encontrar_puerto()
    
    if puerto:
        print(f"\n{'='*60}")
        print(f" Servidor iniciado en http://127.0.0.1:{puerto}")
        print(f"{'='*60}\n")
        app.run(debug=True, port=puerto, host='127.0.0.1')
    else:
        print("No se pudo encontrar un puerto disponible")
        print("   Intenta cerrar otras aplicaciones y vuelve a intentar")
