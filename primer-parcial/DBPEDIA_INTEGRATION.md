# 🌍 Integración con DBpedia - Guía Completa

## Introducción

Esta ontología de videojuegos es completamente compatible con **DBpedia**, permitiendo consultas federadas entre datos locales y la base de conocimiento global de DBpedia.

## ¿Qué es DBpedia?

**DBpedia** es una extracción estructurada de datos de Wikipedia que proporciona:
- 📚 Millones de entidades (recursos)
- 🔗 Propiedades claramente definidas
- 🌐 Cobertura multilingüe
- 🔄 SPARQL endpoint público

**Referencia:** https://dbpedia.org/

## Mapeos Implementados

### Clases Equivalentes

| Ontología Local | DBpedia | Tipo |
|---|---|---|
| `game:Juego` | `dbo:VideoGame` | `owl:equivalentClass` |
| `game:Desarrolladora` | `dbo:Company` | `owl:equivalentClass` |
| `game:Editora` | `dbo:Company` | `owl:equivalentClass` |
| `game:Plataforma` | `dbo:Platform` | `owl:equivalentClass` |
| `game:Genero` | `dbo:Genre` | `owl:equivalentClass` |
| `game:Premio` | `dbo:Award` | `owl:equivalentClass` |

### Propiedades Equivalentes

| Ontología Local | DBpedia | Relación |
|---|---|---|
| `game:desarrolladoPor` | `dbo:developer` | `owl:equivalentProperty` |
| `game:editadoPor` | `dbo:publisher` | `owl:equivalentProperty` |
| `game:disponibleEn` | `dbo:platform` | `owl:equivalentProperty` |
| `game:tieneGenero` | `dbo:genre` | `owl:equivalentProperty` |
| `game:ganoPremio` | `dbo:award` | `owl:equivalentProperty` |
| `game:fechaPublicacion` | `dbo:releaseDate` | `owl:equivalentProperty` |
| `game:nombreJuego` | `rdfs:label` | `owl:equivalentProperty` |
| `game:descripcionJuego` | `rdfs:comment` | `owl:equivalentProperty` |

## Enlaces a Recursos (owl:sameAs)

Los siguientes recursos están enlazados directamente con DBpedia:

### Videojuegos Conocidos
- **Minecraft** → http://dbpedia.org/resource/Minecraft
- **Call of Duty: Modern Warfare** → http://dbpedia.org/resource/Call_of_Duty:_Modern_Warfare
- **Cyberpunk 2077** → http://dbpedia.org/resource/Cyberpunk_2077
- **League of Legends** → http://dbpedia.org/resource/League_of_Legends
- **The Witcher 3** → http://dbpedia.org/resource/The_Witcher_3:_Wild_Hunt

### Compañías Desarrolladoras
- **Nintendo** → http://dbpedia.org/resource/Nintendo
- **Activision** → http://dbpedia.org/resource/Activision
- **Mojang Studios** → http://dbpedia.org/resource/Mojang
- **Riot Games** → http://dbpedia.org/resource/Riot_Games
- **CD Projekt Red** → http://dbpedia.org/resource/CD_Projekt_Red

### Plataformas
- **PlayStation 5** → http://dbpedia.org/resource/PlayStation_5
- **Xbox Series X** → http://dbpedia.org/resource/Xbox_Series_X_and_Series_S
- **Nintendo Switch** → http://dbpedia.org/resource/Nintendo_Switch

## Consultas Federadas

### Ejemplo 1: Enriquecer datos locales con información de DBpedia

```sparql
PREFIX game: <http://example.org/game#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?nombreLocal ?descripcionDBpedia
WHERE {
  ?juego game:nombreJuego "Minecraft" .
  ?juego owl:sameAs ?juegoDBpedia .
  ?juegoDBpedia rdfs:comment ?descripcionDBpedia .
  FILTER (LANG(?descripcionDBpedia) = "en")
}
```

**Resultado:** Obtiene la descripción en inglés de Minecraft desde DBpedia

### Ejemplo 2: Verificar consistencia

