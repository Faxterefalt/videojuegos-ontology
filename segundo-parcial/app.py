from flask import Flask, render_template, request, jsonify
from buscador_semantico import BuscadorSemantico, VG
from hybrid_search import HybridSearch
from multilingual import traductor_global
from rdflib import RDF
import os
import socket

app = Flask(__name__)

# NUEVO: Habilitar compresión de respuestas
from flask_compress import Compress
compress = Compress()
compress.init_app(app)

# Configuración
OWL_PATH = r"c:\Users\FABIAN\Desktop\GALLETAS\WEB SEMÁNTICAS\videojuegos-ontology\segundo-parcial\videojuegos.owl"
buscador = BuscadorSemantico(OWL_PATH)
hybrid_search = HybridSearch(buscador)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/verificar-dbpedia', methods=['GET'])
def verificar_dbpedia():
    """Verificar conexión con DBpedia"""
    try:
        disponible = buscador.verificar_conexion_dbpedia()
        
        # Contar videojuegos locales correctamente
        count = sum(1 for _ in buscador.graph.triples((None, RDF.type, VG.Videojuego)))
        
        return jsonify({
            'success': True,
            'dbpedia_disponible': disponible,
            'videojuegos_locales': count,
            'mensaje': 'DBpedia disponible' if disponible else 'DBpedia no disponible - usando datos locales'
        })
    except Exception as e:
        print(f"Error en verificar_dbpedia: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'dbpedia_disponible': False
        }), 500

@app.route('/api/poblar', methods=['POST'])
def poblar():
    """Endpoint para poblar la ontología"""
    try:
        data = request.get_json()
        limite = int(data.get('limite', 10))
        
        print(f"\n{'='*60}")
        print(f"Solicitud de población recibida: {limite} videojuegos")
        print(f"{'='*60}\n")
        
        # Contar antes de poblar
        count_antes = sum(1 for _ in buscador.graph.triples((None, RDF.type, VG.Videojuego)))
        print(f"Videojuegos antes: {count_antes}")
        
        # Poblar ontología
        buscador.poblar_ontologia(limite)
        
        # Contar después de poblar correctamente
        count_despues = sum(1 for _ in buscador.graph.triples((None, RDF.type, VG.Videojuego)))
        print(f"Videojuegos después: {count_despues}")
        
        agregados = count_despues - count_antes
        
        return jsonify({
            'success': True, 
            'message': f'{agregados} videojuegos nuevos agregados. Total en ontología: {count_despues}',
            'total': count_despues,
            'agregados': agregados
        })
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n✗ Error en población:")
        print(error_detail)
        return jsonify({
            'success': False, 
            'error': str(e),
            'detail': 'Ver consola del servidor para detalles'
        }), 500

