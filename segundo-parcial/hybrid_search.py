"""
Módulo para búsqueda híbrida (local + online)
Busca primero en la ontología local y luego en DBpedia si no hay resultados
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Literal
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
        self.sparql.setTimeout(30)
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    def buscar_titulo_hibrido(self, termino):
        """
        Busca por título primero localmente, luego en DBpedia
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            dict: Resultados con información de origen (local/online)
        """
        print(f"\n{'='*60}")
        print(f"BÚSQUEDA HÍBRIDA POR TÍTULO: '{termino}'")
        print(f"{'='*60}")
        
        # Paso 1: Buscar localmente
        print("\n[1/2] Buscando en ontología local...")
        resultados_locales = self.buscador.buscar_por_titulo(termino)
        
        if resultados_locales:
            print(f"✓ Encontrados {len(resultados_locales)} resultado(s) LOCAL(ES)")
            return {
                'success': True,
                'source': 'local',
                'results': resultados_locales,
                'count': len(resultados_locales),
                'message': f'Resultados encontrados en ontología local'
            }
        
        # Paso 2: Si no hay resultados locales, buscar en DBpedia
        print("⊙ No se encontraron resultados locales")
        print("\n[2/2] Buscando en DBpedia...")
        
        resultados_dbpedia = self._buscar_en_dbpedia_por_titulo(termino)
        
        if resultados_dbpedia:
            print(f"✓ Encontrados {len(resultados_dbpedia)} resultado(s) en DBpedia")
            return {
                'success': True,
                'source': 'dbpedia',
                'results': resultados_dbpedia,
                'count': len(resultados_dbpedia),
                'message': f'Resultados encontrados en DBpedia (no están en tu ontología local)'
            }
        
        print("✗ No se encontraron resultados ni local ni en DBpedia")
        return {
            'success': False,
            'source': 'none',
            'results': [],
            'count': 0,
            'message': 'No se encontraron resultados'
        }
    
    def buscar_desarrollador_hibrido(self, termino):
        """Búsqueda híbrida por desarrollador"""
        print(f"\n{'='*60}")
        print(f"BÚSQUEDA HÍBRIDA POR DESARROLLADOR: '{termino}'")
        print(f"{'='*60}")
        
        # Buscar localmente
        print("\n[1/2] Buscando en ontología local...")
        resultados_locales = self.buscador.buscar_por_desarrollador(termino)
        
        if resultados_locales:
            print(f"✓ Encontrados {len(resultados_locales)} resultado(s) LOCAL(ES)")
            return {
                'success': True,
                'source': 'local',
                'results': resultados_locales,
                'count': len(resultados_locales),
                'message': f'Resultados encontrados en ontología local'
            }
        
        # Buscar en DBpedia
        print("⊙ No se encontraron resultados locales")
        print("\n[2/2] Buscando en DBpedia...")
        
        resultados_dbpedia = self._buscar_en_dbpedia_por_desarrollador(termino)
        
        if resultados_dbpedia:
            print(f"✓ Encontrados {len(resultados_dbpedia)} resultado(s) en DBpedia")
            return {
                'success': True,
                'source': 'dbpedia',
                'results': resultados_dbpedia,
                'count': len(resultados_dbpedia),
                'message': f'Resultados encontrados en DBpedia (no están en tu ontología local)'
            }
        
        return {
            'success': False,
            'source': 'none',
            'results': [],
            'count': 0,
            'message': 'No se encontraron resultados'
        }
    
    def buscar_general_hibrido(self, termino):
        """Búsqueda general híbrida"""
        print(f"\n{'='*60}")
        print(f"BÚSQUEDA GENERAL HÍBRIDA: '{termino}'")
        print(f"{'='*60}")
        
        # Buscar localmente
        print("\n[1/2] Buscando en ontología local...")
        resultados_locales = self.buscador.buscar_general(termino)
        
        if resultados_locales:
            print(f"✓ Encontrados {len(resultados_locales)} resultado(s) LOCAL(ES)")
            return {
                'success': True,
                'source': 'local',
                'results': resultados_locales,
                'count': len(resultados_locales),
                'message': f'Resultados encontrados en ontología local'
            }
        
        # Buscar en DBpedia
        print("⊙ No se encontraron resultados locales")
        print("\n[2/2] Buscando en DBpedia...")
        
        resultados_dbpedia = self._buscar_en_dbpedia_general(termino)
        
        if resultados_dbpedia:
            print(f"✓ Encontrados {len(resultados_dbpedia)} resultado(s) en DBpedia")
            return {
                'success': True,
                'source': 'dbpedia',
                'results': resultados_dbpedia,
                'count': len(resultados_dbpedia),
                'message': f'Resultados encontrados en DBpedia (no están en tu ontología local)'
            }
        
        return {
            'success': False,
            'source': 'none',
            'results': [],
            'count': 0,
            'message': 'No se encontraron resultados'
        }
    
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
        
        return count
