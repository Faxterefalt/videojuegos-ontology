"""
Módulo para sincronización con DBpedia
Maneja la validación de duplicados y obtención de nuevos videojuegos
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import URIRef
import time
import random

class DBpediaSync:
    def __init__(self, sparql_endpoint="http://dbpedia.org/sparql"):
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(30)
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    def obtener_juegos_existentes(self, graph, vg_namespace):
        """
        Obtiene conjunto de URIs de juegos que ya están en la ontología local
        
        Args:
            graph: El grafo RDF de la ontología
            vg_namespace: Namespace VG para Videojuego
            
        Returns:
            set: Conjunto de URIs (como strings) de juegos existentes
        """
        from rdflib import RDF
        
        uris_existentes = set()
        for s, p, o in graph.triples((None, RDF.type, vg_namespace.Videojuego)):
            uris_existentes.add(str(s))
        
        print(f"   Juegos en ontología local: {len(uris_existentes)}")
        return uris_existentes
    
    def consultar_dbpedia_con_estrategias(self, limite, uris_existentes):
        """
        Consulta DBpedia usando múltiples estrategias para obtener juegos nuevos
        
        Args:
            limite: Número de juegos nuevos deseados
            uris_existentes: Set de URIs que ya existen localmente
            
        Returns:
            list: Lista de juegos nuevos (formato bindings de SPARQL)
        """
        juegos_nuevos = []
        
        # Estrategia 1: Juegos recientes (post-2000) con desarrollador
        estrategia1 = self._consultar_juegos_recientes(limite * 3, uris_existentes)
        juegos_nuevos.extend(estrategia1)
        
        if len(juegos_nuevos) >= limite:
            return juegos_nuevos[:limite]
        
        # Estrategia 2: Juegos con género específico
        estrategia2 = self._consultar_por_genero(limite * 3, uris_existentes)
        juegos_nuevos.extend(estrategia2)
        
        if len(juegos_nuevos) >= limite:
            return juegos_nuevos[:limite]
        
        # Estrategia 3: Usando OFFSET dinámico
        offset = len(uris_existentes)
        estrategia3 = self._consultar_con_offset(limite * 3, offset, uris_existentes)
        juegos_nuevos.extend(estrategia3)
        
        return juegos_nuevos[:limite] if juegos_nuevos else []
    
    def _consultar_juegos_recientes(self, limite, uris_existentes):
        """Consulta juegos lanzados después del año 2000"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            ?game dbo:releaseDate ?releaseDate .
            ?game dbo:developer ?developer .
            FILTER (lang(?label) = 'en')
            FILTER (YEAR(?releaseDate) >= 2000)
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite}
        """
        
        print("\n   Estrategia 1: Buscando juegos recientes con desarrollador...")
        return self._ejecutar_query_filtrada(query, uris_existentes)
    
    def _consultar_por_genero(self, limite, uris_existentes):
        """Consulta juegos por géneros populares"""
        generos = [
            "Action_game",
            "Role-playing_game", 
            "Adventure_game",
            "Simulation_game",
            "Strategy_game"
        ]
        
        genero_aleatorio = random.choice(generos)
        
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbr: <http://dbpedia.org/resource/>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            ?game dbo:genre dbr:{genero_aleatorio} .
            FILTER (lang(?label) = 'en')
            OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
            OPTIONAL {{ ?game dbo:developer ?developer }}
            BIND(dbr:{genero_aleatorio} as ?genre)
        }}
        LIMIT {limite}
        """
        
        print(f"\n   Estrategia 2: Buscando juegos de género {genero_aleatorio.replace('_', ' ')}...")
        return self._ejecutar_query_filtrada(query, uris_existentes)
    
    def _consultar_con_offset(self, limite, offset, uris_existentes):
        """Consulta con OFFSET para saltar los primeros resultados"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            FILTER (lang(?label) = 'en')
            OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        ORDER BY ?game
        OFFSET {offset}
        LIMIT {limite}
        """
        
        print(f"\n   Estrategia 3: Consultando con offset {offset}...")
        return self._ejecutar_query_filtrada(query, uris_existentes)
    
    def _ejecutar_query_filtrada(self, query, uris_existentes):
        """
        Ejecuta una query SPARQL y filtra resultados que ya existen
        
        Args:
            query: Query SPARQL a ejecutar
            uris_existentes: Set de URIs existentes
            
        Returns:
            list: Juegos nuevos (no existentes)
        """
        juegos_nuevos = []
        max_intentos = 2
        
        self.sparql.setQuery(query)
        
        for intento in range(1, max_intentos + 1):
            try:
                print(f"      Intento {intento}/{max_intentos}...")
                results = self.sparql.query().convert()
                
                if "results" in results and "bindings" in results["results"]:
                    bindings = results["results"]["bindings"]
                    
                    # Filtrar juegos que no existen localmente
                    for row in bindings:
                        game_uri = row["game"]["value"]
                        if game_uri not in uris_existentes:
                            juegos_nuevos.append(row)
                    
                    if juegos_nuevos:
                        print(f"      ✓ {len(juegos_nuevos)} juegos nuevos encontrados")
                        return juegos_nuevos
                    else:
                        print(f"      ⊙ Todos los {len(bindings)} juegos ya existen")
                        return []
                
            except Exception as e:
                print(f"      ✗ Error: {str(e)[:100]}")
                if intento < max_intentos:
                    time.sleep(2)
        
        return juegos_nuevos
    
    def validar_juego_nuevo(self, game_uri, uris_existentes):
        """
        Valida si un juego es nuevo (no existe en la ontología)
        
        Args:
            game_uri: URI del juego a validar (string o URIRef)
            uris_existentes: Set de URIs existentes
            
        Returns:
            bool: True si el juego es nuevo, False si ya existe
        """
        uri_str = str(game_uri)
        return uri_str not in uris_existentes
    
    def generar_reporte_sincronizacion(self, total_solicitados, nuevos_agregados, duplicados_encontrados):
        """
        Genera un reporte de la sincronización
        
        Args:
            total_solicitados: Cantidad de juegos solicitados
            nuevos_agregados: Cantidad de juegos nuevos agregados
            duplicados_encontrados: Cantidad de duplicados encontrados
            
        Returns:
            dict: Reporte con estadísticas
        """
        return {
            "solicitados": total_solicitados,
            "nuevos": nuevos_agregados,
            "duplicados": duplicados_encontrados,
            "exito": nuevos_agregados > 0,
            "mensaje": self._generar_mensaje_reporte(nuevos_agregados, duplicados_encontrados)
        }
    
    def _generar_mensaje_reporte(self, nuevos, duplicados):
        """Genera mensaje descriptivo del resultado"""
        if nuevos > 0:
            msg = f"✓ {nuevos} juego(s) nuevo(s) agregado(s)"
            if duplicados > 0:
                msg += f" ({duplicados} duplicado(s) omitido(s))"
            return msg
        else:
            if duplicados > 0:
                return f"⊙ Los {duplicados} juegos consultados ya existían en la ontología"
            else:
                return "✗ No se pudieron obtener juegos nuevos de DBpedia"
