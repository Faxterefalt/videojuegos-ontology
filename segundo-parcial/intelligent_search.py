"""
Módulo de Búsqueda Inteligente con NLP
Interpreta consultas en lenguaje natural tipo Google
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import re

class IntelligentSearch:
    def __init__(self, sparql_endpoint="http://dbpedia.org/sparql"):
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(15)
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0")
        
        # FIXED: Traducciones mejoradas
        self.traducciones_es_en = {
            'más vendido': 'best selling',
            'mas vendido': 'best selling',
            'ganador': 'winner',
            'ganó': 'won',
            'goty': 'game of the year',
            'juego del año': 'game of the year',
            'más jugadores': 'most players',
            'mas jugadores': 'most players',
            'recientes': 'recent',
            'reciente': 'recent',
            'mejor': 'best',
            'juegos': 'games',
            'juego': 'game'
        }
        
        # Patrones de consulta (estilo Google)
        self.patrones = {
            'mas_vendido': {
                'keywords': ['más vendido', 'mas vendido', 'best selling', 'mayor venta', 
                           'top ventas', 'más exitoso', 'mas exitoso', 'bestseller'],
                'tipo': 'superlativo_ventas',
                'descripcion': 'Juegos más vendidos de todos los tiempos',
                'singular': True  # NUEVO: indica que solo debe retornar 1 resultado
            },
            'goty': {
                'keywords': ['goty', 'game of the year', 'juego del año', 'ganador goty',
                           'ganó goty', 'ganador del goty', 'winner goty', 'premiado'],
                'tipo': 'premio',
                'descripcion': 'Juegos ganadores de premios GOTY',
                'singular': False
            },
            'mas_jugadores': {
                'keywords': ['más jugadores', 'mas jugadores', 'most players', 
                           'jugadores simultáneos', 'más popular', 'mas popular',
                           'más jugado', 'mas jugado', 'most played', 'concurrent players'],
                'tipo': 'superlativo_jugadores',
                'descripcion': 'Juegos con mayor número de jugadores'
            },
            'mejor_calificado': {
                'keywords': ['mejor calificado', 'mejor valorado', 'highest rated',
                           'mejor puntuado', 'top rated', 'best rated'],
                'tipo': 'superlativo_calificacion',
                'descripcion': 'Juegos mejor calificados por la crítica'
            },
            'mas_caro': {
                'keywords': ['más caro', 'mas caro', 'most expensive', 'precio más alto'],
                'tipo': 'superlativo_precio',
                'descripcion': 'Juegos más caros'
            },
            'mas_largo': {
                'keywords': ['más largo', 'mas largo', 'longest', 'mayor duración', 'más horas'],
                'tipo': 'superlativo_duracion',
                'descripcion': 'Juegos más largos'
            },
            'mas_reciente': {
                'keywords': ['más reciente', 'mas reciente', 'newest', 'último lanzamiento',
                           'ultimo lanzamiento', 'latest', 'más nuevo'],
                'tipo': 'superlativo_reciente',
                'descripcion': 'Juegos lanzados recientemente'
            },
            'mas_antiguo': {
                'keywords': ['más antiguo', 'mas antiguo', 'oldest', 'más viejo', 'clásico'],
                'tipo': 'superlativo_antiguo',
                'descripcion': 'Juegos clásicos/antiguos'
            }
        }
    
    def traducir_consulta(self, consulta):
        """Traduce consulta español a inglés MEJORADO"""
        consulta_traducida = consulta.lower()
        
        for es, en in self.traducciones_es_en.items():
            if es in consulta_traducida:
                consulta_traducida = consulta_traducida.replace(es, en)
        
        print(f"   Traducción: '{consulta}' → '{consulta_traducida}'")
        return consulta_traducida
    
    def analizar_consulta(self, consulta):
        """Analiza consulta en lenguaje natural con NLP básico"""
        consulta_lower = consulta.lower().strip()
        
        print(f"\n{'='*60}")
        print(f"ANÁLISIS INTELIGENTE DE CONSULTA (NLP)")
        print(f"{'='*60}")
        print(f"Consulta: '{consulta}'")
        print(f"{'─'*60}")
        
        resultado = {
            'tipo': 'general',
            'parametros': {'termino': consulta},
            'descripcion': 'Búsqueda general',
            'confianza': 0.0,
            'entidades': [],
            'singular': False,  # NUEVO
            'consulta_traducida': self.traducir_consulta(consulta)  # NUEVO
        }
        
        # 1. Detectar año específico
        anio_match = re.search(r'20\d{2}', consulta)
        if anio_match:
            anio = int(anio_match.group())
            resultado['parametros']['anio'] = anio
            resultado['entidades'].append(('AÑO', anio))
            resultado['confianza'] = 0.7
            print(f"✓ Año detectado: {anio}")
        
        # 2. Detectar patrones de consulta
        max_confianza = resultado['confianza']
        mejor_patron = None
        
        for patron_key, patron_info in self.patrones.items():
            for keyword in patron_info['keywords']:
                if keyword in consulta_lower:
                    confianza = max(0.6, len(keyword) / len(consulta_lower))
                    
                    if confianza > max_confianza:
                        max_confianza = confianza
                        mejor_patron = {
                            'tipo': patron_info['tipo'],
                            'keyword': keyword,
                            'descripcion': patron_info['descripcion'],
                            'singular': patron_info.get('singular', False)  # NUEVO
                        }
        
        if mejor_patron:
            resultado['tipo'] = mejor_patron['tipo']
            resultado['descripcion'] = mejor_patron['descripcion']
            resultado['confianza'] = max_confianza
            resultado['singular'] = mejor_patron['singular']  # NUEVO
            resultado['entidades'].append(('PATRON', mejor_patron['keyword']))
            print(f"✓ Patrón: {mejor_patron['tipo']}")
            print(f"✓ Singular: {mejor_patron['singular']}")
        
        # 3. Detectar géneros
        generos = {
            'accion': ['acción', 'accion', 'action'],
            'rpg': ['rpg', 'rol', 'role-playing'],
            'shooter': ['shooter', 'disparos', 'fps'],
            'aventura': ['aventura', 'adventure'],
            'estrategia': ['estrategia', 'strategy'],
            'deportes': ['deportes', 'sports'],
            'terror': ['terror', 'horror'],
        }
        
        for genero_key, keywords in generos.items():
            for keyword in keywords:
                if keyword in consulta_lower:
                    resultado['parametros']['genero'] = genero_key
                    resultado['entidades'].append(('GENERO', genero_key))
                    # FIXED: Solo actualizar si aumenta la confianza
                    if resultado['confianza'] < 0.6:
                        resultado['confianza'] = 0.6
                    print(f"✓ Género: {genero_key}")
                    break
        
        # 4. Detectar desarrolladores
        desarrolladores = [
            'nintendo', 'sony', 'microsoft', 'valve', 'rockstar', 'ea', 
            'ubisoft', 'activision', 'capcom', 'bethesda', 'fromsoftware',
            'naughty dog', 'cd projekt'
        ]
        
        for dev in desarrolladores:
            if dev in consulta_lower:
                resultado['parametros']['desarrollador'] = dev
                resultado['entidades'].append(('DESARROLLADOR', dev))
                # FIXED: Solo actualizar si aumenta la confianza
                if resultado['confianza'] < 0.6:
                    resultado['confianza'] = 0.6
                print(f"✓ Desarrollador: {dev}")
                break
        
        # 5. Detectar términos temporales (reciente, nuevo, antiguo)
        temporales = {
            'reciente': 'superlativo_reciente',
            'nuevo': 'superlativo_reciente',
            'latest': 'superlativo_reciente',
            'recientes': 'superlativo_reciente',  # ADDED
            'nuevos': 'superlativo_reciente',     # ADDED
            'antiguo': 'superlativo_antiguo',
            'clásico': 'superlativo_antiguo',
            'old': 'superlativo_antiguo'
        }
        
        for temp, tipo_temporal in temporales.items():
            if temp in consulta_lower:
                resultado['tipo'] = tipo_temporal
                resultado['descripcion'] = 'Juegos recientes' if 'reciente' in tipo_temporal else 'Juegos clásicos'
                resultado['entidades'].append(('TEMPORAL', temp))
                # FIXED: Garantizar confianza mínima
                if resultado['confianza'] < 0.7:
                    resultado['confianza'] = 0.7
                print(f"✓ Término temporal: {temp} → {tipo_temporal}")
                break
        
        # 6. GARANTÍA FINAL: Si hay entidades, confianza mínima de 0.5
        if len(resultado['entidades']) > 0 and resultado['confianza'] < 0.5:
            resultado['confianza'] = 0.5
            print(f"✓ Confianza ajustada a 50% (tiene entidades)")
        
        print(f"{'─'*60}")
        print(f"Tipo final: {resultado['tipo']}")
        print(f"Entidades: {len(resultado['entidades'])}")
        print(f"Confianza FINAL: {resultado['confianza']:.2%}")
        print(f"Singular: {resultado['singular']}")
        print(f"{'='*60}\n")
        
        return resultado
    
    def buscar_inteligente(self, consulta, limite=15):
        """Ejecuta búsqueda basada en análisis NLP"""
        analisis = self.analizar_consulta(consulta)
        
        if analisis['confianza'] < 0.3:
            print(f"→ Confianza demasiado baja ({analisis['confianza']:.2%})")
            return {
                'success': False,
                'resultados': [],
                'analisis': analisis,
                'count': 0
            }
        
        print(f"✓ Confianza aceptable ({analisis['confianza']:.2%})")
        
        tipo = analisis['tipo']
        params = analisis['parametros']
        singular = analisis['singular']
        
        # NUEVO: Ajustar límite si es singular
        limite_efectivo = 1 if singular else limite
        
        try:
            if tipo == 'superlativo_ventas':
                resultados = self._query_mas_vendidos(params, limite_efectivo)
            elif tipo == 'premio':
                resultados = self._query_premiados(params, limite_efectivo)
            elif tipo == 'superlativo_jugadores':
                resultados = self._query_mas_populares(params, limite_efectivo)
            elif tipo == 'superlativo_calificacion':
                resultados = self._query_mejor_calificados(params, limite_efectivo)
            elif tipo == 'superlativo_reciente':
                resultados = self._query_mas_recientes(params, limite_efectivo)
            elif tipo == 'superlativo_antiguo':
                resultados = self._query_mas_antiguos(params, limite_efectivo)
            else:
                resultados = self._query_general(params, limite_efectivo)
            
            # NUEVO: Eliminar duplicados y filtrar no lanzados
            resultados = self._filtrar_y_deduplicar(resultados, params)
            
            if len(resultados) > 0:
                print(f"✓ Query exitosa: {len(resultados)} resultados únicos")
            else:
                print(f"⚠ Query sin resultados después de filtrado")
            
            return {
                'success': True,
                'resultados': resultados,
                'analisis': analisis,
                'count': len(resultados)
            }
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'resultados': [],
                'analisis': analisis,
                'count': 0,
                'error': str(e)
            }
    
    def _filtrar_y_deduplicar(self, resultados, params):
        """Filtra duplicados pero PERMITE juegos futuros cercanos (2025)"""
        import datetime
        
        vistos = set()
        filtrados = []
        anio_actual = datetime.datetime.now().year
        
        for resultado in resultados:
            titulo = resultado['titulo'].lower()
            
            if titulo in vistos:
                print(f"   ⊙ Duplicado omitido: {resultado['titulo']}")
                continue
            
            # ARREGLADO: Permitir juegos del año siguiente (2025 si estamos en 2024)
            if resultado.get('anios'):
                anio_juego = resultado['anios'][0]
                if anio_juego > anio_actual + 1:
                    print(f"   ✗ Muy futuro omitido: {resultado['titulo']} ({anio_juego})")
                    continue
            
            if 'vendido' in params.get('termino', '').lower():
                if any(x in titulo for x in ['vi ', ' 6', 'six']) and not any(x in titulo for x in ['v ', ' 5', 'five']):
                    if resultado.get('anios') and resultado['anios'][0] > anio_actual:
                        print(f"   ✗ Versión futura omitida: {resultado['titulo']} ({resultado['anios'][0]})")
                        continue
            
            vistos.add(titulo)
            filtrados.append(resultado)
        
        return filtrados
    
    def _query_mas_vendidos(self, params, limite):
        """Query para EL juego más vendido - CON MULTILINGÜISMO"""
        # Detectar idioma de la consulta
        termino = params.get('termino', '')
        from multilingual import traductor_global
        idioma = traductor_global.detectar_idioma(termino)
        
        filtro_anio = f"FILTER (YEAR(?releaseDate) <= 2024)" if 'anio' not in params else f"FILTER (YEAR(?releaseDate) = {params['anio']})"
        
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            FILTER (lang(?label) = '{idioma}')
            
            OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
            
            {filtro_anio}
            
            # Top juegos más vendidos de la historia
            FILTER (
                CONTAINS(LCASE(?label), 'tetris') ||
                (CONTAINS(LCASE(?label), 'minecraft') && !CONTAINS(LCASE(?label), 'story')) ||
                (CONTAINS(LCASE(?label), 'grand theft auto v') && !CONTAINS(LCASE(?label), 'vi')) ||
                CONTAINS(LCASE(?label), 'wii sports') ||
                CONTAINS(LCASE(?label), 'super mario bros')
            )
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite * 3}
        """
        return self._ejecutar_query(query)
    
    def _query_premiados(self, params, limite):
        """Query para juegos GOTY - CORREGIDA para 2024"""
        anio = params.get('anio')
        
        # Mapeo ACTUALIZADO de ganadores GOTY
        ganadores_goty = {
            2024: "baldur's gate 3",  # GOTY 2023 anunciado en 2024
            2023: "elden ring",
            2022: "it takes two",
            2021: "the last of us part ii",
            2020: "sekiro",
            2019: "god of war",
            2018: "the legend of zelda: breath of the wild"
        }
        
        if anio and anio in ganadores_goty:
            ganador = ganadores_goty[anio]
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?label .
                FILTER (lang(?label) = 'en')
                FILTER (CONTAINS(LCASE(?label), '{ganador}'))
                
                OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
                OPTIONAL {{ ?game dbo:developer ?developer }}
                OPTIONAL {{ ?game dbo:genre ?genre }}
            }}
            LIMIT {limite}
            """
            print(f"   → GOTY {anio}: Buscando '{ganador}'")
        elif anio:
            # Año sin ganador conocido, buscar juegos del año
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?label .
                ?game dbo:releaseDate ?releaseDate .
                FILTER (lang(?label) = 'en')
                FILTER (YEAR(?releaseDate) = {anio})
                
                OPTIONAL {{ ?game dbo:developer ?developer }}
                OPTIONAL {{ ?game dbo:genre ?genre }}
            }}
            ORDER BY DESC(?releaseDate)
            LIMIT {limite}
            """
        else:
            # Sin año específico
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
                
                FILTER (
                    CONTAINS(LCASE(?label), "baldur's gate 3") ||
                    CONTAINS(LCASE(?label), 'elden ring') ||
                    CONTAINS(LCASE(?label), 'the last of us') ||
                    CONTAINS(LCASE(?label), 'god of war') ||
                    CONTAINS(LCASE(?label), 'the witcher 3')
                )
            }}
            ORDER BY DESC(?releaseDate)
            LIMIT {limite}
            """
        
        return self._ejecutar_query(query)
    
    def _query_mas_populares(self, params, limite):
        """Query para juegos con MÁS JUGADORES - ARREGLADA"""
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
            
            # Top juegos con más jugadores activos
            FILTER (
                CONTAINS(LCASE(?label), 'minecraft') ||
                CONTAINS(LCASE(?label), 'league of legends') ||
                CONTAINS(LCASE(?label), 'fortnite') ||
                CONTAINS(LCASE(?label), 'roblox') ||
                CONTAINS(LCASE(?label), 'counter-strike') ||
                CONTAINS(LCASE(?label), 'dota') ||
                CONTAINS(LCASE(?label), 'valorant') ||
                CONTAINS(LCASE(?label), 'grand theft auto v') ||
                CONTAINS(LCASE(?label), 'world of warcraft') ||
                CONTAINS(LCASE(?label), 'apex legends')
            )
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_mas_recientes(self, params, limite):
        """Query para juegos RECIENTES - CON MULTILINGÜISMO MEJORADO"""
        # Detectar idioma y traducir si es necesario
        termino = params.get('termino', '')
        from multilingual import traductor_global
        idioma_original = traductor_global.detectar_idioma(termino)
        
        # Decidir en qué idioma buscar (preferir idioma original si hay contenido)
        idioma_busqueda = idioma_original if idioma_original in ['es', 'en', 'fr', 'de', 'it', 'pt'] else 'en'
        
        filtro_dev = ""
        if 'desarrollador' in params:
            dev = params['desarrollador'].title()
            filtro_dev = f"""
            ?game dbo:developer ?dev .
            ?dev rdfs:label ?devLabel .
            FILTER (CONTAINS(LCASE(?devLabel), LCASE("{dev}")))
            """
        
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            ?game dbo:releaseDate ?releaseDate .
            FILTER (lang(?label) = '{idioma_busqueda}')
            FILTER (YEAR(?releaseDate) >= 2023 && YEAR(?releaseDate) <= 2025)
            
            {filtro_dev}
            
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite * 2}
        """
        return self._ejecutar_query(query)
    
    def _query_mejor_calificados(self, params, limite):
        """Query para juegos mejor calificados - MEJORADA"""
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
            
            # Juegos mejor calificados de la historia
            FILTER (
                CONTAINS(LCASE(?label), 'the legend of zelda') ||
                CONTAINS(LCASE(?label), 'super mario') ||
                CONTAINS(LCASE(?label), 'grand theft auto v') ||
                CONTAINS(LCASE(?label), 'the witcher 3') ||
                CONTAINS(LCASE(?label), 'red dead redemption') ||
                CONTAINS(LCASE(?label), 'half-life') ||
                CONTAINS(LCASE(?label), 'portal') ||
                CONTAINS(LCASE(?label), 'elden ring') ||
                CONTAINS(LCASE(?label), "baldur's gate")
            )
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _ejecutar_query(self, query):
        """Ejecuta query y formatea resultados CON SOPORTE MULTILINGÜE MEJORADO"""
        self.sparql.setQuery(query)
        
        try:
            print(f"   Ejecutando query inteligente...")
            results = self.sparql.query().convert()
            
            if "results" in results and "bindings" in results["results"]:
                bindings = results["results"]["bindings"]
                resultados = []
                
                for row in bindings:
                    resultado = {
                        'game': row['game']['value'],
                        'titulo': row['label']['value'],
                        'anios': [],
                        'desarrollador': None,
                        'generos': [],
                        'source': 'dbpedia',
                        'idioma': row['label'].get('xml:lang', 'en')  # Idioma del label
                    }
                    
                    if 'releaseDate' in row:
                        try:
                            year = row['releaseDate']['value'][:4]
                            resultado['anios'] = [int(year)]
                        except:
                            pass
                    
                    if 'developer' in row:
                        dev_name = row['developer']['value'].split('/')[-1].replace('_', ' ')
                        resultado['desarrollador'] = dev_name
                    
                    if 'genre' in row:
                        genre_name = row['genre']['value'].split('/')[-1].replace('_', ' ')
                        resultado['generos'] = [genre_name]
                    
                    resultados.append(resultado)
                
                print(f"   ✓ {len(resultados)} resultados")
                return resultados
            
            return []
            
        except Exception as e:
            print(f"   ✗ Error: {str(e)[:100]}")
            return []
