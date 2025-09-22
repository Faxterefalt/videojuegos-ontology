#!/usr/bin/env python3
"""
Ejemplo de uso de la Ontología de Videojuegos
Example usage of the Video Games Ontology

Este script demuestra cómo usar la ontología con RDFLib (si está disponible).
This script demonstrates how to use the ontology with RDFLib (if available).
"""

def ejemplo_sin_rdflib():
    """
    Ejemplo básico sin dependencias externas que muestra la estructura de datos
    Basic example without external dependencies showing data structure
    """
    print("=== Ejemplo de Uso de la Ontología de Videojuegos ===")
    print("=== Video Games Ontology Usage Example ===\n")
    
    # Estructura de datos representando instancias de la ontología
    videojuegos_data = {
        "The Legend of Zelda: Breath of the Wild": {
            "tipo": "Videojuego",
            "titulo": "The Legend of Zelda: Breath of the Wild",
            "generos": ["Aventura"],
            "plataformas": ["Nintendo Switch"],
            "desarrollador": "Nintendo EPD",
            "editor": "Nintendo",
            "fecha_lanzamiento": "2017-03-03",
            "precio": 59.99,
            "puntuacion": 9.7,
            "modos_juego": ["Un Jugador"],
            "clasificacion": "ESRB E (Everyone)"
        },
        "Cyberpunk 2077": {
            "tipo": "Videojuego", 
            "titulo": "Cyberpunk 2077",
            "generos": ["RPG"],
            "plataformas": ["PC", "PlayStation 5", "Xbox Series X"],
            "desarrollador": "CD Projekt RED",
            "editor": "CD Projekt",
            "fecha_lanzamiento": "2020-12-10",
            "precio": 49.99,
            "puntuacion": 7.8,
            "modos_juego": ["Un Jugador"],
            "clasificacion": "ESRB M (Mature 17+)"
        },
        "Elden Ring": {
            "tipo": "Videojuego",
            "titulo": "Elden Ring", 
            "generos": ["RPG", "Acción"],
            "plataformas": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X"],
            "desarrollador": "FromSoftware",
            "editor": "Bandai Namco Entertainment",
            "fecha_lanzamiento": "2022-02-25",
            "precio": 59.99,
            "puntuacion": 9.6,
            "modos_juego": ["Un Jugador", "Multijugador en Línea"],
            "clasificacion": "ESRB M (Mature 17+)"
        }
    }
    
    # Mostrar información estructurada
    print("📊 Videojuegos en la base de conocimiento:")
    print("-" * 50)
    
    for titulo, datos in videojuegos_data.items():
        print(f"\n🎮 {titulo}")
        print(f"   Géneros: {', '.join(datos['generos'])}")
        print(f"   Plataformas: {', '.join(datos['plataformas'])}")
        print(f"   Desarrollador: {datos['desarrollador']}")
        print(f"   Puntuación: {datos['puntuacion']}/10")
        print(f"   Precio: ${datos['precio']}")
        print(f"   Fecha: {datos['fecha_lanzamiento']}")
    
    # Consultas simuladas
    print("\n" + "="*60)
    print("🔍 Ejemplos de Consultas Semánticas:")
    print("="*60)
    
    # 1. Juegos por género
    print("\n1. Juegos de RPG:")
    rpg_games = [titulo for titulo, datos in videojuegos_data.items() 
                 if "RPG" in datos['generos']]
    for game in rpg_games:
        print(f"   - {game}")
    
    # 2. Juegos multiplataforma
    print("\n2. Juegos disponibles en más de 2 plataformas:")
    multiplatform = [titulo for titulo, datos in videojuegos_data.items() 
                     if len(datos['plataformas']) > 2]
    for game in multiplatform:
        print(f"   - {game} ({len(videojuegos_data[game]['plataformas'])} plataformas)")
    
    # 3. Juegos con puntuación alta
    print("\n3. Juegos con puntuación ≥ 9.5:")
    high_rated = [(titulo, datos['puntuacion']) for titulo, datos in videojuegos_data.items() 
                  if datos['puntuacion'] >= 9.5]
    high_rated.sort(key=lambda x: x[1], reverse=True)
    for game, score in high_rated:
        print(f"   - {game}: {score}/10")
    
    # 4. Análisis por desarrollador
    print("\n4. Análisis por desarrollador:")
    desarrolladores = {}
    for titulo, datos in videojuegos_data.items():
        dev = datos['desarrollador']
        if dev not in desarrolladores:
            desarrolladores[dev] = []
        desarrolladores[dev].append(titulo)
    
    for dev, games in desarrolladores.items():
        print(f"   {dev}: {len(games)} juego(s)")
        for game in games:
            print(f"     - {game}")
    
    # 5. Estadísticas generales
    print("\n" + "="*60)
    print("📈 Estadísticas Generales:")
    print("="*60)
    
    total_games = len(videojuegos_data)
    avg_score = sum(datos['puntuacion'] for datos in videojuegos_data.values()) / total_games
    avg_price = sum(datos['precio'] for datos in videojuegos_data.values()) / total_games
    
    generos_unicos = set()
    plataformas_unicas = set()
    for datos in videojuegos_data.values():
        generos_unicos.update(datos['generos'])
        plataformas_unicas.update(datos['plataformas'])
    
    print(f"📊 Total de videojuegos: {total_games}")
    print(f"📊 Puntuación promedio: {avg_score:.1f}/10")
    print(f"📊 Precio promedio: ${avg_price:.2f}")
    print(f"📊 Géneros únicos: {len(generos_unicos)} ({', '.join(sorted(generos_unicos))})")
    print(f"📊 Plataformas únicas: {len(plataformas_unicas)}")
    
    print("\n" + "="*60)
    print("🚀 Próximos pasos:")
    print("="*60)
    print("• Cargar la ontología en Protégé para visualización")
    print("• Usar Apache Jena o GraphDB para consultas SPARQL avanzadas")
    print("• Integrar con aplicaciones web usando JSON-LD")
    print("• Extender con más clases y propiedades según necesidades")


