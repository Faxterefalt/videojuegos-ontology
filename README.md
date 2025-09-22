# Ontología de Videojuegos para Web Semántica / Video Games Ontology for Semantic Web

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![OWL 2](https://img.shields.io/badge/OWL-2-blue.svg)](https://www.w3.org/TR/owl2-overview/)
[![Turtle](https://img.shields.io/badge/Format-Turtle-green.svg)](https://www.w3.org/TR/turtle/)

Una ontología completa para representar el dominio de los videojuegos en el contexto de la Web Semántica.  
*A comprehensive ontology for representing the video game domain in the Semantic Web context.*

## 🚀 Inicio Rápido / Quick Start

### Archivos Principales / Main Files

- **`videojuegos.owl`** - Ontología en formato OWL/XML
- **`videojuegos.ttl`** - Ontología en formato Turtle (más legible)
- **`ejemplos.ttl`** - Instancias de ejemplo con videojuegos reales
- **`consultas_sparql.rq`** - Consultas SPARQL de ejemplo
- **`videojuegos-context.jsonld`** - Contexto JSON-LD para aplicaciones web

### Validación Rápida / Quick Validation

```bash
python3 validar_ontologia.py
```

## 📋 Contenido de la Ontología / Ontology Content

### Clases Principales / Main Classes

| Clase (ES) | Class (EN) | Descripción / Description |
|------------|------------|---------------------------|
| `Videojuego` | `VideoGame` | Juego electrónico / Electronic game |
| `Genero` | `Genre` | Categoría de videojuego / Video game category |
| `Plataforma` | `Platform` | Sistema donde se ejecuta / System where it runs |
| `Desarrollador` | `Developer` | Creador del juego / Game creator |
| `Editor` | `Publisher` | Empresa distribuidora / Distribution company |
| `Jugador` | `Player` | Persona que juega / Person who plays |
| `ModoJuego` | `GameMode` | Forma de jugar / Way to play |
| `ClasificacionEdad` | `AgeRating` | Clasificación por edad / Age classification |

### Propiedades de Objeto / Object Properties

- `tieneGenero` / `hasGenre` - Relaciona juego con género
- `disponibleEn` / `availableOn` - Plataformas disponibles
- `desarrolladoPor` / `developedBy` - Desarrollador del juego
- `publicadoPor` / `publishedBy` - Editor del juego
- `tieneModoJuego` / `hasGameMode` - Modos de juego
- `tieneClasificacion` / `hasRating` - Clasificación por edad
- `juega` / `plays` - Jugador juega videojuego

### Propiedades de Datos / Data Properties

- `titulo` / `title` - Título del juego
- `descripcion` / `description` - Descripción del juego
- `fechaLanzamiento` / `releaseDate` - Fecha de lanzamiento
- `precio` / `price` - Precio del juego
- `puntuacion` / `score` - Puntuación (0-10)
- `nombre` / `name` - Nombre de entidades

## 🎮 Ejemplos de Videojuegos Incluidos / Included Video Game Examples

- **The Legend of Zelda: Breath of the Wild** (Nintendo Switch)
- **Cyberpunk 2077** (PC, PlayStation 5, Xbox Series X)
- **The Last of Us Part II** (PlayStation 4/5)
- **Elden Ring** (Multi-plataforma)
- **Grand Theft Auto V** (Multi-plataforma)

## 🔍 Consultas SPARQL de Ejemplo / Example SPARQL Queries

### Buscar juegos por género / Find games by genre
```sparql
PREFIX vg: <http://www.semanticweb.org/videojuegos#>

SELECT ?titulo ?genero WHERE {
    ?juego vg:titulo ?titulo ;
           vg:tieneGenero ?generoObj .
    ?generoObj vg:nombre ?genero .
    FILTER (CONTAINS(LCASE(?genero), "accion"))
}
```

### Juegos con puntuación alta / High-rated games
```sparql
PREFIX vg: <http://www.semanticweb.org/videojuegos#>

SELECT ?titulo ?puntuacion WHERE {
    ?juego vg:titulo ?titulo ;
           vg:puntuacion ?puntuacion .
    FILTER (?puntuacion >= 9.0)
}
ORDER BY DESC(?puntuacion)
```

Ver más ejemplos en `consultas_sparql.rq` / *See more examples in `consultas_sparql.rq`*

## 🛠️ Casos de Uso / Use Cases

### 1. Catálogos de Videojuegos / Video Game Catalogs
Representación estructurada de colecciones de videojuegos con metadatos completos.

### 2. Sistemas de Recomendación / Recommendation Systems
Utilizar relaciones semánticas para recomendar juegos similares.

### 3. Análisis de Mercado / Market Analysis
Analizar tendencias por género, plataforma, desarrollador.

### 4. Búsquedas Semánticas / Semantic Search
Consultas complejas como "RPGs japoneses para Nintendo Switch con puntuación > 8.0"

## 🔧 Herramientas Recomendadas / Recommended Tools

### Editores de Ontologías / Ontology Editors
- **[Protégé](https://protege.stanford.edu/)** - Editor visual completo
- **[WebProtégé](https://webprotege.stanford.edu/)** - Versión web colaborativa

### Bases de Datos RDF / RDF Databases
- **[Apache Jena](https://jena.apache.org/)** - Framework RDF completo
- **[GraphDB](https://graphdb.ontotext.com/)** - Triplestore comercial
- **[Stardog](https://www.stardog.com/)** - Plataforma de grafos de conocimiento

### Validación / Validation
- **[RDFLib](https://rdflib.readthedocs.io/)** - Librería Python para RDF
- **Apache Jena RIOT** - Validador de sintaxis RDF

## 📊 Estadísticas / Statistics

- **8 clases principales** / *8 main classes*
- **7 propiedades de objeto** / *7 object properties*
- **6 propiedades de datos** / *6 data properties*
- **5 videojuegos de ejemplo** / *5 example video games*
- **15+ consultas SPARQL** / *15+ SPARQL queries*

## 🌐 Formatos Disponibles / Available Formats

| Formato | Archivo | Uso Principal |
|---------|---------|---------------|
| OWL/XML | `videojuegos.owl` | Herramientas como Protégé |
| Turtle | `videojuegos.ttl` | Lectura humana, desarrollo |
| JSON-LD | `videojuegos-context.jsonld` | Aplicaciones web |
| SPARQL | `consultas_sparql.rq` | Consultas de ejemplo |

## 🤝 Contribuir / Contributing

1. Fork el repositorio / *Fork the repository*
2. Crea una rama para tu característica / *Create a feature branch*
3. Mantén compatibilidad OWL 2 DL / *Maintain OWL 2 DL compatibility*
4. Incluye documentación bilingüe / *Include bilingual documentation*
5. Valida antes de enviar / *Validate before submitting*

### Pautas de Contribución / Contribution Guidelines

- Mantener etiquetas en español e inglés
- Proporcionar ejemplos de uso
- Documentar nuevas clases y propiedades
- Validar sintaxis RDF/OWL

## 📄 Licencia / License

Esta ontología se distribuye bajo [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

*This ontology is distributed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).*

## 📚 Documentación Adicional / Additional Documentation

- **[DOCUMENTACION.md](DOCUMENTACION.md)** - Documentación técnica completa
- **[Especificación OWL 2](https://www.w3.org/TR/owl2-overview/)**
- **[Tutorial de SPARQL](https://www.w3.org/TR/sparql11-query/)**

## 📞 Contacto / Contact

Para preguntas, sugerencias o reportar problemas, utiliza el sistema de issues del repositorio.

*For questions, suggestions or to report issues, use the repository's issue system.*