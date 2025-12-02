"""
Módulo de Multilingüismo para Búsqueda de Videojuegos
Soporta traducción entre español, inglés, francés, alemán, italiano, portugués y japonés
"""

class MultilingualTranslator:
    def __init__(self):
        # Diccionario de traducciones español -> otros idiomas
        self.traducciones_juegos = {
            # Formato: titulo_normalizado: {idioma: traducción}
            'the_last_of_us': {
                'es': 'el último de nosotros',
                'en': 'The Last of Us',
                'fr': ['The Last of Us', 'Le Dernier d\'Entre Nous', "Le Dernier d'Entre Nous"],  # FIXED: agregadas variantes francesas
                'de': 'The Last of Us',
                'it': 'The Last of Us',
                'pt': 'The Last of Us',
                'ja': 'ザ・ラスト・オブ・アス'
            },
            'the_witcher': {
                'es': ['el brujo', 'el hechicero'],
                'en': 'The Witcher',
                'fr': ['Le Sorceleur', 'The Witcher'],  # FIXED: ambas variantes
                'de': 'Der Hexer',
                'it': 'Lo Strigo',
                'pt': 'O Bruxo',
                'ja': 'ウィッチャー'
            },
            'grand_theft_auto': {
                'es': ['gran robo auto', 'robo de autos'],
                'en': 'Grand Theft Auto',
                'fr': 'Grand Theft Auto',
                'de': 'Grand Theft Auto',
                'it': 'Grand Theft Auto',
                'pt': 'Grand Theft Auto',
                'ja': 'グランド・セフト・オート'
            },
            'the_legend_of_zelda': {
                'es': ['la leyenda de zelda', 'leyenda de zelda'],
                'en': 'The Legend of Zelda',
                'fr': 'La Légende de Zelda',
                'de': 'Die Legende von Zelda',
                'it': 'La Leggenda di Zelda',
                'pt': 'A Lenda de Zelda',
                'ja': 'ゼルダの伝説'
            },
            'god_of_war': {
                'es': 'dios de la guerra',
                'en': 'God of War',
                'fr': 'God of War',
                'de': 'God of War',
                'it': 'God of War',
                'pt': 'God of War',
                'ja': 'ゴッド・オブ・ウォー'
            },
            'dark_souls': {
                'es': 'almas oscuras',
                'en': 'Dark Souls',
                'fr': 'Dark Souls',
                'de': 'Dark Souls',
                'it': 'Dark Souls',
                'pt': 'Dark Souls',
                'ja': 'ダークソウル'
            },
            'call_of_duty': {
                'es': 'llamado del deber',
                'en': 'Call of Duty',
                'fr': "L'Appel du Devoir",
                'de': 'Call of Duty',
                'it': 'Call of Duty',
                'pt': 'Call of Duty',
                'ja': 'コール オブ デューティ'
            },
            'red_dead_redemption': {
                'es': ['redención del vaquero', 'muerto rojo'],
                'en': 'Red Dead Redemption',
                'fr': 'Red Dead Redemption',
                'de': 'Red Dead Redemption',
                'it': 'Red Dead Redemption',
                'pt': 'Red Dead Redemption',
                'ja': 'レッド・デッド・リデンプション'
            },
            'final_fantasy': {
                'es': 'fantasía final',
                'en': 'Final Fantasy',
                'fr': 'Final Fantasy',
                'de': 'Final Fantasy',
                'it': 'Final Fantasy',
                'pt': 'Final Fantasy',
                'ja': 'ファイナルファンタジー'
            },
            'resident_evil': {
                'es': ['residente malvado', 'residente evil'],
                'en': 'Resident Evil',
                'fr': 'Resident Evil',
                'de': 'Resident Evil',
                'it': 'Resident Evil',
                'pt': 'Resident Evil',
                'ja': 'バイオハザード'
            },
            'minecraft': {
                'es': 'minecraft',
                'en': 'Minecraft',
                'fr': 'Minecraft',
                'de': 'Minecraft',
                'it': 'Minecraft',
                'pt': 'Minecraft',
                'ja': 'マインクラフト'
            },
            'super_mario_bros': {
                'es': ['super mario hermanos', 'mario bros'],
                'en': 'Super Mario Bros',
                'fr': 'Super Mario Bros',
                'de': 'Super Mario Bros',
                'it': 'Super Mario Bros',
                'pt': 'Super Mario Bros',
                'ja': 'スーパーマリオブラザーズ'
            },
            'elden_ring': {
                'es': 'anillo de elden',
                'en': 'Elden Ring',
                'fr': 'Elden Ring',
                'de': 'Elden Ring',
                'it': 'Elden Ring',
                'pt': 'Elden Ring',
                'ja': 'エルデンリング'
            }
        }
        
        # Índice inverso para búsqueda rápida
        self._construir_indice_inverso()
        
        # Palabras clave por idioma
        self.palabras_clave = {
            'es': {
                'el': 'the', 'la': 'the', 'los': 'the', 'las': 'the',
                'de': 'of', 'del': 'of the', 'y': 'and', 'o': 'or'
            },
            'fr': {
                'le': 'the', 'la': 'the', 'les': 'the', "l'": 'the',
                'de': 'of', 'du': 'of the', 'et': 'and', 'ou': 'or'
            },
            'de': {
                'der': 'the', 'die': 'the', 'das': 'the',
                'von': 'of', 'und': 'and', 'oder': 'or'
            },
            'it': {
                'il': 'the', 'la': 'the', 'lo': 'the', 'i': 'the', 'gli': 'the',
                'di': 'of', 'e': 'and', 'o': 'or'
            },
            'pt': {
                'o': 'the', 'a': 'the', 'os': 'the', 'as': 'the',
                'de': 'of', 'do': 'of the', 'e': 'and', 'ou': 'or'
            }
        }
        
        # Códigos de idioma ISO
        self.idiomas_soportados = ['es', 'en', 'fr', 'de', 'it', 'pt', 'ja']
        self.nombres_idiomas = {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ja': '日本語'
        }
    
    def _construir_indice_inverso(self):
        """Construye un índice inverso para búsqueda rápida"""
        self.indice_inverso = {}
        
        for key, traducciones in self.traducciones_juegos.items():
            for idioma, valor in traducciones.items():
                if isinstance(valor, list):
                    # Manejar listas de variantes
                    for variante in valor:
                        self.indice_inverso[variante.lower()] = (key, idioma)
                else:
                    self.indice_inverso[valor.lower()] = (key, idioma)
    
    def detectar_idioma(self, termino):
        """
        Detecta el idioma del término usando múltiples heurísticas
        
        Returns:
            str: Código de idioma ('es', 'en', 'fr', 'de', 'it', 'pt', 'ja') o 'unknown'
        """
        termino_lower = termino.lower().strip()
        
        # 1. Búsqueda en índice inverso (más precisa)
        if termino_lower in self.indice_inverso:
            _, idioma = self.indice_inverso[termino_lower]
            print(f"   ✓ Idioma detectado por índice: {idioma}")
            return idioma
        
        # 2. Detectar caracteres japoneses
        if any('\u3040' <= char <= '\u309F' or  # Hiragana
               '\u30A0' <= char <= '\u30FF' or  # Katakana
               '\u4E00' <= char <= '\u9FFF'     # Kanji
               for char in termino):
            print(f"   ✓ Idioma detectado por caracteres: ja")
            return 'ja'
        
        # 3. Detectar francés por patrones específicos
        palabras_fr = ['le', 'la', 'les', 'de', 'du', 'des', "l'", 'd\'', 'dernier', 'entre', 'sorceleur']
        termino_words = termino_lower.split()
        
        if any(word in palabras_fr for word in termino_words):
            print(f"   ✓ Idioma detectado por palabras clave: fr")
            return 'fr'
        
        # 4. Detectar por acentos franceses específicos
        if any(c in termino for c in ['é', 'è', 'ê', 'à', 'ù', 'û', 'ô', 'î']):
            if 'ç' in termino.lower() or any(word in termino_lower for word in ['nous', 'entre', 'nous', 'le', 'la']):
                print(f"   ✓ Idioma detectado por acentos: fr")
                return 'fr'
        
        # 5. Detectar alemán
        if any(c in termino for c in ['ä', 'ö', 'ü', 'ß']):
            print(f"   ✓ Idioma detectado por caracteres: de")
            return 'de'
        
        # 6. Detectar italiano
        if any(c in termino for c in ['ò']):
            print(f"   ✓ Idioma detectado por caracteres: it")
            return 'it'
        
        # 7. Detectar portugués
        if any(c in termino for c in ['ã', 'õ']):
            print(f"   ✓ Idioma detectado por caracteres: pt")
            return 'pt'
        
        # 8. Por palabras clave
        palabras = termino_lower.split()
        puntuaciones = {idioma: 0 for idioma in self.idiomas_soportados}
        
        for palabra in palabras:
            for idioma, keywords in self.palabras_clave.items():
                if palabra in keywords:
                    puntuaciones[idioma] += 1
        
        max_puntuacion = max(puntuaciones.values())
        if max_puntuacion > 0:
            idioma_detectado = max(puntuaciones, key=puntuaciones.get)
            print(f"   ✓ Idioma detectado por puntuación: {idioma_detectado}")
            return idioma_detectado
        
        # 9. Detectar inglés vs español
        palabras_en = sum(1 for p in palabras if p in ['the', 'of', 'and', 'or', 'in'])
        palabras_es = sum(1 for p in palabras if p in ['el', 'la', 'de', 'y', 'o', 'en'])
        
        if palabras_en > palabras_es:
            print(f"   ✓ Idioma detectado por defecto: en")
            return 'en'
        elif palabras_es > palabras_en:
            print(f"   ✓ Idioma detectado por defecto: es")
            return 'es'
        
        # Default: inglés
        print(f"   ✓ Idioma por defecto: en")
        return 'en'
    
    def traducir_a_todos_idiomas(self, termino):
        """
        Traduce un término a todos los idiomas soportados
        
        Returns:
            dict: {idioma: [traducciones]}
        """
        termino_lower = termino.lower().strip()
        traducciones = {idioma: [] for idioma in self.idiomas_soportados}
        
        # Buscar en índice inverso
        if termino_lower in self.indice_inverso:
            key, _ = self.indice_inverso[termino_lower]
            
            for idioma in self.idiomas_soportados:  # FIXED: era self.idiomas_soportadas
                if idioma in self.traducciones_juegos[key]:
                    valor = self.traducciones_juegos[key][idioma]
                    if isinstance(valor, list):
                        traducciones[idioma].extend(valor)
                    else:
                        traducciones[idioma].append(valor)
        
        # Agregar término original
        idioma_detectado = self.detectar_idioma(termino)
        if termino not in traducciones[idioma_detectado]:
            traducciones[idioma_detectado].append(termino)
        
        return traducciones
    
    def obtener_nombre_ingles(self, termino):
        """
        Obtiene el nombre en inglés de un término en cualquier idioma
        
        Args:
            termino: Término en cualquier idioma
            
        Returns:
            str: Nombre en inglés o el término original si no se encuentra
        """
        termino_lower = termino.lower().strip()
        
        # Buscar en índice inverso
        if termino_lower in self.indice_inverso:
            key, _ = self.indice_inverso[termino_lower]
            
            # Retornar versión en inglés
            if 'en' in self.traducciones_juegos[key]:
                nombre_en = self.traducciones_juegos[key]['en']
                print(f"   ✓ Traducción a inglés: '{termino}' → '{nombre_en}'")
                return nombre_en
        
        # Si no se encuentra, retornar original
        return termino

    def agregar_traduccion_juego(self, titulo_normalizado, traducciones_dict):
        """
        Agrega traducciones de un nuevo juego
        
        Args:
            titulo_normalizado: Clave única (ej: 'the_last_of_us')
            traducciones_dict: {idioma: traducción}
        """
        self.traducciones_juegos[titulo_normalizado] = traducciones_dict
        self._construir_indice_inverso()
        print(f"✓ Traducciones agregadas para: {titulo_normalizado}")
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del sistema multilingüe"""
        return {
            'total_juegos_traducidos': len(self.traducciones_juegos),
            'idiomas_soportados': len(self.idiomas_soportados),
            'idiomas': self.nombres_idiomas,
            'entradas_indice': len(self.indice_inverso)
        }
    
    def expandir_con_traducciones(self, termino):
        """
        Expande un término con todas sus traducciones en todos los idiomas
        
        Returns:
            list: Lista de términos en diferentes idiomas
        """
        expansiones = [termino]  # Incluir original
        
        todas_traducciones = self.traducir_a_todos_idiomas(termino)
        
        for idioma, lista in todas_traducciones.items():
            expansiones.extend(lista)
        
        # Eliminar duplicados preservando orden
        return list(dict.fromkeys(expansiones))
    
    def obtener_traducciones_por_idioma(self, termino, idioma_destino):
        """
        Obtiene traducciones específicas para un idioma
        
        Args:
            termino: Término a traducir
            idioma_destino: Código de idioma destino ('es', 'en', 'fr', etc.)
            
        Returns:
            list: Lista de traducciones en el idioma destino
        """
        if idioma_destino not in self.idiomas_soportados:
            return []
        
        todas = self.traducir_a_todos_idiomas(termino)
        return todas.get(idioma_destino, [])
    
    def obtener_codigo_idioma_dbpedia(self, termino):
        """
        Obtiene el código de idioma para usar en consultas DBpedia
        
        Returns:
            str: Código de idioma para filtro SPARQL (ej: 'es', 'en', 'fr')
        """
        return self.detectar_idioma(termino)


# Instancia global para uso fácil
traductor_global = MultilingualTranslator()


# Funciones de conveniencia
def traducir_es_en(termino):
    """Atajo para traducir español -> inglés"""
    return traductor_global.traducir_es_a_en(termino)


def traducir_en_es(termino):
    """Atajo para traducir inglés -> español"""
    return traductor_global.traducir_en_a_es(termino)


def expandir_multilingue(termino):
    """Atajo para expandir con traducciones"""
    return traductor_global.expandir_con_traducciones(termino)


# Para testing
if __name__ == "__main__":
    print("="*60)
    print("SISTEMA DE MULTILINGÜISMO - PRUEBAS")
    print("="*60)
    
    traductor = MultilingualTranslator()
    
    # Pruebas
    pruebas = [
        "el último de nosotros",
        "el hechicero",
        "gran robo auto",
        "The Last of Us",
        "God of War",
        "leyenda de zelda"
    ]
    
    for termino in pruebas:
        print(f"\nTermino: '{termino}'")
        print(f"Idioma detectado: {traductor.detectar_idioma(termino)}")
        print(f"Expansiones: {traductor.expandir_con_traducciones(termino)}")
    
    print(f"\n{'='*60}")
    print("Estadísticas:")
    stats = traductor.obtener_estadisticas()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("="*60)