def ejemplo_con_rdflib():
    """
    Ejemplo usando RDFLib si está disponible
    Example using RDFLib if available
    """
    try:
        from rdflib import Graph, Namespace, URIRef, Literal
        from rdflib.namespace import RDF, RDFS
        
        print("\n🐍 Ejemplo usando RDFLib:")
        print("-" * 40)
        
        # Crear grafo RDF
        g = Graph()
        
        # Definir namespace
        VG = Namespace("http://www.semanticweb.org/videojuegos#")
        
        # Cargar ontología
        try:
            g.parse("videojuegos.ttl", format="turtle")
            print(f"✓ Ontología cargada: {len(g)} triples")
            
            # Consulta simple
            print("\nClases en la ontología:")
            for s, p, o in g.triples((None, RDF.type, URIRef("http://www.w3.org/2002/07/owl#Class"))):
                label = g.value(s, RDFS.label)
                if label:
                    print(f"  - {label}")
        
        except Exception as e:
            print(f"Error cargando ontología: {e}")
            
        # Cargar ejemplos
        try:
            g.parse("ejemplos.ttl", format="turtle")
            print(f"✓ Ejemplos cargados: {len(g)} triples totales")
            
            # Consulta SPARQL simple
            query = """
                PREFIX vg: <http://www.semanticweb.org/videojuegos#>
                SELECT ?titulo ?puntuacion WHERE {
                    ?juego vg:titulo ?titulo ;
                           vg:puntuacion ?puntuacion .
                }
                ORDER BY DESC(?puntuacion)
            """
            
            results = g.query(query)
            print(f"\nVideojuegos ordenados por puntuación:")
            for row in results:
                print(f"  - {row.titulo}: {row.puntuacion}/10")
                
        except Exception as e:
            print(f"Error con consulta SPARQL: {e}")
            
    except ImportError:
        print("\n⚠️  RDFLib no está disponible.")
        print("Para instalarlo: pip install rdflib")
        print("Ejecutando ejemplo básico en su lugar...\n")
        return False
    
    return True


def main():
    """Función principal"""
    # Intentar ejemplo con RDFLib primero
    if not ejemplo_con_rdflib():
        # Si no está disponible, usar ejemplo básico
        ejemplo_sin_rdflib()
    else:
        # Si RDFLib funciona, también mostrar ejemplo básico
        ejemplo_sin_rdflib()


if __name__ == "__main__":
    main()