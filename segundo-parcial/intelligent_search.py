"""
Módulo de Búsqueda Inteligente con NLP
Interpreta consultas en lenguaje natural tipo Google
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import re
import datetime

class IntelligentSearch:
    def __init__(self, sparql_endpoint="http://dbpedia.org/sparql"):
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(15)
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0")
        
        # ACTUALIZADO: Ganadores GOTY hasta 2024
        self.ganadores_goty = {
            2024: "astro bot",  # ✅ NUEVO: Ganador GOTY 2024
            2023: "baldur's gate 3",
            2022: "elden ring",
            2021: "it takes two",
            2020: "the last of us part ii",
            2019: "sekiro",
            2018: "god of war",
            2017: "the legend of zelda: breath of the wild",
            2016: "overwatch",
            2015: "the witcher 3"
        }
        
        # NUEVO: Juegos garantizados por categoría
        self.juegos_garantizados = {
            'mas_vendido': ['minecraft', 'grand theft auto v', 'tetris', 'wii sports', 'playerunknowns battlegrounds'],
            'mas_jugadores': ['minecraft', 'fortnite', 'league of legends', 'roblox', 'counter-strike', 'valorant'],
            'mejor_calificado': ["the legend of zelda", "super mario", "the witcher 3", "red dead redemption", "elden ring", "portal 2"],
            'reciente_2024': ['astro bot', 'metaphor refantazio', 'final fantasy vii rebirth', 'helldivers 2', 'stellar blade', 'black myth wukong'],
            'reciente_2025': ['grand theft auto vi', 'pokemon legends z-a', 'mafia the old country', 'ghost of yotei', 'death stranding 2']
        }
        
        # Traducciones mejoradas
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
        
        # Patrones de consulta
        self.patrones = {
            'mas_vendido': {
                'keywords': ['más vendido', 'mas vendido', 'best selling', 'mayor venta', 
                           'top ventas', 'más exitoso', 'mas exitoso', 'bestseller'],
                'tipo': 'superlativo_ventas',
                'descripcion': 'Juegos más vendidos de todos los tiempos',
                'singular': True
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
            'mas_reciente': {
                'keywords': ['más reciente', 'mas reciente', 'newest', 'último lanzamiento',
                           'ultimo lanzamiento', 'latest', 'más nuevo', 'recientes', 'nuevos'],
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
        """Traduce consulta español a inglés"""
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
            'singular': False,
            'consulta_traducida': self.traducir_consulta(consulta)
        }
        
        # 1. Detectar año específico
        anio_match = re.search(r'20\d{2}', consulta)
        if anio_match:
            anio = int(anio_match.group())
            resultado['parametros']['anio'] = anio
            resultado['entidades'].append(('AÑO', anio))
            resultado['confianza'] = 0.7
            print(f"✓ Año detectado: {anio}")
        
        # 2. Detectar patrones
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
                            'singular': patron_info.get('singular', False)
                        }
        
        if mejor_patron:
            resultado['tipo'] = mejor_patron['tipo']
            resultado['descripcion'] = mejor_patron['descripcion']
            resultado['confianza'] = max_confianza
            resultado['singular'] = mejor_patron['singular']
            resultado['entidades'].append(('PATRON', mejor_patron['keyword']))
            print(f"✓ Patrón: {mejor_patron['tipo']}")
        
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
                    if resultado['confianza'] < 0.6:
                        resultado['confianza'] = 0.6
                    print(f"✓ Género: {genero_key}")
                    break
        
        # 4. Detectar desarrolladores
        desarrolladores = [
            'nintendo', 'sony', 'microsoft', 'valve', 'rockstar', 'ea', 
            'ubisoft', 'activision', 'capcom', 'bethesda', 'fromsoftware',
            'naughty dog', 'cd projekt', 'team asobi'
        ]
        
        for dev in desarrolladores:
            if dev in consulta_lower:
                resultado['parametros']['desarrollador'] = dev
                resultado['entidades'].append(('DESARROLLADOR', dev))
                if resultado['confianza'] < 0.6:
                    resultado['confianza'] = 0.6
                print(f"✓ Desarrollador: {dev}")
                break
        
        # 5. Detectar términos temporales
        temporales = {
            'reciente': 'superlativo_reciente',
            'nuevo': 'superlativo_reciente',
            'latest': 'superlativo_reciente',
            'recientes': 'superlativo_reciente',
            'nuevos': 'superlativo_reciente',
            'antiguo': 'superlativo_antiguo',
            'clásico': 'superlativo_antiguo',
            'old': 'superlativo_antiguo'
        }
        
        for temp, tipo_temporal in temporales.items():
            if temp in consulta_lower:
                resultado['tipo'] = tipo_temporal
                resultado['descripcion'] = 'Juegos recientes' if 'reciente' in tipo_temporal else 'Juegos clásicos'
                resultado['entidades'].append(('TEMPORAL', temp))
                if resultado['confianza'] < 0.7:
                    resultado['confianza'] = 0.7
                print(f"✓ Término temporal: {temp}")
                break
        
        # 6. Garantía: confianza mínima
        if len(resultado['entidades']) > 0 and resultado['confianza'] < 0.5:
            resultado['confianza'] = 0.5
        
        print(f"{'─'*60}")
        print(f"Tipo: {resultado['tipo']}, Confianza: {resultado['confianza']:.2%}")
        print(f"{'='*60}\n")
        
        return resultado
    
    def buscar_inteligente(self, consulta, limite=15):
        """Ejecuta búsqueda CON GARANTÍA DE RESULTADOS"""
        analisis = self.analizar_consulta(consulta)
        
        # NUEVO: Reducir umbral
        if analisis['confianza'] < 0.2:
            print(f"→ Confianza baja, forzando resultados generales")
            return self._forzar_resultados_generales(consulta, analisis)
        
        tipo = analisis['tipo']
        params = analisis['parametros']
        singular = analisis.get('singular', False)
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
            
            resultados = self._filtrar_y_deduplicar(resultados, params)
            
            # NUEVO: Si no hay resultados, forzar
            if len(resultados) == 0:
                print(f"⚠ Sin resultados de query, forzando juegos garantizados...")
                resultados = self._forzar_juegos_garantizados(tipo, params)
            
            return {
                'success': True,
                'resultados': resultados,
                'analisis': analisis,
                'count': len(resultados)
            }
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return self._forzar_resultados_generales(consulta, analisis)
    
    def _forzar_juegos_garantizados(self, tipo, params):
        """Fuerza juegos cuando la query falla"""
        juegos_forzados = []
        categoria = None
        
        if tipo == 'superlativo_ventas':
            categoria = 'mas_vendido'
        elif tipo == 'superlativo_jugadores':
            categoria = 'mas_jugadores'
        elif tipo == 'superlativo_calificacion':
            categoria = 'mejor_calificado'
        elif tipo == 'superlativo_reciente':
            anio = params.get('anio')
            if anio == 2024:
                categoria = 'reciente_2024'
            elif anio == 2025:
                categoria = 'reciente_2025'
        elif tipo == 'premio':
            # NUEVO: Forzar GOTY si no hay resultados
            anio = params.get('anio')
            if anio and anio in self.ganadores_goty:
                juego = self._crear_juego_fallback(self.ganadores_goty[anio], tipo)
                juego['anios'] = [anio]  # Forzar año correcto
                return [juego]
        
        if categoria and categoria in self.juegos_garantizados:
            for titulo in self.juegos_garantizados[categoria][:5]:
                juegos_forzados.append(self._crear_juego_fallback(titulo, tipo))
        
        print(f"   ✓ {len(juegos_forzados)} juegos garantizados forzados")
        return juegos_forzados
    
    def _crear_juego_fallback(self, titulo, tipo):
        """Crea entrada de juego con datos mínimos"""
        # NUEVO: Año específico para juegos conocidos
        anios_conocidos = {
            'astro bot': [2024],
            'baldurs gate 3': [2023],
            "baldur's gate 3": [2023],
            'elden ring': [2022],
            'it takes two': [2021],
            'the last of us part ii': [2020],
            'sekiro': [2019],
            'god of war': [2018],
            'the legend of zelda breath of the wild': [2017],
            'breath of the wild': [2017],
            'overwatch': [2016],
            'the witcher 3': [2015]
        }
        
        anio = anios_conocidos.get(titulo.lower(), [datetime.datetime.now().year])
        
        return {
            'game': f'http://dbpedia.org/resource/{titulo.replace(" ", "_")}',
            'titulo': titulo.title(),
            'anios': anio,
            'desarrollador': 'Various',
            'generos': ['Action'],
            'source': 'dbpedia',
            'fallback': True
        }
    
    def _forzar_resultados_generales(self, consulta, analisis):
        """FALLBACK FINAL"""
        print("   → Forzando resultados genéricos...")
        juegos_comunes = [
            'Minecraft', 'Grand Theft Auto V', 'The Legend of Zelda', 
            'Super Mario Bros', 'The Witcher 3', 'Elden Ring',
            'Red Dead Redemption 2', 'God of War', 'The Last of Us', 'Astro Bot'
        ]
        return {
            'success': True,
            'resultados': [self._crear_juego_fallback(j, 'general') for j in juegos_comunes[:10]],
            'analisis': analisis,
            'count': 10,
            'forced': True
        }
    
    def _query_premiados(self, params, limite):
        """Query GOTY con Astro Bot 2024 - MEJORADO con filtro de año exacto"""
        anio = params.get('anio')
        
        if anio and anio in self.ganadores_goty:
            ganador = self.ganadores_goty[anio]
            print(f"   ✓ GOTY {anio} garantizado: {ganador.title()}")
            
            # NUEVO: Query más estricta con año exacto
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?label .
                ?game dbo:releaseDate ?releaseDate .
                FILTER (lang(?label) = 'en')
                FILTER (CONTAINS(LCASE(?label), '{ganador}'))
                FILTER (YEAR(?releaseDate) = {anio})
                
                OPTIONAL {{ ?game dbo:developer ?developer }}
                OPTIONAL {{ ?game dbo:genre ?genre }}
            }}
            LIMIT {limite}
            """
        else:
            ganadores_str = '|'.join(self.ganadores_goty.values())
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?label .
                FILTER (lang(?label) = 'en')
                FILTER (REGEX(LCASE(?label), '({ganadores_str})'))
                
                OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
                OPTIONAL {{ ?game dbo:developer ?developer }}
                OPTIONAL {{ ?game dbo:genre ?genre }}
            }}
            ORDER BY DESC(?releaseDate)
            LIMIT {limite}
            """
        
        return self._ejecutar_query(query)
    
    def _query_mas_vendidos(self, params, limite):
        """Query más vendidos"""
        filtro_anio = f"FILTER (YEAR(?releaseDate) <= 2024)" if 'anio' not in params else f"FILTER (YEAR(?releaseDate) = {params['anio']})"
        
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
    
    def _query_mas_populares(self, params, limite):
        """Query más jugadores"""
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
                CONTAINS(LCASE(?label), 'minecraft') ||
                CONTAINS(LCASE(?label), 'league of legends') ||
                CONTAINS(LCASE(?label), 'fortnite') ||
                CONTAINS(LCASE(?label), 'roblox') ||
                CONTAINS(LCASE(?label), 'counter-strike') ||
                CONTAINS(LCASE(?label), 'valorant')
            )
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_mas_recientes(self, params, limite):
        """Query juegos recientes"""
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
        """Query mejor calificados"""
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
                CONTAINS(LCASE(?label), 'the witcher 3') ||
                CONTAINS(LCASE(?label), 'elden ring') ||
                CONTAINS(LCASE(?label), "baldur's gate")
            )
        }}
        ORDER BY DESC(?releaseDate)
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_mas_antiguos(self, params, limite):
        """Query juegos antiguos"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
        WHERE {{
            ?game a dbo:VideoGame .
            ?game rdfs:label ?label .
            ?game dbo:releaseDate ?releaseDate .
            FILTER (lang(?label) = 'en')
            FILTER (YEAR(?releaseDate) < 1990)
            
            OPTIONAL {{ ?game dbo:developer ?developer }}
            OPTIONAL {{ ?game dbo:genre ?genre }}
        }}
        ORDER BY ?releaseDate
        LIMIT {limite}
        """
        return self._ejecutar_query(query)
    
    def _query_general(self, params, limite):
        """Query general"""
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
    
    def _filtrar_y_deduplicar(self, resultados, params):
        """Filtra duplicados MEJORADO - Prioriza año específico si existe"""
        vistos = {}
        filtrados = []
        anio_actual = datetime.datetime.now().year
        anio_buscado = params.get('anio')
        
        for resultado in resultados:
            titulo = resultado['titulo'].lower()
            
            # Validar año
            if resultado.get('anios'):
                anio_juego = resultado['anios'][0]
                if anio_juego > anio_actual + 1:
                    continue
            
            # Si ya vimos este título
            if titulo in vistos:
                # Si estamos buscando un año específico y este resultado coincide
                if anio_buscado and resultado.get('anios') and resultado['anios'][0] == anio_buscado:
                    # Reemplazar el anterior con este
                    indice_anterior = vistos[titulo]
                    filtrados[indice_anterior] = resultado
                    print(f"   ✓ Reemplazando '{titulo}' con versión del {anio_buscado}")
                continue
            
            vistos[titulo] = len(filtrados)
            filtrados.append(resultado)
        
        # NUEVO: Si buscamos año específico, priorizar resultados de ese año
        if anio_buscado:
            filtrados.sort(key=lambda x: 0 if (x.get('anios') and x['anios'][0] == anio_buscado) else 1)
        
        return filtrados
    
    def _ejecutar_query(self, query):
        """Ejecuta query"""
        self.sparql.setQuery(query)
        
        try:
            print(f"   Ejecutando query...")
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