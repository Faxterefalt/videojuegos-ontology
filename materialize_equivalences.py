#!/usr/bin/env python3
# Materializa equivalencias: duplica triples game:* a dbo:* y añade rdf:type dbo:... y rdfs:label desde game:nombreJuego
# Uso:
#   pip install rdflib
#   python materialize_equivalences.py ontologia_videojuego_dbpedia.owl ontologia_videojuego_materializada.owl

import sys
from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import OWL, XSD

if len(sys.argv) != 3:
    print("Uso: python materialize_equivalences.py input.owl output.owl")
    sys.exit(1)

infile = sys.argv[1]
outfile = sys.argv[2]

g = Graph()
g.parse(infile, format='xml')

GAME = Namespace("http://example.org/game#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/")

# Mapeo: propiedades local -> dbo
prop_map = {
    GAME.desarrolladoPor: DBO.developer,
    GAME.editadoPor:      DBO.publisher,
    GAME.disponibleEn:    DBO.platform,
    GAME.tieneGenero:     DBO.genre,
    GAME.ganoPremio:      DBO.award,
    GAME.incorporaTecnologia: DBO.technology,
    GAME.fechaPublicacion: DBO.releaseDate
}

# Mapeo: clases local -> dbo class
class_map = {
    GAME.Juego: DBO.VideoGame,
    GAME.Desarrolladora: DBO.Company,
    GAME.Editora: DBO.Company,
    GAME.Plataforma: DBO.Platform,
    GAME.Genero: DBO.Genre,
    GAME.Premio: DBO.Award
}

added = 0

for s, p, o in list(g.triples((None, None, None))):
    if p in prop_map:
        newp = prop_map[p]
        if (s, newp, o) not in g:
            g.add((s, newp, o))
            added += 1

# 2) Añadir rdf:type dbo:Clase para sujetos con tipo local
for local_cls, dbo_cls in class_map.items():
    for s in g.subjects(RDF.type, local_cls):
        if (s, RDF.type, dbo_cls) not in g:
            g.add((s, RDF.type, dbo_cls))
            added += 1

for s, p, o in list(g.triples((None, GAME.nombreJuego, None))):
    # o es el literal de nombreJuego
    if (s, RDFS.label, o) not in g:
        g.add((s, RDFS.label, o))
        added += 1


# Guardar el grafo resultante
g.serialize(destination=outfile, format='pretty-xml')
print(f"Hecho. Triples añadidos: {added}. Archivo escrito en: {outfile}")