"""
Módulo de Multilingüismo para Búsqueda de Videojuegos
Soporta traducción español <-> inglés para títulos de videojuegos
"""

class MultilingualTranslator:
    def __init__(self):
        # Diccionario de traducciones español -> inglés
        self.traducciones_es_en = {
            # Juegos populares
            'el último de nosotros': 'The Last of Us',
            'ultimo de nosotros': 'The Last of Us',
            'el hechicero': 'The Witcher',
            'brujo': 'The Witcher',
            'gran robo auto': 'Grand Theft Auto',
            'robo de autos': 'Grand Theft Auto',
            'leyenda de zelda': 'The Legend of Zelda',
            'la leyenda de zelda': 'The Legend of Zelda',
            'super mario hermanos': 'Super Mario Bros',
            'mario bros': 'Super Mario Bros',
            'dios de la guerra': 'God of War',
            'almas oscuras': 'Dark Souls',
            'campo de batalla': 'Battlefield',
            'llamado del deber': 'Call of Duty',
            'credo del asesino': 'Assassin\'s Creed',
            'asesinos': 'Assassin\'s Creed',
            'redención del vaquero': 'Red Dead Redemption',
            'muerto rojo': 'Red Dead Redemption',
            'horizonte cero amanecer': 'Horizon Zero Dawn',
            'anillo de elden': 'Elden Ring',
            'aliento salvaje': 'Breath of the Wild',
            'aliento de lo salvaje': 'Breath of the Wild',
            'lágrimas del reino': 'Tears of the Kingdom',
            'minecraft': 'Minecraft',
            'portal': 'Portal',
            'media vida': 'Half-Life',
            'fortnite': 'Fortnite',
            'entre nosotros': 'Among Us',
            'liga de leyendas': 'League of Legends',
            'mundo de warcraft': 'World of Warcraft',
            'super esmash hermanos': 'Super Smash Bros',
            'pokemon': 'Pokémon',
            'final fantasy': 'Final Fantasy',
            'metal gear': 'Metal Gear',
            'residente malvado': 'Resident Evil',
            'residente evil': 'Resident Evil',
            'demonio puede llorar': 'Devil May Cry',
            'cazador de monstruos': 'Monster Hunter',
            'sangre': 'Bloodborne',
            'sekiro': 'Sekiro',
            'cyberpunk': 'Cyberpunk',
            'destino': 'Destiny',
            'halo': 'Halo',
            'gears of war': 'Gears of War',
            'uncharted': 'Uncharted',
            'tomb raider': 'Tomb Raider',
            'saqueador de tumbas': 'Tomb Raider',
            'bioshock': 'BioShock',
            'fallout': 'Fallout',
            'skyrim': 'Skyrim',
            'elder scrolls': 'The Elder Scrolls',
            'pergaminos antiguos': 'The Elder Scrolls',
            'dragon age': 'Dragon Age',
            'era del dragon': 'Dragon Age',
            'mass effect': 'Mass Effect',
            'efecto masivo': 'Mass Effect',
            'starcraft': 'StarCraft',
            'warcraft': 'Warcraft',
            'diablo': 'Diablo',
            'overwatch': 'Overwatch',
            'apex legends': 'Apex Legends',
            'valorant': 'Valorant',
            'counter strike': 'Counter-Strike',
            'dota': 'Dota',
            'rocket league': 'Rocket League',
            'fifa': 'FIFA',
            'pes': 'Pro Evolution Soccer',
            'nba': 'NBA',
            'madden': 'Madden NFL',
            'forza': 'Forza',
            'gran turismo': 'Gran Turismo',
            'need for speed': 'Need for Speed',
            'necesidad de velocidad': 'Need for Speed',
            'street fighter': 'Street Fighter',
            'peleador callejero': 'Street Fighter',
            'tekken': 'Tekken',
            'mortal kombat': 'Mortal Kombat',
            'souls like': 'Soulslike',
            'almas': 'Souls',
            'persona': 'Persona',
            'kingdom hearts': 'Kingdom Hearts',
            'corazones del reino': 'Kingdom Hearts',
            'final fantasy vii': 'Final Fantasy VII',
            'final fantasy 7': 'Final Fantasy VII',
            'chrono trigger': 'Chrono Trigger',
            'castillo crashers': 'Castle Crashers',
            'hollow knight': 'Hollow Knight',
            'caballero hueco': 'Hollow Knight',
            'celeste': 'Celeste',
            'undertale': 'Undertale',
            'deltarune': 'Deltarune',
            'stardew valley': 'Stardew Valley',
            'valle stardew': 'Stardew Valley',
            'terraria': 'Terraria',
            'dont starve': 'Don\'t Starve',
            'no te mueras de hambre': 'Don\'t Starve',
            'phasmophobia': 'Phasmophobia',
            'miedo': 'Phasmophobia',
            'rust': 'Rust',
            'ark': 'ARK',
            'conan': 'Conan Exiles',
            'valheim': 'Valheim',
            'the forest': 'The Forest',
            'el bosque': 'The Forest',
            'subnautica': 'Subnautica',
            'deep rock galactic': 'Deep Rock Galactic',
            'roca profunda': 'Deep Rock Galactic',
        }
        
        # Diccionario inverso inglés -> español
        self.traducciones_en_es = {v: k for k, v in self.traducciones_es_en.items()}
        
        # Palabras clave en español
        self.palabras_clave_es = {
            'el': 'the',
            'la': 'the',
            'los': 'the',
            'las': 'the',
            'de': 'of',
            'del': 'of the',
            'y': 'and',
            'o': 'or',
            'en': 'in',
            'con': 'with',
            'sin': 'without',
            'para': 'for',
            'por': 'by',
            'entre': 'between',
            'sobre': 'about',
            'bajo': 'under',
            'desde': 'from',
            'hasta': 'to',
        }
        
        # Géneros en español
        self.generos_es_en = {
            'acción': 'action',
            'aventura': 'adventure',
            'rol': 'role-playing',
            'estrategia': 'strategy',
            'simulación': 'simulation',
            'deportes': 'sports',
            'carreras': 'racing',
            'lucha': 'fighting',
            'disparos': 'shooter',
            'plataformas': 'platformer',
            'puzle': 'puzzle',
            'terror': 'horror',
            'supervivencia': 'survival',
            'mundo abierto': 'open world',
            'multijugador': 'multiplayer',
            'cooperativo': 'cooperative',
            'competitivo': 'competitive',
        }
    
    def traducir_es_a_en(self, termino):
        """
        Traduce un término del español al inglés
        
        Args:
            termino: Término en español
            
        Returns:
            list: Lista de posibles traducciones en inglés
        """
        termino_lower = termino.lower().strip()
        traducciones = []
        
        # Búsqueda exacta
        if termino_lower in self.traducciones_es_en:
            traducciones.append(self.traducciones_es_en[termino_lower])
        
        # Búsqueda parcial (si el término contiene una traducción conocida)
        for es, en in self.traducciones_es_en.items():
            if es in termino_lower or termino_lower in es:
                if en not in traducciones:
                    traducciones.append(en)
        
        # Traducir palabras clave
        traduccion_palabras = self._traducir_palabras_clave(termino_lower)
        if traduccion_palabras and traduccion_palabras != termino:
            traducciones.append(traduccion_palabras)
        
        return traducciones
    
    def traducir_en_a_es(self, termino):
        """
        Traduce un término del inglés al español
        
        Args:
            termino: Término en inglés
            
        Returns:
            list: Lista de posibles traducciones en español
        """
        termino_lower = termino.lower().strip()
        traducciones = []
        
        # Búsqueda exacta
        if termino_lower in self.traducciones_en_es:
            traducciones.append(self.traducciones_en_es[termino_lower])
        
        # Búsqueda parcial
        for en, es in self.traducciones_en_es.items():
            if en.lower() in termino_lower or termino_lower in en.lower():
                if es not in traducciones:
                    traducciones.append(es)
        
        return traducciones
    
    def expandir_con_traducciones(self, termino):
        """
        Expande un término con todas sus posibles traducciones
        
        Args:
            termino: Término original (puede estar en español o inglés)
            
        Returns:
            list: Lista con término original + traducciones
        """
        expansiones = [termino]  # Incluir término original
        
        # Intentar traducir de español a inglés
        traducciones_en = self.traducir_es_a_en(termino)
        expansiones.extend(traducciones_en)
        
        # Intentar traducir de inglés a español
        traducciones_es = self.traducir_en_a_es(termino)
        expansiones.extend(traducciones_es)
        
        # Variaciones sin artículos
        expansiones.extend(self._generar_variaciones_sin_articulos(termino))
        
        # Eliminar duplicados preservando orden
        return list(dict.fromkeys(expansiones))
    
    def _traducir_palabras_clave(self, termino):
        """Traduce palabras clave comunes"""
        palabras = termino.split()
        traducidas = []
        
        for palabra in palabras:
            if palabra in self.palabras_clave_es:
                traducidas.append(self.palabras_clave_es[palabra])
            else:
                traducidas.append(palabra)
        
        resultado = ' '.join(traducidas)
        return resultado if resultado != termino else None
    
    def _generar_variaciones_sin_articulos(self, termino):
        """Genera variaciones sin artículos (el, la, the, etc.)"""
        variaciones = []
        termino_lower = termino.lower()
        
        # Remover artículos en español
        for articulo in ['el ', 'la ', 'los ', 'las ']:
            if termino_lower.startswith(articulo):
                variaciones.append(termino[len(articulo):].strip())
        
        # Remover artículos en inglés
        if termino_lower.startswith('the '):
            variaciones.append(termino[4:].strip())
        
        return variaciones
    
    def detectar_idioma(self, termino):
        """
        Detecta si un término está en español o inglés
        
        Returns:
            str: 'es', 'en' o 'unknown'
        """
        termino_lower = termino.lower().strip()
        
        # Verificar si está en diccionario español
        if termino_lower in self.traducciones_es_en:
            return 'es'
        
        # Verificar si está en diccionario inglés
        if termino_lower in self.traducciones_en_es:
            return 'en'
        
        # Buscar palabras clave en español
        palabras = termino_lower.split()
        palabras_es = sum(1 for p in palabras if p in self.palabras_clave_es)
        palabras_en = sum(1 for p in palabras if p in self.palabras_clave_es.values())
        
        if palabras_es > palabras_en:
            return 'es'
        elif palabras_en > palabras_es:
            return 'en'
        
        return 'unknown'
    
    def agregar_traduccion(self, termino_es, termino_en):
        """
        Agrega una nueva traducción al diccionario
        
        Args:
            termino_es: Término en español
            termino_en: Término en inglés
        """
        termino_es = termino_es.lower().strip()
        termino_en = termino_en.strip()
        
        self.traducciones_es_en[termino_es] = termino_en
        self.traducciones_en_es[termino_en] = termino_es
        
        print(f"✓ Traducción agregada: '{termino_es}' <-> '{termino_en}'")
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del diccionario de traducciones"""
        return {
            'total_traducciones': len(self.traducciones_es_en),
            'palabras_clave': len(self.palabras_clave_es),
            'generos': len(self.generos_es_en)
        }


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
