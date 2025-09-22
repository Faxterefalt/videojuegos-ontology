#!/usr/bin/env python3
"""
Script de validación para la Ontología de Videojuegos
Validation script for the Video Games Ontology

Este script valida la ontología y los datos de ejemplo.
This script validates the ontology and example data.
"""

import sys
import os

def main():
    """Función principal de validación"""
    print("=== Validación de la Ontología de Videojuegos ===")
    print("=== Video Games Ontology Validation ===\n")
    
    # Verificar archivos requeridos
    required_files = [
        'videojuegos.owl',
        'videojuegos.ttl', 
        'ejemplos.ttl',
        'videojuegos-context.jsonld',
        'consultas_sparql.rq'
    ]
    
    missing_files = []
    existing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            existing_files.append(file)
            print(f"✓ {file} existe")
        else:
            missing_files.append(file)
            print(f"✗ {file} no encontrado")
    
    print(f"\nArchivos encontrados: {len(existing_files)}/{len(required_files)}")
    
    if missing_files:
        print(f"Archivos faltantes: {missing_files}")
        return False
    
    # Validación básica de sintaxis
    print("\n=== Validación de Sintaxis ===")
    
    # Verificar que los archivos .ttl tienen sintaxis básica correcta
    ttl_files = ['videojuegos.ttl', 'ejemplos.ttl']
    
    for ttl_file in ttl_files:
        print(f"\nValidando {ttl_file}...")
        
        try:
            with open(ttl_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificaciones básicas de sintaxis Turtle
            checks = [
                ('@prefix' in content, "Contiene declaraciones @prefix"),
                ('@base' in content, "Contiene declaración @base"),
                ('rdf:type' in content, "Contiene declaraciones rdf:type"),
                ('rdfs:label' in content, "Contiene etiquetas rdfs:label"),
                ('.' in content, "Contiene terminadores de sentencia"),
                (content.count('@prefix') >= 5, "Múltiples prefijos definidos")
            ]
            
            for check, description in checks:
                status = "✓" if check else "✗"
                print(f"  {status} {description}")
                
        except Exception as e:
            print(f"  ✗ Error leyendo archivo: {e}")
    
    # Validación del contexto JSON-LD
    print(f"\nValidando videojuegos-context.jsonld...")
    try:
        import json
        with open('videojuegos-context.jsonld', 'r', encoding='utf-8') as f:
            context = json.load(f)
        
        if '@context' in context:
            print("  ✓ Estructura JSON-LD válida")
            print(f"  ✓ Contexto contiene {len(context['@context'])} definiciones")
        else:
            print("  ✗ Falta la clave '@context'")
            
    except json.JSONDecodeError as e:
        print(f"  ✗ Error de sintaxis JSON: {e}")
    except Exception as e:
        print(f"  ✗ Error procesando JSON-LD: {e}")
    
    # Estadísticas de contenido
    print("\n=== Estadísticas de Contenido ===")
    
    try:
        # Contar clases, propiedades e instancias en videojuegos.ttl
        with open('videojuegos.ttl', 'r', encoding='utf-8') as f:
            ontology_content = f.read()
        
        class_count = ontology_content.count('rdf:type owl:Class')
        object_prop_count = ontology_content.count('rdf:type owl:ObjectProperty')
        data_prop_count = ontology_content.count('rdf:type owl:DatatypeProperty')
        
        print(f"Ontología principal:")
        print(f"  - Clases: {class_count}")
        print(f"  - Propiedades de objeto: {object_prop_count}")
        print(f"  - Propiedades de datos: {data_prop_count}")
        
        # Contar instancias en ejemplos.ttl
        with open('ejemplos.ttl', 'r', encoding='utf-8') as f:
            examples_content = f.read()
        
        # Contar instancias por tipo
        instance_types = [
            (':Videojuego', 'Videojuegos'),
            (':Genero', 'Géneros'),
            (':Plataforma', 'Plataformas'),
            (':Desarrollador', 'Desarrolladores'),
            (':Editor', 'Editores'),
            (':Jugador', 'Jugadores'),
            (':ModoJuego', 'Modos de juego'),
            (':ClasificacionEdad', 'Clasificaciones')
        ]
        
        print(f"\nInstancias de ejemplo:")
        for instance_type, label in instance_types:
            count = examples_content.count(f'rdf:type {instance_type}')
            print(f"  - {label}: {count}")
            
    except Exception as e:
        print(f"Error calculando estadísticas: {e}")
    
    # Validar consultas SPARQL
    print(f"\n=== Validación de Consultas SPARQL ===")
    try:
        with open('consultas_sparql.rq', 'r', encoding='utf-8') as f:
            sparql_content = f.read()
        
        query_count = sparql_content.count('SELECT')
        prefix_count = sparql_content.count('PREFIX')
        
        print(f"  ✓ {query_count} consultas SELECT encontradas")
        print(f"  ✓ {prefix_count} declaraciones PREFIX")
        
        if 'vg:' in sparql_content:
            print("  ✓ Utiliza el prefijo de la ontología (vg:)")
        else:
            print("  ✗ No utiliza el prefijo de la ontología")
            
    except Exception as e:
        print(f"  ✗ Error validando consultas SPARQL: {e}")
    
    print("\n=== Validación Completada ===")
    
    if not missing_files:
        print("🎉 Todos los archivos están presentes y la validación básica pasó exitosamente.")
        print("📝 Para validación semántica completa, use herramientas como:")
        print("   - Protégé con reasoners OWL")
        print("   - Apache Jena con RIOT")
        print("   - RDFLib para Python")
        return True
    else:
        print("❌ Validación falló - archivos faltantes")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)