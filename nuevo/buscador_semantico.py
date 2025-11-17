from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import OWL, XSD
import sys

# Configuración de namespaces
VG = Namespace("http://www.semanticweb.org/videojuegos#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/")

class BuscadorSemantico:
    def __init__(self, owl_file):
        self.graph = Graph()
        self.graph.bind("vg", VG)
        self.graph.bind("dbo", DBO)
        self.graph.bind("dbr", DBR)
        self.owl_file = owl_file
        
        # Cargar ontología existente
        try:
            self.graph.parse(owl_file, format="xml")
            print(f"✓ Ontología cargada desde {owl_file}")
        except:
            print(f"✓ Creando nueva ontología en {owl_file}")
        
        # Configurar endpoint de DBpedia
        self.sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        self.sparql.setReturnFormat(JSON)
    
    def consultar_dbpedia(self, limite=20):
        """Consulta videojuegos desde DBpedia"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre ?platform ?abstract
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
            OPTIONAL {{ ?game dbo:computingPlatform ?platform }}
            OPTIONAL {{ ?game dbo:abstract ?abstract }}
            FILTER (lang(?label) = 'es' || lang(?label) = 'en')
            FILTER (lang(?abstract) = 'es' || lang(?abstract) = 'en')
        }}
        LIMIT {limite}
        """
        
        self.sparql.setQuery(query)
        try:
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            print(f"✗ Error al consultar DBpedia: {e}")
            return []
    
    def poblar_ontologia(self, limite=20):
        """Pobla la ontología con datos de DBpedia"""
        print(f"\n Consultando DBpedia (límite: {limite} videojuegos)...")
        resultados = self.consultar_dbpedia(limite)
        
        if not resultados:
            print("✗ No se obtuvieron resultados de DBpedia")
            return
        
        print(f"✓ Obtenidos {len(resultados)} resultados\n")
        print("📥 Poblando ontología...")
        
        count = 0
        for row in resultados:
            try:
                game_uri = URIRef(row["game"]["value"])
                label = row.get("label", {}).get("value", "Sin título")
                
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
                
                # Agregar descripción
                if "abstract" in row:
                    abstract = row["abstract"]["value"]
                    self.graph.add((game_uri, VG.descripcion, Literal(abstract[:500])))
                
                # Agregar desarrollador
                if "developer" in row:
                    dev_uri = URIRef(row["developer"]["value"])
                    self.graph.add((dev_uri, RDF.type, VG.Desarrollador))
                    self.graph.add((game_uri, VG.desarrolladoPor, dev_uri))
                
                # Agregar género
                if "genre" in row:
                    genre_uri = URIRef(row["genre"]["value"])
                    self.graph.add((genre_uri, RDF.type, VG.Genero))
                    self.graph.add((game_uri, VG.tieneGenero, genre_uri))
                
                # Agregar plataforma
                if "platform" in row:
                    platform_uri = URIRef(row["platform"]["value"])
                    self.graph.add((platform_uri, RDF.type, VG.Plataforma))
                    self.graph.add((game_uri, VG.tienePlataforma, platform_uri))
                
                count += 1
                print(f"  ✓ {count}. {label}")
            except Exception as e:
                print(f"  ✗ Error procesando: {e}")
        
        # Guardar ontología
        self.graph.serialize(destination=self.owl_file, format="xml")
        print(f"\n✓ Ontología guardada con {count} videojuegos en {self.owl_file}")
    
    def buscar_por_titulo(self, termino):
        """Busca videojuegos por título"""
        query = f"""
        SELECT ?game ?titulo ?anio ?descripcion
        WHERE {{
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            OPTIONAL {{ ?game vg:anioLanzamiento ?anio }}
            OPTIONAL {{ ?game vg:descripcion ?descripcion }}
            FILTER (CONTAINS(LCASE(?titulo), LCASE("{termino}")))
        }}
        """
        return self._ejecutar_consulta(query)
    
    def buscar_por_anio(self, anio):
        """Busca videojuegos por año"""
        query = f"""
        SELECT ?game ?titulo ?anio ?desarrollador
        WHERE {{
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            ?game vg:anioLanzamiento ?anio .
            OPTIONAL {{ ?game vg:desarrolladoPor ?desarrollador }}
            FILTER (?anio = {anio})
        }}
        """
        return self._ejecutar_consulta(query)
    
    def buscar_por_desarrollador(self, termino):
        """Busca videojuegos por desarrollador"""
        query = f"""
        SELECT ?game ?titulo ?anio ?desarrollador
        WHERE {{
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            ?game vg:desarrolladoPor ?desarrollador .
            OPTIONAL {{ ?game vg:anioLanzamiento ?anio }}
            FILTER (CONTAINS(LCASE(STR(?desarrollador)), LCASE("{termino}")))
        }}
        """
        return self._ejecutar_consulta(query)
    
    def listar_todos(self):
        """Lista todos los videojuegos"""
        query = """
        SELECT ?game ?titulo ?anio
        WHERE {
            ?game rdf:type vg:Videojuego .
            ?game vg:titulo ?titulo .
            OPTIONAL { ?game vg:anioLanzamiento ?anio }
        }
        ORDER BY ?titulo
        """
        return self._ejecutar_consulta(query)
    
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
            limite = input("¿Cuántos videojuegos descargar? (default 20): ").strip()
            limite = int(limite) if limite.isdigit() else 20
            buscador.poblar_ontologia(limite)
        
        elif opcion == "2":
            termino = input("Ingresa término de búsqueda: ").strip()
            resultados = buscador.buscar_por_titulo(termino)
            print(f"\n📋 Encontrados {len(resultados)} resultados:")
            for i, row in enumerate(resultados, 1):
                print(f"\n{i}. {row.titulo}")
                if row.anio:
                    print(f"   Año: {row.anio}")
                if hasattr(row, 'descripcion') and row.descripcion:
                    print(f"   {row.descripcion[:200]}...")
        
        elif opcion == "3":
            anio = input("Ingresa año: ").strip()
            if anio.isdigit():
                resultados = buscador.buscar_por_anio(int(anio))
                print(f"\n📋 Encontrados {len(resultados)} resultados para {anio}:")
                for i, row in enumerate(resultados, 1):
                    print(f"{i}. {row.titulo}")
        
        elif opcion == "4":
            termino = input("Ingresa desarrollador: ").strip()
            resultados = buscador.buscar_por_desarrollador(termino)
            print(f"\n📋 Encontrados {len(resultados)} resultados:")
            for i, row in enumerate(resultados, 1):
                print(f"{i}. {row.titulo} - {row.desarrollador}")
        
        elif opcion == "5":
            resultados = buscador.listar_todos()
            print(f"\n📋 Total: {len(resultados)} videojuegos")
            for i, row in enumerate(resultados, 1):
                anio_str = f" ({row.anio})" if row.anio else ""
                print(f"{i}. {row.titulo}{anio_str}")
        
        elif opcion == "6":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("\n✗ Opción no válida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
