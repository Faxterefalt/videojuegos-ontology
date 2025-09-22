# Ontología de Videojuegos para Web Semántica

## Descripción General

Esta ontología proporciona un marco conceptual completo para describir el dominio de los videojuegos en el contexto de la Web Semántica. Está diseñada para ser utilizada en aplicaciones que necesiten representar, consultar y razonar sobre información relacionada con videojuegos, desarrolladores, géneros, plataformas y jugadores.

## Estructura de la Ontología

### Clases Principales

#### 1. `Videojuego`
La clase central de la ontología que representa un videojuego.

**Propiedades de datos:**
- `titulo`: El título del videojuego
- `descripcion`: Descripción del contenido y gameplay
- `fechaLanzamiento`: Fecha de lanzamiento oficial
- `precio`: Precio actual del juego
- `puntuacion`: Puntuación promedio (0-10)

**Propiedades de objeto:**
- `tieneGenero`: Relaciona con uno o más géneros
- `disponibleEn`: Plataformas donde está disponible
- `desarrolladoPor`: Desarrollador responsable
- `publicadoPor`: Editor/Publisher
- `tieneModoJuego`: Modos de juego disponibles
- `tieneClasificacion`: Clasificación por edad

#### 2. `Genero`
Categorías de videojuegos basadas en mecánicas y estilo de juego.

**Ejemplos incluidos:**
- Acción
- RPG (Juego de Rol)
- Aventura
- Estrategia
- Deportes
- Simulación

#### 3. `Plataforma`
Sistemas hardware/software donde se ejecutan los videojuegos.

**Ejemplos incluidos:**
- PlayStation 5
- Xbox Series X
- Nintendo Switch
- PC
- PlayStation 4
- Xbox One

#### 4. `Desarrollador`
Personas o empresas que crean videojuegos.

**Ejemplos incluidos:**
- Nintendo EPD
- CD Projekt RED
- Naughty Dog
- FromSoftware
- Rockstar Games

#### 5. `Editor`
Empresas responsables de la publicación y distribución.

**Ejemplos incluidos:**
- Nintendo
- Sony Interactive Entertainment
- Bandai Namco Entertainment
- Take-Two Interactive

#### 6. `ModoJuego`
Diferentes formas de jugar un videojuego.

**Ejemplos incluidos:**
- Un Jugador
- Multijugador
- Cooperativo
- Multijugador en Línea

#### 7. `ClasificacionEdad`
Sistemas de clasificación por edad.

**Ejemplos incluidos:**
- ESRB E (Everyone)
- ESRB T (Teen)
- ESRB M (Mature 17+)
- PEGI 3, 12, 18

#### 8. `Jugador`
Personas que juegan videojuegos.

## Archivos de la Ontología

### `videojuegos.owl`
Versión en formato OWL/XML, estándar para ontologías OWL. Compatible con herramientas como Protégé.

### `videojuegos.ttl`
Versión en formato Turtle, más legible para humanos y ampliamente utilizada en aplicaciones RDF.

### `ejemplos.ttl`
Instancias de ejemplo que demuestran el uso de la ontología con videojuegos reales como:
- The Legend of Zelda: Breath of the Wild
- Cyberpunk 2077
- The Last of Us Part II
- Elden Ring
- Grand Theft Auto V

## Casos de Uso

### 1. Catálogos de Videojuegos
Representar información estructurada sobre colecciones de videojuegos con metadatos completos.

### 2. Sistemas de Recomendación
Utilizar las relaciones entre géneros, desarrolladores y valoraciones para recomendar juegos similares.

### 3. Análisis de Mercado
Analizar tendencias por género, plataforma, desarrollador o período de tiempo.

### 4. Aplicaciones de Descubrimiento
Permitir búsquedas semánticas complejas como "juegos de rol desarrollados por estudios japoneses para Nintendo Switch".

## Consultas SPARQL de Ejemplo

### Encontrar todos los videojuegos de un género específico:
```sparql
PREFIX vg: <http://www.semanticweb.org/videojuegos#>

SELECT ?juego ?titulo WHERE {
    ?juego vg:tieneGenero vg:RPG ;
           vg:titulo ?titulo .
}
```

### Listar juegos disponibles en múltiples plataformas:
```sparql
PREFIX vg: <http://www.semanticweb.org/videojuegos#>

SELECT ?juego ?titulo (COUNT(?plataforma) as ?numPlataformas) WHERE {
    ?juego vg:titulo ?titulo ;
           vg:disponibleEn ?plataforma .
}
GROUP BY ?juego ?titulo
HAVING (?numPlataformas > 2)
```

### Encontrar juegos con puntuación alta:
```sparql
PREFIX vg: <http://www.semanticweb.org/videojuegos#>

SELECT ?titulo ?puntuacion WHERE {
    ?juego vg:titulo ?titulo ;
           vg:puntuacion ?puntuacion .
    FILTER (?puntuacion >= 9.0)
}
ORDER BY DESC(?puntuacion)
```

## Extensibilidad

La ontología está diseñada para ser fácilmente extensible:

- **Nuevos géneros**: Agregar subclases de `Genero`
- **Plataformas emergentes**: Nuevas instancias de `Plataforma`
- **Propiedades adicionales**: Como dificultad, duración estimada, requisitos del sistema
- **Relaciones complejas**: Secuelas, remasters, DLC

## Integración con Otras Ontologías

La ontología puede integrarse con:

- **Dublin Core**: Para metadatos generales
- **FOAF**: Para información sobre personas (desarrolladores, jugadores)
- **Schema.org**: Para compatibilidad web
- **Ontologías de dominio específico**: Gaming, entretenimiento digital

## Herramientas Recomendadas

### Editores de Ontologías
- **Protégé**: Editor visual completo
- **WebProtégé**: Versión web colaborativa
- **TopBraid Composer**: Herramienta comercial avanzada

### Bases de Datos RDF
- **Apache Jena/Fuseki**: Triplestore open source
- **GraphDB**: Triplestore comercial con razonamiento
- **Stardog**: Plataforma de grafos de conocimiento

### Validación
- **SHACL**: Para validación de formas de datos
- **OWL Reasoners**: HermiT, Pellet, ELK para razonamiento

## Licencia

Esta ontología se distribuye bajo licencia Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Mantenga la compatibilidad con OWL 2 DL
2. Proporcione documentación en español e inglés
3. Incluya ejemplos de uso
4. Valide la ontología antes de enviar cambios

## Contacto

Para preguntas, sugerencias o reportar problemas, utilice el sistema de issues del repositorio.