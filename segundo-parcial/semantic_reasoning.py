"""
Módulo para razonamiento semántico
Expande consultas usando contexto, sinónimos, siglas y relaciones semánticas
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import re
from difflib import SequenceMatcher
from multilingual import traductor_global

class SemanticReasoner:
    def __init__(self, sparql_endpoint="http://dbpedia.org/sparql"):
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(10)  # REDUCIDO de 30 a 10 segundos
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0")
        
        # NUEVO: Caché para resultados de DBpedia
        self.cache_dbpedia = {}
        self.cache_expiracion = {}
        self.CACHE_TTL = 300  # 5 minutos
        
        # Diccionario de siglas y abreviaturas comunes en videojuegos
        self.siglas_conocidas = {
            'gta': ['Grand Theft Auto', 'GTA'],
            'cod': ['Call of Duty', 'COD'],
            'bf': ['Battlefield'],
            'ac': ['Assassin\'s Creed', 'Assassins Creed'],
            'tlou': ['The Last of Us'],
            'rdr': ['Red Dead Redemption'],
            'gow': ['God of War', 'Gears of War'],
            'loz': ['The Legend of Zelda', 'Legend of Zelda'],
            'smb': ['Super Mario Bros', 'Super Mario Brothers'],
            'ffvii': ['Final Fantasy VII', 'Final Fantasy 7'],
            'mgs': ['Metal Gear Solid'],
            'tloz': ['The Legend of Zelda'],
            'botw': ['Breath of the Wild'],
            'totk': ['Tears of the Kingdom'],
            'lol': ['League of Legends'],
            'wow': ['World of Warcraft'],
            'csgo': ['Counter-Strike: Global Offensive', 'Counter Strike Global Offensive'],
            'pvz': ['Plants vs. Zombies', 'Plants and Zombies']
        }
        
        # Sinónimos y términos relacionados
        self.sinonimos = {
            'juego': ['videojuego', 'game', 'título'],
            'desarrollador': ['developer', 'estudio', 'company', 'creador'],
            'acción': ['action', 'aventura', 'adventure'],
            'rpg': ['role-playing', 'rol', 'role playing game'],
            'shooter': ['disparos', 'tiros', 'fps', 'tps'],
            'estrategia': ['strategy', 'rts', 'turn-based'],
            'simulación': ['simulation', 'sim', 'simulador'],
        }
        
        # NUEVO: Traductor multilingüe
        self.traductor = traductor_global
    
    def expandir_consulta(self, termino):
        """Expande una consulta OPTIMIZADO con multilingüismo"""
        termino_lower = termino.lower().strip()
        terminos_expandidos = [termino]
        
        print(f"\nEXPANSIÓN SEMÁNTICA MULTILINGÜE DE: '{termino}'")
        print(f"{'─'*60}")
        
        # 0. NUEVO: Expansión multilingüe (PRIORIDAD)
        traducciones = self.traductor.expandir_con_traducciones(termino)
        if len(traducciones) > 1:  # Si hay traducciones además del original
            terminos_expandidos.extend(traducciones[1:])  # Excluir el original
            idioma = self.traductor.detectar_idioma(termino)
            print(f"✓ Multilingüe ({idioma}): {', '.join(traducciones[1:3])}")
        
        # 1. Verificar si es una sigla conocida (INSTANTÁNEO)
        if termino_lower in self.siglas_conocidas:
            expansiones = self.siglas_conocidas[termino_lower]
            terminos_expandidos.extend(expansiones)
            print(f"✓ Sigla detectada: {termino.upper()} → {', '.join(expansiones)}")
        
        # 2. SKIP búsqueda en DBpedia para términos cortos (optimización)
        if len(termino) >= 4:
            # Usar caché si existe
            if termino_lower in self.cache_dbpedia:
                import time
                if time.time() - self.cache_expiracion.get(termino_lower, 0) < self.CACHE_TTL:
                    alternativas_dbpedia = self.cache_dbpedia[termino_lower]
                    if alternativas_dbpedia:
                        terminos_expandidos.extend(alternativas_dbpedia)
                        print(f"✓ DBpedia (caché): {', '.join(alternativas_dbpedia[:2])}")
                else:
                    # Caché expirado, buscar de nuevo (solo si es necesario)
                    pass
        
        # 3. Variaciones (INSTANTÁNEO)
        variaciones = self._generar_variaciones(termino)
        terminos_expandidos.extend(variaciones[:3])  # LIMITAR a 3
        if variaciones:
            print(f"✓ Variaciones: {', '.join(variaciones[:2])}")
        
        # Eliminar duplicados
        terminos_unicos = list(dict.fromkeys(terminos_expandidos))[:5]  # MAX 5 términos
        
        print(f"{'─'*60}")
        print(f"Total: {len(terminos_unicos)} términos (optimizado)")
        print(f"{'─'*60}\n")
        
        return terminos_unicos
    
    def _buscar_nombres_alternativos_dbpedia(self, termino):
        """OPTIMIZADO - caché + query más simple"""
        # Verificar caché primero
        if termino.lower() in self.cache_dbpedia:
            return self.cache_dbpedia[termino.lower()]
        
        alternativas = []
        
        try:
            # Query SIMPLIFICADA - solo buscar por label
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?name
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?name .
                FILTER (lang(?name) = 'en')
                FILTER (CONTAINS(LCASE(?name), LCASE("{termino}")))
            }}
            LIMIT 3
            """
            
            self.sparql.setQuery(query)
            self.sparql.setTimeout(5)  # Timeout corto
            results = self.sparql.query().convert()
            
            if "results" in results and "bindings" in results["results"]:
                for row in results["results"]["bindings"][:3]:  # MAX 3
                    if 'name' in row:
                        alternativas.append(row['name']['value'])
            
            # Guardar en caché
            import time
            self.cache_dbpedia[termino.lower()] = alternativas
            self.cache_expiracion[termino.lower()] = time.time()
            
        except Exception as e:
            print(f"   ⚠ Timeout DBpedia (normal en búsqueda rápida)")
        
        return alternativas[:3]
    
    def _generar_variaciones(self, termino):
        """Genera variaciones del término (con/sin espacios, guiones, etc.)"""
        variaciones = []
        
        # Variación con espacios
        if '_' in termino or '-' in termino:
            variaciones.append(termino.replace('_', ' ').replace('-', ' '))
        
        # Variación sin espacios
        if ' ' in termino:
            variaciones.append(termino.replace(' ', ''))
            variaciones.append(termino.replace(' ', '_'))
        
        # Variación con "The"
        if not termino.lower().startswith('the '):
            variaciones.append(f'The {termino}')
        
        # Eliminar "The" si existe
        if termino.lower().startswith('the '):
            variaciones.append(termino[4:])
        
        # Variación con números romanos/árabes
        numeros_romanos = {
            'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
            'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'
        }
        
        for romano, arabigo in numeros_romanos.items():
            if f' {romano}' in termino or termino.endswith(romano):
                variaciones.append(termino.replace(f' {romano}', f' {arabigo}'))
                variaciones.append(termino.replace(romano, arabigo))
        
        return list(set(variaciones))
    
    def calcular_similitud_semantica(self, termino1, termino2):
        """
        Calcula similitud semántica entre dos términos
        
        Returns:
            float: Score entre 0 y 1
        """
        # Normalizar términos
        t1 = termino1.lower().strip()
        t2 = termino2.lower().strip()
        
        # Coincidencia exacta
        if t1 == t2:
            return 1.0
        
        # Verificar si uno contiene al otro
        if t1 in t2 or t2 in t1:
            return 0.9
        
        # Similitud de secuencia (Levenshtein simplificado)
        similitud_secuencia = SequenceMatcher(None, t1, t2).ratio()
        
        # Verificar siglas
        if self._es_sigla_de(t1, t2) or self._es_sigla_de(t2, t1):
            return 0.95
        
        # Similitud de palabras
        palabras1 = set(t1.split())
        palabras2 = set(t2.split())
        
        if palabras1 and palabras2:
            interseccion = palabras1.intersection(palabras2)
            union = palabras1.union(palabras2)
            similitud_palabras = len(interseccion) / len(union)
            
            # Combinar similitudes
            return max(similitud_secuencia, similitud_palabras)
        
        return similitud_secuencia
    
    def _es_sigla_de(self, sigla, frase):
        """Verifica si un término es sigla de una frase"""
        if len(sigla) < 2 or len(sigla) > 10:
            return False
        
        palabras = frase.split()
        if len(palabras) < 2:
            return False
        
        # Obtener iniciales
        iniciales = ''.join([p[0] for p in palabras if p])
        
        return sigla.upper() == iniciales.upper()
    
    def buscar_semanticamente_dbpedia(self, termino, limite=20):
        """Búsqueda multilingüe MEJORADA con fallback a inglés"""
        # Detectar idioma original
        idioma_original = self.traductor.detectar_idioma(termino)
        print(f"   ✓ Idioma detectado: {idioma_original}")
        
        # PASO 1: Intentar buscar en el idioma original
        termino_busqueda = termino
        resultados = self._buscar_en_idioma(termino_busqueda, idioma_original, limite)
        
        # PASO 2: Si no hay resultados Y no es inglés, traducir y buscar en inglés
        if len(resultados) == 0 and idioma_original != 'en':
            print(f"\n   ⚠ Sin resultados en {idioma_original}, traduciendo a inglés...")
            termino_en = self.traductor.obtener_nombre_ingles(termino)
            
            if termino_en != termino:
                print(f"   → Traducción: '{termino}' → '{termino_en}'")
                resultados = self._buscar_en_idioma(termino_en, 'en', limite)
                
                # Marcar que estos resultados necesitan traducción de vuelta
                for resultado in resultados:
                    resultado['idioma_contenido'] = 'en'
                    resultado['idioma_busqueda'] = idioma_original
                    resultado['necesita_traduccion'] = True
        else:
            # Marcar resultados que ya están en el idioma correcto
            for resultado in resultados:
                resultado['idioma_contenido'] = idioma_original
                resultado['idioma_busqueda'] = idioma_original
                resultado['necesita_traduccion'] = False
        
        return resultados
    
    def _buscar_en_idioma(self, termino, idioma, limite):
        """Busca en DBpedia en un idioma específico"""
        terminos_expandidos = self._expandir_simple(termino)
        resultados = []
        
        for termino_exp in terminos_expandidos[:2]:
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?game ?label ?releaseDate ?developer ?genre
            WHERE {{
                ?game a dbo:VideoGame .
                ?game rdfs:label ?label .
                FILTER (lang(?label) = '{idioma}')
                FILTER (CONTAINS(LCASE(?label), LCASE("{termino_exp}")))
                OPTIONAL {{ ?game dbo:releaseDate ?releaseDate }}
                OPTIONAL {{ ?game dbo:developer ?developer }}
                OPTIONAL {{ ?game dbo:genre ?genre }}
            }}
            LIMIT {limite}
            """
            
            try:
                self.sparql.setQuery(query)
                self.sparql.setTimeout(8)
                results = self.sparql.query().convert()
                
                if "results" in results and "bindings" in results["results"]:
                    for row in results["results"]["bindings"]:
                        score = self.calcular_similitud_semantica(termino, row['label']['value'])
                        row['semantic_score'] = score
                        resultados.append(row)
                    
                    if len(resultados) > 0:
                        break
            except Exception as e:
                print(f"      ✗ Error: {str(e)[:100]}")
        
        return resultados
    def _expandir_simple(self, termino):
        """Expansión simplificada sin multilingüismo (ya traducido)"""
        terminos = [termino]
    
        # Variaciones básicas
        if ' ' in termino:
            terminos.append(termino.replace(' ', ''))
        
        # Agregar/quitar "The"
        if not termino.lower().startswith('the '):
            terminos.append(f'The {termino}')
        else:
            terminos.append(termino[4:])
        
        return list(dict.fromkeys(terminos))[:3]
    
    def _agregar_labels_multilingues(self, resultados, idioma_destino):
        """Agrega labels en el idioma solicitado a los resultados"""
        for resultado in resultados:
            game_uri = resultado['game']['value']
            
            # Query para obtener label en el idioma destino
            query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?label
            WHERE {{
                <{game_uri}> rdfs:label ?label .
                FILTER (lang(?label) = '{idioma_destino}')
            }}
            LIMIT 1
            """
            
            try:
                self.sparql.setQuery(query)
                self.sparql.setTimeout(3)
                results = self.sparql.query().convert()
                
                if "results" in results and "bindings" in results["results"]:
                    bindings = results["results"]["bindings"]
                    if len(bindings) > 0:
                        # Agregar label traducido
                        resultado['label_traducido'] = bindings[0]['label']
                        print(f"      ✓ Label {idioma_destino}: {bindings[0]['label']['value']}")
                    else:
                        # Si no hay traducción, usar el inglés
                        resultado['label_traducido'] = resultado['label']
                        print(f"      ⊙ Sin traducción a {idioma_destino}, usando inglés")
                else:
                    resultado['label_traducido'] = resultado['label']
            except Exception as e:
                # En caso de error, usar el inglés
                resultado['label_traducido'] = resultado['label']
                print(f"      ✗ Error obteniendo label {idioma_destino}: {str(e)[:50]}")
        
        return resultados
