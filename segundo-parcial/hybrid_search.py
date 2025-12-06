"""
Módulo para búsqueda híbrida (local + online)
Busca primero en la ontología local y luego en DBpedia si no hay resultados
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Literal
from semantic_reasoning import SemanticReasoner
from multilingual import traductor_global
import time

# NUEVO: Importar con manejo de errores
try:
    from intelligent_search import IntelligentSearch
    INTELLIGENT_SEARCH_DISPONIBLE = True
except ImportError:
    INTELLIGENT_SEARCH_DISPONIBLE = False
    print("⚠ Búsqueda inteligente no disponible")

class HybridSearch:
    def __init__(self, buscador_local, sparql_endpoint="http://dbpedia.org/sparql"):
        """
        Inicializa el buscador híbrido
        
        Args:
            buscador_local: Instancia de BuscadorSemantico para búsquedas locales
            sparql_endpoint: URL del endpoint SPARQL de DBpedia
        """
        self.buscador = buscador_local
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(8)  # REDUCIDO de 30 a 8
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0")
        
        self.semantic_reasoner = SemanticReasoner(sparql_endpoint)
        
        # NUEVO: Traductor multilingüe
        self.traductor = traductor_global
        
        # NUEVO: Caché de resultados
        self.cache_resultados = {}
        self.CACHE_TTL = 180  # 3 minutos
        
        # NUEVO: Búsqueda inteligente (solo si está disponible)
        if INTELLIGENT_SEARCH_DISPONIBLE:
            try:
                self.intelligent_search = IntelligentSearch(sparql_endpoint)
                print("✓ Búsqueda inteligente inicializada")
            except Exception as e:
                self.intelligent_search = None
                print(f"✗ Error al inicializar búsqueda inteligente: {e}")
        else:
            self.intelligent_search = None
    
    def buscar_titulo_hibrido(self, termino):
        """OPTIMIZADO con multilingüismo - búsqueda más rápida"""
        print(f"\n{'='*60}")
        print(f"BÚSQUEDA HÍBRIDA MULTILINGÜE: '{termino}'")
        print(f"{'='*60}")
        
        # Detectar idioma
        idioma = self.traductor.detectar_idioma(termino)
        print(f"Idioma detectado: {idioma.upper()}")
        
        # Verificar caché
        cache_key = f"hybrid_{termino.lower()}"
        if cache_key in self.cache_resultados:
            tiempo_cache = self.cache_resultados[cache_key]['timestamp']
            if time.time() - tiempo_cache < self.CACHE_TTL:
                print("✓ Resultados desde caché (instantáneo)")
                return self.cache_resultados[cache_key]['data']
        
        # OPTIMIZACIÓN: Expansión limitada CON traducciones
        terminos_expandidos = self.traductor.expandir_con_traducciones(termino)[:3]
        
        # Solo expandir si es sigla conocida
        if termino.lower() in self.semantic_reasoner.siglas_conocidas:
            terminos_expandidos.extend(
                self.semantic_reasoner.siglas_conocidas[termino.lower()][:2]
            )
        
        # Búsqueda local (RÁPIDA)
        print("\n[1/2] Búsqueda local (rápida)...")
        resultados_locales = self._buscar_local_expandido(terminos_expandidos)
        count_local = len(resultados_locales)

        if count_local > 0:
            print("✓ Resultados locales encontrados. DBpedia omitida para evitar duplicados.")
            resultado_final = {
                'success': True,
                'source': 'hybrid',
                'local': {'results': resultados_locales, 'count': count_local},
                'dbpedia': {'results': [], 'count': 0},
                'total_count': count_local,
                'message': f'{count_local} resultado(s) locales. DBpedia no consultada.',
                'terminos_usados': terminos_expandidos[:2]
            }
            self.cache_resultados[cache_key] = {
                'data': resultado_final,
                'timestamp': time.time()
            }
            return resultado_final
        
        # Búsqueda DBpedia (OPTIMIZADA)
        print("\n[2/2] Búsqueda DBpedia (optimizada)...")
        resultados_dbpedia_raw = []
        
        try:
            # Usar búsqueda rápida con timeout corto
            resultados_dbpedia_raw = self.semantic_reasoner.buscar_semanticamente_dbpedia(
                termino, 
                limite=15  # Reducido de 20 a 15
            )
        except Exception as e:
            print(f"   ⚠ DBpedia timeout (continuando con local)")
        
        resultados_dbpedia = self._formatear_resultados_dbpedia(resultados_dbpedia_raw) if resultados_dbpedia_raw else []
        count_dbpedia = len(resultados_dbpedia)

        resultado_final = {
            'success': True,
            'source': 'hybrid',
            'local': {'results': [], 'count': 0},
            'dbpedia': {'results': resultados_dbpedia, 'count': count_dbpedia},
            'total_count': count_dbpedia,
            'message': 'Sin coincidencias locales. Mostrando resultados de DBpedia.' if count_dbpedia else 'Sin coincidencias locales ni en DBpedia.',
            'terminos_usados': terminos_expandidos[:2]
        }
        self.cache_resultados[cache_key] = {
            'data': resultado_final,
            'timestamp': time.time()
        }
        return resultado_final
    
    def _buscar_local_expandido(self, terminos):
        """OPTIMIZADO - búsqueda local más eficiente"""
        resultados = []
        uris_encontradas = set()
        
        # OPTIMIZACIÓN: Solo buscar con 2 términos máximo
        for termino in terminos[:2]:
            try:
                res = self.buscador.buscar_por_titulo(termino)
                for r in res:
                    uri = str(r.game) if hasattr(r, 'game') else ''
                    if uri and uri not in uris_encontradas:
                        resultados.append(r)
                        uris_encontradas.add(uri)
                        
                # Si ya tenemos 20 resultados, parar
                if len(resultados) >= 20:
                    break
            except:
                pass
        
        return resultados[:20]  # Limitar a 20
    
    def _formatear_resultados_dbpedia(self, resultados_dbpedia):
        """Formatea resultados de DBpedia"""
        resultados_formateados = []
        
        for row in resultados_dbpedia:
            resultado = {
                'game': row['game']['value'],
                'titulo': row['label']['value'],
                'anios': [],
                'desarrollador': None,
                'generos': [],
                'source': 'dbpedia',
                'relevancia': row.get('semantic_score', 0)
            }
            
            # Procesar año
            if 'releaseDate' in row:
                try:
                    year = row['releaseDate']['value'][:4]
                    resultado['anios'] = [int(year)]
                except:
                    pass
            
            # Procesar desarrollador
            if 'developer' in row:
                dev_name = row['developer']['value'].split('/')[-1].replace('_', ' ')
                resultado['desarrollador'] = dev_name
            
            # Procesar género
            if 'genre' in row:
                genre_name = row['genre']['value'].split('/')[-1].replace('_', ' ')
                resultado['generos'] = [genre_name]
            
            resultados_formateados.append(resultado)
        
        return resultados_formateados
    
    def buscar_desarrollador_hibrido(self, termino):
        """Búsqueda híbrida por desarrollador - SIEMPRE ambas fuentes"""
        print(f"\n{'='*60}")
        print(f"BÚSQUEDA SEMÁNTICA POR DESARROLLADOR: '{termino}'")
        print(f"{'='*60}")
        
        terminos_expandidos = self.semantic_reasoner.expandir_consulta(termino)
        
        # Buscar en AMBAS fuentes
        print("\n[1/2] Buscando en ontología local...")
        resultados_locales = self.buscador.buscar_por_desarrollador(termino)

        if resultados_locales:
            print("✓ Resultados locales encontrados. DBpedia omitida.")
            return {
                'success': True,
                'source': 'hybrid',
                'local': {'results': resultados_locales, 'count': len(resultados_locales)},
                'dbpedia': {'results': [], 'count': 0},
                'total_count': len(resultados_locales),
                'message': 'Coincidencias encontradas en la ontología local. No se consulta DBpedia.'
            }
        
        print("\n[2/2] Buscando en DBpedia...")
        resultados_dbpedia = self._buscar_en_dbpedia_por_desarrollador(termino)
        count_dbpedia = len(resultados_dbpedia)

        return {
            'success': True,
            'source': 'hybrid',
            'local': {'results': [], 'count': 0},
            'dbpedia': {'results': resultados_dbpedia, 'count': count_dbpedia},
            'total_count': count_dbpedia,
            'message': 'Sin coincidencias locales. Resultados obtenidos desde DBpedia.' if count_dbpedia else 'Sin coincidencias en ninguna fuente.'
        }

    def buscar_general_hibrido(self, termino):
        """Búsqueda general híbrida CON búsqueda inteligente"""
        print(f"\n{'='*60}")
        print(f"BÚSQUEDA HÍBRIDA: '{termino}'")
        print(f"{'='*60}")
        
        print("→ Explorando ontología local antes de consultar DBpedia...")
        resultados_locales = self.buscador.buscar_general(termino)

        if resultados_locales:
            print("✓ Resultados locales encontrados. No se consultará DBpedia.")
            return {
                'success': True,
                'source': 'hybrid',
                'local': {'results': resultados_locales, 'count': len(resultados_locales)},
                'dbpedia': {'results': [], 'count': 0},
                'total_count': len(resultados_locales),
                'message': 'Coincidencias locales detectadas. Consulta online omitida.'
            }
        
        if self.intelligent_search is not None:
            try:
                print("→ Intentando búsqueda inteligente...")
                # ARREGLADO: Aumentar límite para búsquedas específicas
                limite_busqueda = 30 if any(x in termino.lower() for x in ['recientes', 'nintendo', 'jugadores']) else 20
                
                resultado_inteligente = self.intelligent_search.buscar_inteligente(termino, limite=limite_busqueda)
                
                if resultado_inteligente['success'] and resultado_inteligente['count'] > 0:
                    print(f"\n✓ Búsqueda inteligente EXITOSA")
                    print(f"  Tipo: {resultado_inteligente['analisis']['tipo']}")
                    print(f"  Confianza: {resultado_inteligente['analisis']['confianza']:.2%}")
                    return {
                        'success': True,
                        'source': 'hybrid_intelligent',
                        'local': {'results': [], 'count': 0},
                        'dbpedia': {
                            'results': resultado_inteligente['resultados'],
                            'count': resultado_inteligente['count']
                        },
                        'total_count': resultado_inteligente['count'],
                        'message': f"Sin coincidencias locales. {resultado_inteligente['count']} resultado(s) desde DBpedia (inteligente).",
                        'analisis': resultado_inteligente['analisis']
                    }
                else:
                    print(f"→ Búsqueda inteligente rechazada (confianza: {resultado_inteligente['analisis']['confianza']:.2%})")
            except Exception as e:
                print(f"✗ Error en búsqueda inteligente: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠ Búsqueda inteligente no disponible")
        
        print("\n→ Usando búsqueda híbrida estándar...")
        return self.buscar_titulo_hibrido(termino)
    
    def _buscar_en_dbpedia_por_titulo(self, termino):
        """Busca en DBpedia por título"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            FILTER (lang(?label) = 'en')
            FILTER (CONTAINS(LCASE(?label), LCASE("{termino}")))
            OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        LIMIT 20
        """
        
        return self._ejecutar_query_dbpedia(query)
    
    def _buscar_en_dbpedia_por_desarrollador(self, termino):
        """Busca en DBpedia por desarrollador"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            ?game dbo:developer ?dev .
            ?dev rdfs:label ?devLabel .
            FILTER (lang(?label) = 'en')
            FILTER (CONTAINS(LCASE(?devLabel), LCASE("{termino}")))
            OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
            BIND(?dev as ?developer)
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        LIMIT 20
        """
        
        return self._ejecutar_query_dbpedia(query)
    
    def _buscar_en_dbpedia_general(self, termino):
        """Búsqueda general en DBpedia"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            FILTER (lang(?label) = 'en')
            FILTER (
                CONTAINS(LCASE(?label), LCASE("{termino}"))
            )
            OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        LIMIT 20
        """
        
        return self._ejecutar_query_dbpedia(query)
    
    def _ejecutar_query_dbpedia(self, query):
        """Ejecuta una query en DBpedia y formatea resultados"""
        self.sparql.setQuery(query)
        
        max_intentos = 2
        for intento in range(1, max_intentos + 1):
            try:
                print(f"   Consultando DBpedia (intento {intento}/{max_intentos})...")
                results = self.sparql.query().convert()
                
                if "results" in results and "bindings" in results["results"]:
                    bindings = results["results"]["bindings"]
                    
                    if not bindings:
                        return []
                    
                    # Formatear resultados para que sean compatibles con el formato local
                    resultados_formateados = []
                    for row in bindings:
                        resultado = {
                            'game': row['game']['value'],
                            'titulo': row['label']['value'],
                            'anios': [],
                            'desarrollador': None,
                            'generos': [],
                            'source': 'dbpedia'
                        }
                        
                        # Procesar año
                        if 'releaseDate' in row:
                            try:
                                year = row['releaseDate']['value'][:4]
                                resultado['anios'] = [int(year)]
                            except:
                                pass
                        
                        # Procesar desarrollador
                        if 'developer' in row:
                            dev_name = row['developer']['value'].split('/')[-1].replace('_', ' ')
                            resultado['desarrollador'] = dev_name
                        
                        # Procesar género
                        if 'genre' in row:
                            genre_name = row['genre']['value'].split('/')[-1].replace('_', ' ')
                            resultado['generos'] = [genre_name]
                        
                        resultados_formateados.append(resultado)
                    
                    return resultados_formateados
                
            except Exception as e:
                print(f"   ✗ Error: {str(e)[:100]}")
                if intento < max_intentos:
                    time.sleep(2)
        
        return []
    
    def agregar_juegos_dbpedia_a_ontologia(self, juegos_dbpedia):
        """
        Agrega juegos encontrados en DBpedia a la ontología local
        CORREGIDO - Usa namespaces correctamente
        
        Args:
            juegos_dbpedia: Lista de juegos obtenidos de DBpedia
            
        Returns:
            int: Cantidad de juegos agregados
        """
        from rdflib import URIRef, RDF, RDFS, Literal
        from rdflib.namespace import XSD
        from buscador_semantico import VG  # Importar el namespace correcto
        
        print(f"\n{'='*60}")
        print(f"AGREGANDO JUEGOS DE DBPEDIA A ONTOLOGÍA LOCAL")
        print(f"{'='*60}")
        print(f"Total de juegos a procesar: {len(juegos_dbpedia)}")
        
        count = 0
        errores = 0
        
        for idx, juego in enumerate(juegos_dbpedia, 1):
            try:
                game_uri = URIRef(juego['game'])
                titulo = juego.get('titulo', 'Sin título')
                
                # Verificar si ya existe
                if (game_uri, RDF.type, VG.Videojuego) in self.buscador.graph:
                    print(f"  ⊙ {idx}. {titulo} (ya existe)")
                    continue
                
                # Agregar el juego
                self.buscador.graph.add((game_uri, RDF.type, VG.Videojuego))
                self.buscador.graph.add((game_uri, VG.titulo, Literal(titulo, lang="es")))
                self.buscador.graph.add((game_uri, VG.dbpediaURI, Literal(juego['game'], datatype=XSD.anyURI)))
                
                # Agregar año
                if juego.get('anios') and len(juego['anios']) > 0:
                    try:
                        anio = int(juego['anios'][0])
                        self.buscador.graph.add((game_uri, VG.anioLanzamiento, 
                                               Literal(anio, datatype=XSD.integer)))
                    except (ValueError, TypeError) as e:
                        print(f"      ⚠ Error procesando año: {e}")
                
                # Agregar desarrollador
                if juego.get('desarrollador'):
                    try:
                        dev_name = juego['desarrollador']
                        # Crear URI segura para el desarrollador
                        dev_uri_safe = dev_name.replace(' ', '_').replace('/', '_').replace('&', 'and')
                        dev_uri = URIRef(f"http://dbpedia.org/resource/{dev_uri_safe}")
                        
                        self.buscador.graph.add((dev_uri, RDF.type, VG.Desarrollador))
                        self.buscador.graph.add((dev_uri, RDFS.label, Literal(dev_name)))
                        self.buscador.graph.add((game_uri, VG.desarrolladoPor, dev_uri))
                    except Exception as e:
                        print(f"      ⚠ Error procesando desarrollador: {e}")
                
                # Agregar géneros
                if juego.get('generos'):
                    for genero in juego['generos']:
                        try:
                            # Crear URI segura para el género
                            genre_uri_safe = genero.replace(' ', '_').replace('/', '_').replace('&', 'and')
                            genre_uri = URIRef(f"http://dbpedia.org/resource/{genre_uri_safe}")
                            
                            self.buscador.graph.add((genre_uri, RDF.type, VG.Genero))
                            self.buscador.graph.add((genre_uri, RDFS.label, Literal(genero)))
                            self.buscador.graph.add((game_uri, VG.tieneGenero, genre_uri))
                        except Exception as e:
                            print(f"      ⚠ Error procesando género {genero}: {e}")
                
                count += 1
                
                # Mostrar progreso
                anio_str = f" ({juego['anios'][0]})" if juego.get('anios') else ""
                print(f"  ✓ {idx}. {titulo}{anio_str}")
                
            except Exception as e:
                errores += 1
                print(f"  ✗ {idx}. Error procesando {juego.get('titulo', 'desconocido')}: {str(e)[:80]}")
        
        # Guardar si se agregaron juegos
        if count > 0:
            try:
                self.buscador.graph.serialize(destination=self.buscador.owl_file, format="xml")
                print(f"\n{'='*60}")
                print(f"✓ ONTOLOGÍA GUARDADA EXITOSAMENTE")
                print(f"{'='*60}")
                print(f"  Nuevos agregados: {count}")
                print(f"  Errores: {errores}")
                
                # Contar total
                from buscador_semantico import VG
                total = sum(1 for _ in self.buscador.graph.triples((None, RDF.type, VG.Videojuego)))
                print(f"  Total en ontología: {total}")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"\n✗ Error al guardar ontología: {e}")
                import traceback
                traceback.print_exc()
                return 0
        else:
            print(f"\n⊙ No se agregaron juegos nuevos")
            if errores > 0:
                print(f"  Se encontraron {errores} errores")
        
        return count