@app.route('/api/buscar/titulo', methods=['GET'])
def buscar_titulo():
    """Buscar por título con búsqueda híbrida"""
    try:
        termino = request.args.get('q', '')
        modo_hibrido = request.args.get('hybrid', 'true').lower() == 'true'
        
        if modo_hibrido:
            # Búsqueda híbrida (local + DBpedia)
            resultado = hybrid_search.buscar_titulo_hibrido(termino)
            
            if resultado['success']:
                return jsonify(_formatear_resultados_hibridos(resultado))
            else:
                return jsonify({'success': False, 'data': [], 'count': 0, 'message': resultado['message']})
        else:
            # Solo búsqueda local
            resultados = buscador.buscar_por_titulo(termino)
            return jsonify(_formatear_resultados(resultados))
            
    except Exception as e:
        print(f"Error en buscar_titulo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/buscar/anio', methods=['GET'])
def buscar_anio():
    """Buscar por año"""
    try:
        anio = request.args.get('anio', type=int)
        resultados = buscador.buscar_por_anio(anio)
        return jsonify(_formatear_resultados(resultados))
    except Exception as e:
        print(f"Error en buscar_anio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/buscar/general', methods=['GET'])
def buscar_general():
    """Búsqueda general OPTIMIZADA"""
    try:
        termino = request.args.get('q', '')
        modo_hibrido = request.args.get('hybrid', 'true').lower() == 'true'
        
        if not termino:
            return jsonify({'success': False, 'error': 'Término vacío'}), 400
        
        # OPTIMIZACIÓN: Límite de longitud
        if len(termino) > 100:
            return jsonify({'success': False, 'error': 'Término muy largo'}), 400
        
        if modo_hibrido:
            resultado = hybrid_search.buscar_general_hibrido(termino)
            
            if resultado['success']:
                response = jsonify(_formatear_resultados_hibridos(resultado))
                # NUEVO: Agregar headers de caché
                response.cache_control.max_age = 180  # 3 minutos
                return response
            else:
                return jsonify({'success': False, 'data': [], 'count': 0, 'message': resultado['message']})
        else:
            resultados = buscador.buscar_general(termino)
            return jsonify(_formatear_resultados(resultados))
            
    except Exception as e:
        print(f"Error en buscar_general: {str(e)}")
        return jsonify({'success': False, 'error': 'Error en búsqueda'}), 500

@app.route('/api/buscar/desarrollador', methods=['GET'])
def buscar_desarrollador():
    """Buscar por desarrollador con modo híbrido"""
    try:
        termino = request.args.get('q', '')
        modo_hibrido = request.args.get('hybrid', 'true').lower() == 'true'
        
        if modo_hibrido:
            # Búsqueda híbrida
            resultado = hybrid_search.buscar_desarrollador_hibrido(termino)
            
            if resultado['success']:
                return jsonify(_formatear_resultados_hibridos(resultado))
            else:
                return jsonify({'success': False, 'data': [], 'count': 0, 'message': resultado['message']})
        else:
            # Solo búsqueda local
            resultados = buscador.buscar_por_desarrollador(termino)
            return jsonify(_formatear_resultados(resultados))
            
    except Exception as e:
        print(f"Error en buscar_desarrollador: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agregar-desde-dbpedia', methods=['POST'])
def agregar_desde_dbpedia():
    """Agrega juegos encontrados en DBpedia a la ontología local - MEJORADO"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
        
        juegos = data.get('juegos', [])
        
        if not juegos or not isinstance(juegos, list):
            return jsonify({'success': False, 'message': 'No hay juegos para agregar o formato inválido'}), 400
        
        print(f"\n{'='*60}")
        print(f"SOLICITUD DE AGREGAR JUEGOS")
        print(f"{'='*60}")
        print(f"Cantidad de juegos recibidos: {len(juegos)}")
        
        # Validar estructura de cada juego
        juegos_validos = []
        for idx, juego in enumerate(juegos):
            if isinstance(juego, dict) and ('game' in juego or 'uri' in juego):
                # Normalizar estructura
                juego_normalizado = {
                    'game': juego.get('game') or juego.get('uri', ''),
                    'titulo': juego.get('titulo', 'Sin título'),
                    'anios': juego.get('anios', []),
                    'desarrollador': juego.get('desarrollador'),
                    'generos': juego.get('generos', [])
                }
                
                if juego_normalizado['game']:
                    juegos_validos.append(juego_normalizado)
                    print(f"  ✓ Juego {idx+1}: {juego_normalizado['titulo']}")
                else:
                    print(f"  ✗ Juego {idx+1}: Sin URI válida")
            else:
                print(f"  ✗ Juego {idx+1}: Estructura inválida")
        
        if not juegos_validos:
            return jsonify({
                'success': False, 
                'message': 'Ningún juego tiene una estructura válida'
            }), 400
        
        print(f"\nJuegos válidos a procesar: {len(juegos_validos)}")
        print(f"{'='*60}\n")
        
        # Intentar agregar los juegos
        count = hybrid_search.agregar_juegos_dbpedia_a_ontologia(juegos_validos)
        
        # Contar total después de agregar
        total = sum(1 for _ in buscador.graph.triples((None, RDF.type, VG.Videojuego)))
        
        if count > 0:
            return jsonify({
                'success': True,
                'message': f'✓ {count} juego(s) agregado(s) exitosamente. Total en ontología: {total}',
                'agregados': count,
                'total': total
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No se pudieron agregar juegos. Es posible que ya existan en la ontología.',
                'agregados': 0,
                'total': total
            })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"\n✗ ERROR EN AGREGAR DESDE DBPEDIA:")
        print(error_detail)
        
        return jsonify({
            'success': False, 
            'error': str(e),
            'detail': 'Ver consola del servidor para detalles completos'
        }), 500

@app.route('/api/listar', methods=['GET'])
def listar_todos():
    """Listar todos los videojuegos"""
    try:
        resultados = buscador.listar_todos()
        return jsonify(_formatear_resultados(resultados))
    except Exception as e:
        print(f"Error en listar_todos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """Obtener estadísticas generales"""
    try:
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
    except Exception as e:
        print(f"Error en estadisticas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/traducir', methods=['GET'])
def traducir():
    """Endpoint para traducir términos"""
    try:
        termino = request.args.get('q', '')
        
        if not termino:
            return jsonify({'success': False, 'error': 'Término vacío'}), 400
        
        idioma = traductor_global.detectar_idioma(termino)
        expansiones = traductor_global.expandir_con_traducciones(termino)
        
        # Obtener traducciones específicas
        traducciones_en = traductor_global.traducir_es_a_en(termino)
        traducciones_es = traductor_global.traducir_en_a_es(termino)
        
        return jsonify({
            'success': True,
            'termino_original': termino,
            'idioma_detectado': idioma,
            'traducciones_ingles': traducciones_en,
            'traducciones_espanol': traducciones_es,
            'todas_expansiones': expansiones
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/estadisticas-multilingue', methods=['GET'])
def estadisticas_multilingue():
    """Estadísticas del sistema multilingüe"""
    try:
        stats = traductor_global.obtener_estadisticas()
        return jsonify({
            'success': True,
            'estadisticas': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def _formatear_resultados(resultados):
    """Convierte resultados SPARQL a formato JSON"""
    try:
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
                'anios': anios,
                'desarrollador': desarrollador,
                'generos': generos,
                'uri': str(row.game) if hasattr(row, 'game') else ''
            }
            data.append(item)
        return {'success': True, 'data': data, 'count': len(data)}
    except Exception as e:
        print(f"Error en _formatear_resultados: {str(e)}")
        return {'success': False, 'data': [], 'count': 0, 'error': str(e)}

def _formatear_resultados_hibridos(resultado):
    """Formatea resultados de búsqueda híbrida - NUEVA LÓGICA"""
    try:
        if resultado['source'] == 'hybrid':
            # NUEVO: Resultados combinados (local + DBpedia)
            data_local = []
            data_dbpedia = []
            
            # Procesar resultados locales
            if resultado['local']['count'] > 0:
                for row in resultado['local']['results']:
                    # Procesar años
                    anios = None
                    if hasattr(row, 'anios') and row.anios:
                        anios_str = str(row.anios)
                        anios = sorted([int(a.strip()) for a in anios_str.split(',') if a.strip().isdigit()])
                    
                    # Procesar géneros
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
                        'anios': anios,
                        'desarrollador': desarrollador,
                        'generos': generos,
                        'uri': str(row.game) if hasattr(row, 'game') else '',
                        'source': 'local'
                    }
                    data_local.append(item)
            
            # Procesar resultados de DBpedia
            if resultado['dbpedia']['count'] > 0:
                data_dbpedia = resultado['dbpedia']['results']
            
            return {
                'success': True,
                'source': 'hybrid',
                'local': data_local,
                'dbpedia': data_dbpedia,
                'count_local': len(data_local),
                'count_dbpedia': len(data_dbpedia),
                'count': len(data_local) + len(data_dbpedia),
                'message': resultado['message']
            }
        
        elif resultado['source'] == 'local':
            # Resultados solo locales (fallback)
            return _formatear_resultados(resultado['results'])
        
        elif resultado['source'] == 'dbpedia':
            # Resultados solo DBpedia (fallback)
            return {
                'success': True,
                'data': resultado['results'],
                'count': resultado['count'],
                'source': 'dbpedia',
                'message': resultado['message']
            }
        else:
            return {
                'success': False,
                'data': [],
                'count': 0,
                'message': resultado['message']
            }
    except Exception as e:
        print(f"Error en _formatear_resultados_hibridos: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'data': [], 'count': 0, 'error': str(e)}

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
        print(f" SERVIDOR INICIADO")
        print(f"{'='*60}")
        print(f"  URL: http://127.0.0.1:{puerto}")
        print(f"  Modo: Debug")
        print(f"  Ontología: {OWL_PATH}")
        
        # Mostrar cantidad inicial de videojuegos
        count_inicial = sum(1 for _ in buscador.graph.triples((None, RDF.type, VG.Videojuego)))
        print(f"  Videojuegos en ontología: {count_inicial}")
        print(f"{'='*60}\n")
        
        app.run(debug=True, port=puerto, host='127.0.0.1')
    else:
        print("✗ No se pudo encontrar un puerto disponible")
        print("   Intenta cerrar otras aplicaciones y vuelve a intentar")
