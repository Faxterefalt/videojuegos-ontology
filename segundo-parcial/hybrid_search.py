"""
Módulo para búsqueda híbrida (local + online)
Busca primero en la ontología local y luego en DBpedia si no hay resultados
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Literal
from semantic_reasoning import SemanticReasoner
import time

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
        
        # NUEVO: Caché de resultados
        self.cache_resultados = {}
        self.CACHE_TTL = 180  # 3 minutos
    
    def buscar_titulo_hibrido(self, termino):
        """OPTIMIZADO - búsqueda más rápida"""
        print(f"\n{'='*60}")
        print(f"BÚSQUEDA HÍBRIDA OPTIMIZADA: '{termino}'")
        print(f"{'='*60}")
        
        # Verificar caché
        cache_key = f"hybrid_{termino.lower()}"
        if cache_key in self.cache_resultados:
            import time
            tiempo_cache = self.cache_resultados[cache_key]['timestamp']
            if time.time() - tiempo_cache < self.CACHE_TTL:
                print("✓ Resultados desde caché (instantáneo)")
                return self.cache_resultados[cache_key]['data']
        
        # OPTIMIZACIÓN: Expansión limitada
        terminos_expandidos = [termino]  # Solo término original por defecto
        
        # Solo expandir si es sigla conocida
        if termino.lower() in self.semantic_reasoner.siglas_conocidas:
            terminos_expandidos.extend(
                self.semantic_reasoner.siglas_conocidas[termino.lower()][:2]
            )
        
        # Búsqueda local (RÁPIDA)
        print("\n[1/2] Búsqueda local (rápida)...")
        resultados_locales = self._buscar_local_expandido(terminos_expandidos)
        
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
        
        count_local = len(resultados_locales)
        count_dbpedia = len(resultados_dbpedia)
        
        print(f"\nLocal: {count_local}, DBpedia: {count_dbpedia}\n")
        
        resultado_final = {
            'success': True,
            'source': 'hybrid',
            'local': {
                'results': resultados_locales,
                'count': count_local
            },
            'dbpedia': {
                'results': resultados_dbpedia,
                'count': count_dbpedia
            },
            'total_count': count_local + count_dbpedia,
            'message': f'{count_local} local(es), {count_dbpedia} de DBpedia',
            'terminos_usados': terminos_expandidos[:2]
        }
        
        # Guardar en caché
        import time
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
        
        print("\n[2/2] Buscando en DBpedia...")
        resultados_dbpedia = self._buscar_en_dbpedia_por_desarrollador(termino)
        
        count_local = len(resultados_locales)
        count_dbpedia = len(resultados_dbpedia)
        
        print(f"\nLocal: {count_local}, DBpedia: {count_dbpedia}\n")
        
        return {
            'success': True,
            'source': 'hybrid',
            'local': {
                'results': resultados_locales,
                'count': count_local
            },
            'dbpedia': {
                'results': resultados_dbpedia,
                'count': count_dbpedia
            },
            'total_count': count_local + count_dbpedia,
            'message': f'{count_local} local(es), {count_dbpedia} de DBpedia'
        }
    
    def buscar_general_hibrido(self, termino):
        """Búsqueda general híbrida - SIEMPRE ambas fuentes"""
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
        
        Args:
            juegos_dbpedia: Lista de juegos obtenidos de DBpedia
            
        Returns:
            int: Cantidad de juegos agregados
        """
        from rdflib import URIRef, RDF, RDFS
        from rdflib.namespace import XSD
        
        count = 0
        for juego in juegos_dbpedia:
            try:
                game_uri = URIRef(juego['game'])
                
                # Verificar si ya existe
                if (game_uri, RDF.type, self.buscador.graph.namespace_manager.store.namespace('vg')['Videojuego']) in self.buscador.graph:
                    continue
                
                # Agregar el juego
                VG = self.buscador.graph.namespace_manager.store.namespace('vg')
                
                self.buscador.graph.add((game_uri, RDF.type, VG['Videojuego']))
                self.buscador.graph.add((game_uri, VG['titulo'], Literal(juego['titulo'], lang="es")))
                self.buscador.graph.add((game_uri, VG['dbpediaURI'], Literal(juego['game'], datatype=XSD.anyURI)))
                
                # Agregar año
                if juego['anios']:
                    self.buscador.graph.add((game_uri, VG['anioLanzamiento'], 
                                           Literal(juego['anios'][0], datatype=XSD.integer)))
                
                # Agregar desarrollador
                if juego['desarrollador']:
                    dev_uri = URIRef(f"http://dbpedia.org/resource/{juego['desarrollador'].replace(' ', '_')}")
                    self.buscador.graph.add((dev_uri, RDF.type, VG['Desarrollador']))
                    self.buscador.graph.add((dev_uri, RDFS.label, Literal(juego['desarrollador'])))
                    self.buscador.graph.add((game_uri, VG['desarrolladoPor'], dev_uri))
                
                # Agregar géneros
                for genero in juego['generos']:
                    genre_uri = URIRef(f"http://dbpedia.org/resource/{genero.replace(' ', '_')}")
                    self.buscador.graph.add((genre_uri, RDF.type, VG['Genero']))
                    self.buscador.graph.add((genre_uri, RDFS.label, Literal(genero)))
                    self.buscador.graph.add((game_uri, VG['tieneGenero'], genre_uri))
                count += 1
                
            except Exception as e:
                print(f"Error agregando juego: {str(e)[:50]}")
        
        if count > 0:
            self.buscador.graph.serialize(destination=self.buscador.owl_file, format="xml")
            print(f"\n✓ {count} juegos de DBpedia agregados a la ontología local")