```sparql
PREFIX game: <http://example.org/game#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?juego ?nombreLocal ?nombreDBpedia
WHERE {
  ?juego rdf:type game:Juego .
  ?juego game:nombreJuego ?nombreLocal .
  ?juego owl:sameAs ?juegoDBpedia .
  ?juegoDBpedia rdfs:label ?nombreDBpedia .
  FILTER (LANG(?nombreDBpedia) = "en")
}
```

### Ejemplo 3: Encontrar juegos similares en DBpedia

```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?juego ?nombre
WHERE {
  ?juego rdf:type dbo:VideoGame .
  ?juego rdfs:label ?nombre .
  ?juego dbo:genre ?genero .
  FILTER (LANG(?nombre) = "en")
  FILTER (REGEX(?nombre, "Call of Duty", "i"))
}
LIMIT 5
```

## Cómo Usar Esta Integración

### 1. Cargar la Ontología

```bash
# Con protégé
# File → Open → ontologia_videojuego_dbpedia.owl

# Con Apache Jena
riot ontologia_videojuego_dbpedia.owl | sparql --query query.rq
```

### 2. Consultar Localmente

```sparql
# Obtener todos los juegos
PREFIX game: <http://example.org/game#>
SELECT ?juego WHERE { ?juego rdf:type game:Juego . }
```

### 3. Consultar DBpedia (SPARQL Endpoint)

El endpoint público de DBpedia está en:
```
https://dbpedia.org/sparql
```

### 4. Consultas Federadas

Combina ambas fuentes con `SERVICE` en SPARQL:

```sparql
PREFIX game: <http://example.org/game#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?nombre ?descripcion
WHERE {
  # Tu triplestore local
  ?juego game:nombreJuego ?nombre .
  ?juego owl:sameAs ?dbpediaJuego .
  
  # DBpedia (remoto)
  SERVICE <https://dbpedia.org/sparql> {
    ?dbpediaJuego rdfs:comment ?descripcion .
    FILTER (LANG(?descripcion) = "en")
  }
}
```

## Ventajas de la Integración

✅ **Enriquecimiento de datos:** Accede a información adicional de Wikipedia  
✅ **Validación cruzada:** Verifica la consistencia de tus datos  
✅ **Alcance global:** Conecta tu ontología con millones de recursos  
✅ **Interoperabilidad:** Permite integración con otros sistemas que usan DBpedia  
✅ **Mantenimiento reducido:** Aprovecha actualizaciones de Wikipedia automáticamente  

## Limitaciones y Consideraciones

⚠️ **Acceso remoto:** Las consultas federadas pueden ser lentas  
⚠️ **Disponibilidad:** Depende de la disponibilidad del endpoint de DBpedia  
⚠️ **Cobertura:** No todos los juegos pequeños están en DBpedia  
⚠️ **Idioma:** La mayoría de etiquetas están en inglés  

## Cómo Agregar Nuevos Mapeos

1. Identifica la clase/propiedad en DBpedia
2. Agrega `owl:equivalentClass` o `owl:equivalentProperty`
3. Para recursos, usa `owl:sameAs`
4. Actualiza `dbpedia_mappings.json`

Ejemplo:
```xml
<owl:ObjectProperty rdf:about="http://example.org/game#miPropiedad">
    <owl:equivalentProperty rdf:resource="http://dbpedia.org/ontology/suPropiedad"/>
</owl:ObjectProperty>
```

## Recursos Útiles

- 🔗 **DBpedia SPARQL Endpoint:** https://dbpedia.org/sparql
- 📖 **DBpedia Documentation:** https://wiki.dbpedia.org/
- 🎮 **Video Games in DBpedia:** https://dbpedia.org/page/Video_game
- 📚 **OWL Specification:** https://www.w3.org/OWL/
- 🔍 **SPARQL Tutorial:** https://www.w3.org/TR/sparql11-query/

## Contacto y Contribuciones

Si encuentras inconsistencias o quieres agregar nuevos mapeos:

1. Abre un issue en GitHub
2. Proporciona:
   - Recurso local
   - Recurso DBpedia equivalente
   - Justificación
   - Evidencia

---

**Última actualización:** 2025-10-25  
**Versión:** 2.0-DBpedia  
**Mantenedor:** Equipo de Ontología de Videojuegos