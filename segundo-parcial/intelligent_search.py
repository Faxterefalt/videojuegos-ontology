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
        
        # Patrones de consulta (estilo Google)
        self.patrones = {
            'mas_vendido': {
                'keywords': ['más vendido', 'mas vendido', 'best selling', 'mayor venta', 
                           'top ventas', 'más exitoso', 'mas exitoso', 'bestseller'],
                'tipo': 'superlativo_ventas',
                'descripcion': 'Juegos más vendidos de todos los tiempos'
            },
            'goty': {
                'keywords': ['goty', 'game of the year', 'juego del año', 'ganador goty',
                           'ganó goty', 'premio', 'award', 'premiado', 'game of year'],
                'tipo': 'premio',
                'descripcion': 'Juegos ganadores de premios GOTY'
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
            'entidades': []
        }
        
        # 1. Detectar año específico
        anio_match = re.search(r'20\d{2}', consulta)
        if anio_match:
            anio = int(anio_match.group())
            resultado['parametros']['anio'] = anio
            resultado['entidades'].append(('AÑO', anio))
            resultado['confianza'] = 0.7  # FIXED: Asignar directamente
            print(f"✓ Año detectado: {anio}")
        
        # 2. Detectar patrones de consulta PRIMERO (más importante)
        max_confianza = resultado['confianza']  # FIXED: Empezar desde confianza actual
        mejor_patron = None
        
        for patron_key, patron_info in self.patrones.items():
            for keyword in patron_info['keywords']:
                if keyword in consulta_lower:
                    # Calcular confianza (mínimo 0.6)
                    confianza = max(0.6, len(keyword) / len(consulta_lower))
                    
                    if confianza > max_confianza:
                        max_confianza = confianza
                        mejor_patron = {
                            'tipo': patron_info['tipo'],
                            'keyword': keyword,
                            'descripcion': patron_info['descripcion']
                        }
        
        if mejor_patron:
            resultado['tipo'] = mejor_patron['tipo']
            resultado['descripcion'] = mejor_patron['descripcion']
            resultado['confianza'] = max_confianza  # FIXED: Usar max_confianza
            resultado['entidades'].append(('PATRON', mejor_patron['keyword']))
            print(f"✓ Patrón: {mejor_patron['tipo']}")
            print(f"✓ Keyword: '{mejor_patron['keyword']}'")
        
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
        print(f"Confianza FINAL: {resultado['confianza']:.2%}")  # FIXED: Mostrar claramente
        print(f"{'='*60}\n")
        
        return resultado
    
    def buscar_inteligente(self, consulta, limite=15):
        """Ejecuta búsqueda basada en análisis NLP"""
        analisis = self.analizar_consulta(consulta)
        
        # FIXED: Umbral más bajo para aceptar consultas
        if analisis['confianza'] < 0.3:
            print(f"→ Confianza demasiado baja ({analisis['confianza']:.2%}), usando búsqueda estándar")
            return {
                'success': False,
                'resultados': [],
                'analisis': analisis,
                'count': 0
            }
        
        print(f"✓ Confianza aceptable ({analisis['confianza']:.2%}), ejecutando búsqueda inteligente...")
        
        tipo = analisis['tipo']
        params = analisis['parametros']
        
        try:
            # Ejecutar query según tipo detectado
            if tipo == 'superlativo_ventas':
                resultados = self._query_mas_vendidos(params, limite)
            elif tipo == 'premio':
                resultados = self._query_premiados(params, limite)
            elif tipo == 'superlativo_jugadores':
                resultados = self._query_mas_populares(params, limite)
            elif tipo == 'superlativo_calificacion':
                resultados = self._query_mejor_calificados(params, limite)
            elif tipo == 'superlativo_reciente':
                resultados = self._query_mas_recientes(params, limite)
            elif tipo == 'superlativo_antiguo':
                resultados = self._query_mas_antiguos(params, limite)
            else:
                resultados = self._query_general(params, limite)
            
            if len(resultados) > 0:
                print(f"✓ Query exitosa: {len(resultados)} resultados")
            else:
                print(f"⚠ Query ejecutada pero sin resultados")
            
            return {
                'success': True,
                'resultados': resultados,
                'analisis': analisis,
                'count': len(resultados)
            }
        except Exception as e:
            print(f"✗ Error ejecutando query: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'resultados': [],
                'analisis': analisis,
                'count': 0,
                'error': str(e)
            }
    
    def _query_mas_vendidos(self, params, limite):
        """Query para juegos más vendidos"""
        filtro_anio = f"FILTER (YEAR(?releaseDate) = {params['anio']})" if 'anio' in params else ""
        
        # FIXED: Query más específica con juegos realmente vendidos
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
            
            {filtro_anio}
            
            # Juegos conocidos como best-sellers
            FILTER (
                CONTAINS(LCASE(?label), 'minecraft') ||
                CONTAINS(LCASE(?label), 'grand theft auto') ||
                CONTAINS(LCASE(?label), 'tetris') ||
                CONTAINS(LCASE(?label), 'mario kart') ||
                CONTAINS(LCASE(?label), 'pokemon')
            )
        }}
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_premiados(self, params, limite):
        """Query para juegos premiados/GOTY"""
        anio = params.get('anio')
        
        if anio:
            filtro = f"FILTER (YEAR(?releaseDate) = {anio})"
        else:
            filtro = ""
        
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
            
            {filtro}
            
            FILTER (
                CONTAINS(LCASE(?label), 'the last of us') ||
                CONTAINS(LCASE(?label), 'the witcher 3') ||
                CONTAINS(LCASE(?label), 'elden ring') ||
                CONTAINS(LCASE(?label), 'god of war') ||
                CONTAINS(LCASE(?label), 'breath of the wild') ||
                CONTAINS(LCASE(?label), "baldur's gate") ||
                CONTAINS(LCASE(?label), 'red dead redemption 2') ||
                CONTAINS(LCASE(?label), 'sekiro') ||
                CONTAINS(LCASE(?label), 'it takes two')
            )
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_mas_populares(self, params, limite):
        """Query para juegos con más jugadores"""
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
                CONTAINS(LCASE(?label), 'league of legends') ||
                CONTAINS(LCASE(?label), 'fortnite') ||
                CONTAINS(LCASE(?label), 'minecraft') ||
                CONTAINS(LCASE(?label), 'roblox') ||
                CONTAINS(LCASE(?label), 'counter-strike') ||
                CONTAINS(LCASE(?label), 'valorant') ||
                CONTAINS(LCASE(?label), 'dota') ||
                CONTAINS(LCASE(?label), 'apex legends') ||
                CONTAINS(LCASE(?label), 'world of warcraft')
            )
        }}
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_mejor_calificados(self, params, limite):
        """Query para juegos mejor calificados"""
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
                CONTAINS(LCASE(?label), 'the legend of zelda') ||
                CONTAINS(LCASE(?label), 'super mario') ||
                CONTAINS(LCASE(?label), 'grand theft auto v') ||
                CONTAINS(LCASE(?label), 'the witcher 3') ||
                CONTAINS(LCASE(?label), 'red dead redemption') ||
                CONTAINS(LCASE(?label), 'half-life') ||
                CONTAINS(LCASE(?label), 'portal')
            )
        }}
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_mas_recientes(self, params, limite):
        """Query para juegos recientes - ARREGLADA"""
        # Si hay desarrollador, filtrarlo
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
            FILTER (lang(?label) = 'en')
            FILTER (YEAR(?releaseDate) >= 2020)
            
            {filtro_dev}
            
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_mas_antiguos(self, params, limite):
        """Query para juegos clásicos"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            ?game dbo:releaseDate ?releaseDate .
            FILTER (lang(?label) = 'en')
            FILTER (YEAR(?releaseDate) <= 1990)
            
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        ORDER BY ?releaseDate
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_general(self, params, limite):
        """Búsqueda general - MÁS FLEXIBLE"""
        # Si hay desarrollador, priorizar eso
        if 'desarrollador' in params:
            dev = params['desarrollador'].title()
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?label .
                ?game dbo:developer ?dev .
                ?dev rdfs:label ?devLabel .
                FILTER (lang(?label) = 'en')
                FILTER (CONTAINS(LCASE(?devLabel), LCASE("{dev}")))
                
                OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
                BIND(?dev as ?developer)
                OPTIONAL {{ ?game dbo:genre ?genre }}
            }}
            ORDER BY DESC(?releaseDate)
            LIMIT {limite}
            """
        # Si hay género
        elif 'genero' in params:
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
            ORDER BY RAND()
            LIMIT {limite}
            """
        else:
            # Búsqueda por término
            termino = params.get('termino', '')
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?label .
                FILTER (lang(?label) = 'en')
                FILTER (CONTAINS(LCASE(?label), LCASE("{termino}")))
                
                OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
                OPTIONAL {{ ?game dbo:developer ?developer }}
                OPTIONAL {{ ?game dbo:genre ?genre }}
            }}
            LIMIT {limite}
            """
        
        return self._ejecutar_query(query)
    
    def _ejecutar_query(self, query):
        """Ejecuta query y formatea resultados"""
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
                        'source': 'dbpedia'
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
