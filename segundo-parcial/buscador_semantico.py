from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import OWL, XSD
import sys
import time
import requests
from dbpedia_sync import DBpediaSync

# Configuración de namespaces (exportables)
VG = Namespace("http://www.semanticweb.org/videojuegos#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/")

# Exportar para uso en otros módulos
__all__ = ['BuscadorSemantico', 'VG', 'DBO', 'DBR']

class BuscadorSemantico:
    def __init__(self, owl_file):
        self.graph = Graph()
        self.graph.bind("vg", VG)
        self.graph.bind("dbo", DBO)
        self.graph.bind("dbr", DBR)
        self.owl_file = owl_file
        
        # Inicializar sincronizador de DBpedia
        self.dbpedia_sync = DBpediaSync()
        
        # Cargar ontología existente
        try:
            self.graph.parse(owl_file, format="xml")
            print(f"✓ Ontología cargada desde {owl_file}")
            # Contar videojuegos existentes
            count = sum(1 for _ in self.graph.triples((None, RDF.type, VG.Videojuego)))
            if count > 0:
                print(f"  {count} videojuegos en la ontología local")
        except Exception as e:
            print(f"✓ Creando nueva ontología en {owl_file}")
        
        # Configurar endpoint de DBpedia con timeout y user agent
        self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(30)
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    def verificar_conexion_dbpedia(self):
        """Verifica si DBpedia está disponible"""
        try:
            print("Verificando conexión con DBpedia...")
            
            # Intento 1: Petición HTTP simple
            response = requests.get("http://dbpedia.org/sparql", timeout=10)
            if response.status_code == 200:
                print("✓ DBpedia responde correctamente")
                
                # Intento 2: Query SPARQL de prueba
                test_query = """
                SELECT (COUNT(*) as ?count)
                WHERE {
                    ?s a <http://dbpedia.org/ontology/VideoGame>
                }
                LIMIT 1
                """
                self.sparql.setQuery(test_query)
                result = self.sparql.query().convert()
                
                if "results" in result:
                    print("✓ Endpoint SPARQL funcional")
                    return True
            
            print("⚠ DBpedia no responde adecuadamente")
            return False
            
        except requests.exceptions.Timeout:
            print("✗ Timeout al conectar con DBpedia")
            return False
        except requests.exceptions.ConnectionError:
            print("✗ Error de conexión con DBpedia")
            return False
        except Exception as e:
            print(f"✗ Error inesperado: {str(e)[:100]}")
            return False
    
    def consultar_dbpedia(self, limite=20):
        """Consulta videojuegos desde DBpedia evitando duplicados - MÉTODO PRINCIPAL"""
        # Verificar conexión primero
        if not self.verificar_conexion_dbpedia():
            print("\n⚠ No se puede conectar con DBpedia.")
            print("Usando datos de ejemplo...")
            return self._crear_datos_ejemplo()
        
        print(f"\n{'─'*60}")
        print("CONSULTANDO DBPEDIA CON VALIDACIÓN DE DUPLICADOS")
        print(f"{'─'*60}")
        
        # Obtener juegos que ya existen en la ontología
        uris_existentes = self.dbpedia_sync.obtener_juegos_existentes(self.graph, VG)
        
        if not uris_existentes:
            print("   No hay juegos previos, consultando normalmente...")
            # Si no hay juegos, usar consulta simple
            return self._consultar_dbpedia_simple(limite)
        
        # Usar estrategias múltiples para obtener juegos nuevos
        juegos_nuevos = self.dbpedia_sync.consultar_dbpedia_con_estrategias(limite, uris_existentes)
        
        if juegos_nuevos:
            print(f"\n✓ Total de juegos NUEVOS obtenidos: {len(juegos_nuevos)}")
            return juegos_nuevos
        else:
            print("\n⚠ No se pudieron obtener juegos nuevos de DBpedia.")
            print("Usando datos de ejemplo...")
            # Filtrar ejemplos que no existan
            ejemplos = self._crear_datos_ejemplo()
            ejemplos_nuevos = [ej for ej in ejemplos if ej["game"]["value"] not in uris_existentes]
            return ejemplos_nuevos if ejemplos_nuevos else ejemplos[:limite]
    
    def _consultar_dbpedia_simple(self, limite):
        """Consulta simple cuando no hay juegos previos"""
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
        LIMIT {limite}
        """
        
        self.sparql.setQuery(query)
        
        try:
            print("   Consultando DBpedia...")
            results = self.sparql.query().convert()
            
            if "results" in results and "bindings" in results["results"]:
                bindings = results["results"]["bindings"]
                print(f"   ✓ {len(bindings)} juegos obtenidos")
                return bindings
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
        
        return []

    def _crear_datos_ejemplo(self):
        """Crea datos de ejemplo si DBpedia no funciona"""
        ejemplos = [
            {
                "game": {"value": "http://dbpedia.org/resource/The_Legend_of_Zelda"},
                "label": {"value": "The Legend of Zelda"},
                "releaseDate": {"value": "1986-02-21"},
                "genre": {"value": "http://dbpedia.org/resource/Action-adventure_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Super_Mario_Bros."},
                "label": {"value": "Super Mario Bros."},
                "releaseDate": {"value": "1985-09-13"},
                "developer": {"value": "http://dbpedia.org/resource/Nintendo"},
                "genre": {"value": "http://dbpedia.org/resource/Platform_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Minecraft"},
                "label": {"value": "Minecraft"},
                "releaseDate": {"value": "2011-11-18"},
                "developer": {"value": "http://dbpedia.org/resource/Mojang_Studios"},
                "genre": {"value": "http://dbpedia.org/resource/Sandbox_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/The_Witcher_3:_Wild_Hunt"},
                "label": {"value": "The Witcher 3: Wild Hunt"},
                "releaseDate": {"value": "2015-05-19"},
                "developer": {"value": "http://dbpedia.org/resource/CD_Projekt_Red"},
                "genre": {"value": "http://dbpedia.org/resource/Role-playing_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Grand_Theft_Auto_V"},
                "label": {"value": "Grand Theft Auto V"},
                "releaseDate": {"value": "2013-09-17"},
                "developer": {"value": "http://dbpedia.org/resource/Rockstar_Games"},
                "genre": {"value": "http://dbpedia.org/resource/Action_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Dark_Souls"},
                "label": {"value": "Dark Souls"},
                "releaseDate": {"value": "2011-09-22"},
                "developer": {"value": "http://dbpedia.org/resource/FromSoftware"},
                "genre": {"value": "http://dbpedia.org/resource/Action_role-playing_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Portal_(video_game)"},
                "label": {"value": "Portal"},
                "releaseDate": {"value": "2007-10-10"},
                "developer": {"value": "http://dbpedia.org/resource/Valve_Corporation"},
                "genre": {"value": "http://dbpedia.org/resource/Puzzle_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Half-Life_2"},
                "label": {"value": "Half-Life 2"},
                "releaseDate": {"value": "2004-11-16"},
                "developer": {"value": "http://dbpedia.org/resource/Valve_Corporation"},
                "genre": {"value": "http://dbpedia.org/resource/First-person_shooter"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Red_Dead_Redemption_2"},
                "label": {"value": "Red Dead Redemption 2"},
                "releaseDate": {"value": "2018-10-26"},
                "developer": {"value": "http://dbpedia.org/resource/Rockstar_Games"},
                "genre": {"value": "http://dbpedia.org/resource/Action-adventure_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Cyberpunk_2077"},
                "label": {"value": "Cyberpunk 2077"},
                "releaseDate": {"value": "2020-12-10"},
                "developer": {"value": "http://dbpedia.org/resource/CD_Projekt_Red"},
                "genre": {"value": "http://dbpedia.org/resource/Role-playing_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Elden_Ring"},
                "label": {"value": "Elden Ring"},
                "releaseDate": {"value": "2022-02-25"},
                "developer": {"value": "http://dbpedia.org/resource/FromSoftware"},
                "genre": {"value": "http://dbpedia.org/resource/Action_role-playing_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/God_of_War_(2018_video_game)"},
                "label": {"value": "God of War"},
                "releaseDate": {"value": "2018-04-20"},
                "developer": {"value": "http://dbpedia.org/resource/Santa_Monica_Studio"},
                "genre": {"value": "http://dbpedia.org/resource/Action-adventure_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Horizon_Zero_Dawn"},
                "label": {"value": "Horizon Zero Dawn"},
                "releaseDate": {"value": "2017-02-28"},
                "developer": {"value": "http://dbpedia.org/resource/Guerrilla_Games"},
                "genre": {"value": "http://dbpedia.org/resource/Action_role-playing_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/The_Last_of_Us"},
                "label": {"value": "The Last of Us"},
                "releaseDate": {"value": "2013-06-14"},
                "developer": {"value": "http://dbpedia.org/resource/Naughty_Dog"},
                "genre": {"value": "http://dbpedia.org/resource/Action-adventure_game"}
            },
            {
                "game": {"value": "http://dbpedia.org/resource/Bloodborne"},
                "label": {"value": "Bloodborne"},
                "releaseDate": {"value": "2015-03-24"},
                "developer": {"value": "http://dbpedia.org/resource/FromSoftware"},
                "genre": {"value": "http://dbpedia.org/resource/Action_role-playing_game"}
            }
        ]
        
        print(f"✓ Creados {len(ejemplos)} videojuegos de ejemplo (modo offline)")
        return ejemplos
    
    def poblar_ontologia(self, limite=20):
        """Pobla la ontología con datos de DBpedia o ejemplos"""
        print(f"\n{'='*60}")
        print(f" POBLANDO ONTOLOGÍA")
        print(f"{'='*60}")
        print(f"Límite solicitado: {limite} videojuegos nuevos")
        
        resultados = self.consultar_dbpedia(limite)
        
        if not resultados:
            print("✗ No se obtuvieron resultados")
            return
        
        print(f"\n{'─'*60}")
        print(f"Procesando {len(resultados)} videojuegos...")
        print(f"{'─'*60}")
        
        count_agregados = 0
        count_duplicados = 0
        
        # Obtener URIs existentes para doble verificación
        uris_existentes = self.dbpedia_sync.obtener_juegos_existentes(self.graph, VG)
        
        for row in resultados:
            try:
                game_uri = URIRef(row["game"]["value"])
                label = row.get("label", {}).get("value", "Sin título")
                
                # Verificar si el juego ya existe (doble verificación)
                if not self.dbpedia_sync.validar_juego_nuevo(game_uri, uris_existentes):
                    count_duplicados += 1
                    print(f"  ⊙ {label} (ya existe, omitiendo)")
                    continue
                
                # Agregar videojuego
                self.graph.add((game_uri, RDF.type, VG.Videojuego))
                self.graph.add((game_uri, VG.titulo, Literal(label, lang="es")))
                self.graph.add((game_uri, VG.dbpediaURI, Literal(row["game"]["value"], datatype=XSD.anyURI)))
                
                # Agregar año de lanzamiento
                if "releaseDate" in row:
                    try:
                        year = row["releaseDate"]["value"][:4]
                        self.graph.add((game_uri, VG.anioLanzamiento, Literal(int(year), datatype=XSD.integer)))
                    except:
                        pass
                
                # Agregar desarrollador
                if "developer" in row:
                    dev_uri = URIRef(row["developer"]["value"])
                    dev_name = row["developer"]["value"].split("/")[-1].replace("_", " ")
                    self.graph.add((dev_uri, RDF.type, VG.Desarrollador))
                    self.graph.add((dev_uri, RDFS.label, Literal(dev_name)))
                    self.graph.add((game_uri, VG.desarrolladoPor, dev_uri))
                
                # Agregar género
                if "genre" in row:
                    genre_uri = URIRef(row["genre"]["value"])
                    genre_name = row["genre"]["value"].split("/")[-1].replace("_", " ")
                    self.graph.add((genre_uri, RDF.type, VG.Genero))
                    self.graph.add((genre_uri, RDFS.label, Literal(genre_name)))
                    self.graph.add((game_uri, VG.tieneGenero, genre_uri))
                
                count_agregados += 1
                uris_existentes.add(str(game_uri))  # Agregar a la lista para futuras verificaciones
                
                anio = ""
                if "releaseDate" in row:
                    try:
                        anio = f" ({row['releaseDate']['value'][:4]})"
                    except:
                        pass
                print(f"  ✓ {count_agregados}. {label}{anio} (NUEVO)")
                
            except Exception as e:
                print(f"  ✗ Error procesando {label}: {str(e)[:50]}")
        

        reporte = self.dbpedia_sync.generar_reporte_sincronizacion(
            limite, count_agregados, count_duplicados
        )
        
        if count_agregados > 0:
            try:
                self.graph.serialize(destination=self.owl_file, format="xml")
                print(f"\n{'='*60}")
                print(f"✓ ONTOLOGÍA GUARDADA EXITOSAMENTE")
                print(f"{'='*60}")
                print(f"  Archivo: {self.owl_file}")
                print(f"  Nuevos agregados: {count_agregados} videojuegos")
                print(f"  Duplicados omitidos: {count_duplicados}")
                
                total = sum(1 for _ in self.graph.triples((None, RDF.type, VG.Videojuego)))
                print(f"  Total en ontología: {total} videojuegos")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"\n✗ Error al guardar: {e}")
        else:
            print(f"\n{'='*60}")
            print(f"⚠ NO SE AGREGARON NUEVOS VIDEOJUEGOS")
            print(f"{'='*60}")
            print(f"  {reporte['mensaje']}")
            total = sum(1 for _ in self.graph.triples((None, RDF.type, VG.Videojuego)))
            print(f"  Total en ontología: {total} videojuegos")
            print(f"  SUGERENCIA: Aumenta el límite de juegos a solicitar")
            print(f"{'='*60}\n")

    def buscar_por_titulo(self, termino):
        """Busca videojuegos por título"""
        print(f"\n Buscando por título: '{termino}'")
        query = f"""
        SELECT ?game ?titulo 
               (GROUP_CONCAT(DISTINCT ?anio; separator=",") as ?anios)
               (SAMPLE(?desarrollador) as ?dev)
               (GROUP_CONCAT(DISTINCT ?genero; separator=",") as ?generos)
        WHERE {{
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            OPTIONAL {{ ?game vg:anioLanzamiento ?anio }}
            OPTIONAL {{ 
                ?game vg:desarrolladoPor ?devUri .
                ?devUri rdfs:label ?desarrollador 
            }}
            OPTIONAL {{ 
                ?game vg:tieneGenero ?gen .
                ?gen rdfs:label ?genero 
            }}
            FILTER (CONTAINS(LCASE(?titulo), LCASE("{termino}")))
        }}
        GROUP BY ?game ?titulo
        ORDER BY ?titulo
        """
        resultados = self._ejecutar_consulta(query)
        print(f"✓ {len(resultados)} resultado(s) encontrado(s)")
        return resultados
    
    def buscar_por_anio(self, anio):
        """Busca videojuegos por año"""
        print(f"\n Buscando por año: {anio}")
        query = f"""
        SELECT ?game ?titulo 
               (GROUP_CONCAT(DISTINCT ?anio; separator=",") as ?anios)
               (SAMPLE(?desarrollador) as ?dev)
        WHERE {{
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            ?game vg:anioLanzamiento ?anio .
            OPTIONAL {{ 
                ?game vg:desarrolladoPor ?devUri .
                ?devUri rdfs:label ?desarrollador 
            }}
            FILTER (?anio = {anio})
        }}
        GROUP BY ?game ?titulo
        ORDER BY ?titulo
        """
        resultados = self._ejecutar_consulta(query)
        print(f"✓ {len(resultados)} resultado(s) encontrado(s)")
        return resultados
    
    def buscar_por_desarrollador(self, termino):
        """Busca videojuegos por desarrollador"""
        print(f"\n Buscando por desarrollador: '{termino}'")
        query = f"""
        SELECT ?game ?titulo 
               (GROUP_CONCAT(DISTINCT ?anio; separator=",") as ?anios)
               (SAMPLE(?desarrollador) as ?dev)
        WHERE {{
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            ?game vg:desarrolladoPor ?devUri .
            ?devUri rdfs:label ?desarrollador .
            OPTIONAL {{ ?game vg:anioLanzamiento ?anio }}
            FILTER (CONTAINS(LCASE(?desarrollador), LCASE("{termino}")))
        }}
        GROUP BY ?game ?titulo
        ORDER BY ?titulo
        """
        resultados = self._ejecutar_consulta(query)
        print(f"✓ {len(resultados)} resultado(s) encontrado(s)")
        return resultados
    
    def listar_todos(self):
        """Lista todos los videojuegos"""
        print(f"\n Listando todos los videojuegos")
        query = """
        SELECT ?game ?titulo 
               (GROUP_CONCAT(DISTINCT ?anio; separator=",") as ?anios)
               (SAMPLE(?desarrollador) as ?dev)
               (GROUP_CONCAT(DISTINCT ?genero; separator=",") as ?generos)
        WHERE {
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            OPTIONAL { ?game vg:anioLanzamiento ?anio }
            OPTIONAL { 
                ?game vg:desarrolladoPor ?devUri .
                ?devUri rdfs:label ?desarrollador 
            }
            OPTIONAL { 
                ?game vg:tieneGenero ?gen .
                ?gen rdfs:label ?genero 
            }
        }
        GROUP BY ?game ?titulo
        ORDER BY ?titulo
        """
        resultados = self._ejecutar_consulta(query)
        print(f"✓ Total: {len(resultados)} videojuegos")
        return resultados
    
    def buscar_general(self, termino):
        """Búsqueda general en todos los campos de la ontología"""
        print(f"\n Búsqueda general: '{termino}'")
        query = f"""
        SELECT DISTINCT ?game ?titulo 
               (GROUP_CONCAT(DISTINCT ?anio; separator=",") as ?anios)
               (SAMPLE(?desarrollador) as ?dev)
               (GROUP_CONCAT(DISTINCT ?genero; separator=",") as ?generos)
        WHERE {{
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            OPTIONAL {{ ?game vg:anioLanzamiento ?anio }}
            OPTIONAL {{ 
                ?game vg:desarrolladoPor ?devUri .
                ?devUri rdfs:label ?desarrollador 
            }}
            OPTIONAL {{ 
                ?game vg:tieneGenero ?gen .
                ?gen rdfs:label ?genero 
            }}
            FILTER (
                CONTAINS(LCASE(?titulo), LCASE("{termino}")) ||
                CONTAINS(LCASE(STR(?desarrollador)), LCASE("{termino}")) ||
                CONTAINS(LCASE(STR(?genero)), LCASE("{termino}")) ||
                CONTAINS(LCASE(STR(?anio)), LCASE("{termino}"))
            )
        }}
        GROUP BY ?game ?titulo
        ORDER BY ?titulo
        """
        resultados = self._ejecutar_consulta(query)
        print(f"✓ {len(resultados)} resultado(s) encontrado(s)")
        return resultados
    
    def _ejecutar_consulta(self, query):
        """Ejecuta una consulta SPARQL en la ontología local"""
        resultados = self.graph.query(query)
        return list(resultados)

def menu_principal():
    print("\n" + "="*60)
    print("  BUSCADOR SEMÁNTICO DE VIDEOJUEGOS")
    print("="*60)
    print("\n1. Poblar ontología desde DBpedia")
    print("2. Buscar por título")
    print("3. Buscar por año")
    print("4. Buscar por desarrollador")
    print("5. Listar todos los videojuegos")
    print("6. Salir")
    print("-"*60)

def main():
    owl_path = r"c:\Users\FABIAN\Desktop\GALLETAS\WEB SEMÁNTICAS\videojuegos-ontology\nuevo\videojuegos.owl"
    buscador = BuscadorSemantico(owl_path)
    
    while True:
        menu_principal()
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            limite = input("¿Cuántos videojuegos descargar? (default 10): ").strip()
            limite = int(limite) if limite.isdigit() else 10
            buscador.poblar_ontologia(limite)
        
        elif opcion == "2":
            termino = input(" Ingresa término de búsqueda: ").strip()
            if termino:
                resultados = buscador.buscar_por_titulo(termino)
                print(f"\n Encontrados {len(resultados)} resultados:")
                for i, row in enumerate(resultados, 1):
                    info = f"\n{i}. {row.titulo}"
                    if row.anios:
                        info += f" ({row.anios})"
                    if hasattr(row, 'desarrollador') and row.desarrollador:
                        info += f"\n    Desarrollador: {row.desarrollador}"
                    if hasattr(row, 'generos') and row.generos:
                        info += f"\n    Género: {row.generos}"
                    print(info)
        
        elif opcion == "3":
            anio = input(" Ingresa año: ").strip()
            if anio.isdigit():
                resultados = buscador.buscar_por_anio(int(anio))
                print(f"\n Encontrados {len(resultados)} resultados para {anio}:")
                for i, row in enumerate(resultados, 1):
                    dev = f" - {row.desarrollador}" if hasattr(row, 'desarrollador') and row.desarrollador else ""
                    print(f"{i}. {row.titulo}{dev}")
        
        elif opcion == "4":
            termino = input(" Ingresa desarrollador: ").strip()
            if termino:
                resultados = buscador.buscar_por_desarrollador(termino)
                print(f"\n Encontrados {len(resultados)} resultados:")
                for i, row in enumerate(resultados, 1):
                    anio = f" ({row.anio})" if row.anio else ""
                    print(f"{i}. {row.titulo}{anio} - {row.desarrollador}")
        
        elif opcion == "5":
            resultados = buscador.listar_todos()
            print(f"\n Total: {len(resultados)} videojuegos en la ontología")
            for i, row in enumerate(resultados, 1):
                anio_str = f" ({row.anio})" if row.anio else ""
                print(f"{i}. {row.titulo}{anio_str}")
        
        elif opcion == "6":
            print("\n Saliendo...")
            break
        
        else:
            print("\n✗ Opción no válida")
        
        input("\n⏎ Presiona Enter para continuar...")

if __name__ == "__main__":
    main()