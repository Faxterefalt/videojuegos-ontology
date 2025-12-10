class GameCard {
    constructor(data, source = 'local') {
        this.data = data;
        this.source = source;
        
        // ⭐ GARANTIZAR CAMPOS DE TRADUCCIÓN
        this.idiomaUsuario = data.idioma_usuario || window.idiomaBusquedaGlobal || 'en';
        this.idiomaContenido = data.idioma_contenido || 'en';
        
        // ⭐ LÓGICA SIMPLIFICADA: Si tiene URI de DBpedia Y idioma no es inglés → traducir
        const uri = data.uri || data.game || '';
        const tieneDBpediaURI = uri.includes('dbpedia.org');
        
        this.necesitaTraduccion = (tieneDBpediaURI && this.idiomaUsuario !== 'en' && this.idiomaUsuario !== '');
        
        // ⭐ DEBUG para casos críticos
        const tituloLower = (data.titulo || '').toLowerCase();
        const esCritico = tituloLower.includes('last of us') || 
                         tituloLower.includes('god of war') ||
                         tituloLower.includes('último') ||
                         tituloLower.includes('dios') ||
                         tituloLower.includes('ラスト');
        
        if (esCritico) {
            console.log(`🎮 [CRÍTICO] "${data.titulo}"`);
            console.log(`   Source: ${source}`);
            console.log(`   URI: ${uri.substring(0, 60)}...`);
            console.log(`   Tiene DBpedia: ${tieneDBpediaURI}`);
            console.log(`   Idioma usuario: ${this.idiomaUsuario}`);
            console.log(`   ✓ NECESITA TRADUCCIÓN: ${this.necesitaTraduccion}`);
        }
    }
    
    render() {
        return `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card game-card h-100 shadow-sm ${this._cardClass()}">
                <div class="card-body">
                    ${this._badges()}
                    <h5 class="card-title">${this.data.titulo}</h5>
                    ${this._years()}
                    ${this._developer()}
                    ${this._genres()}
                    ${this._actionButton()}
                </div>
                ${this._footer()}
            </div>
        </div>`;
    }
    _badges() {
        let out = this.source === 'local'
            ? '<span class="badge bg-success mb-2"><i class="bi bi-hdd"></i> Local</span>'
            : '<span class="badge bg-warning text-dark mb-2"><i class="bi bi-cloud"></i> DBpedia</span>';
        
        // ⭐ Badge de traducción PARA AMBOS (local y DBpedia)
        if (this.necesitaTraduccion) {
            const nombreIdioma = obtenerNombreIdioma(this.idiomaUsuario);
            out += ` <span class="badge bg-info mb-2" title="Enlace traducido a ${nombreIdioma}">
                <i class="bi bi-translate"></i> ${nombreIdioma}
            </span>`;
        }
        return out;
    }
    _years() {
        return (this.data.anios && this.data.anios.length)
            ? `<p class="text-muted mb-2"><i class="bi bi-calendar"></i> ${this.data.anios.join(', ')}</p>`
            : '';
    }
    _developer() {
        return this.data.desarrollador
            ? `<p class="mb-2"><i class="bi bi-building"></i> ${this.data.desarrollador}</p>`
            : '';
    }
    _genres() {
        if (!this.data.generos || !this.data.generos.length) return '';
        const g = this.data.generos.map(x => `<span class="badge bg-secondary">${x}</span>`).join(' ');
        return `<p class="mb-2">${g}</p>`;
    }
    _actionButton() {
        if (this.source === 'local') return '';
        const juegoJSON = JSON.stringify(this.data).replace(/"/g, '&quot;');
        return `<button class="btn btn-sm btn-primary w-100 mt-2" onclick='agregarJuegoIndividual(${juegoJSON})'>
                    <i class="bi bi-download"></i> Agregar a local
                </button>`;
    }
    _footer() {
        const urlOriginal = this.data.uri || this.data.game || '';
        
        if (!urlOriginal) {
            console.warn('⚠ Juego sin URI:', this.data.titulo);
            return `<div class="card-footer bg-transparent">
                <small class="text-muted">Sin enlace disponible</small>
            </div>`;
        }
        
        const { enlace, texto, icono, esTraducido } = this._dbpediaLink(urlOriginal);
        
        return `
        <div class="card-footer bg-transparent">
            <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">
                    <a href="${enlace}" 
                       target="_blank" 
                       class="text-decoration-none ${esTraducido ? 'fw-bold text-primary' : ''}" 
                       title="${esTraducido ? 'Página traducida con Google Translate' : 'Ver en DBpedia'}">
                        <i class="bi ${icono}"></i> ${texto}
                    </a>
                </small>
                ${this._originalLink(urlOriginal, esTraducido)}
            </div>
        </div>`;
    }
    _dbpediaLink(urlOriginal) {
        // ⭐ VALIDACIÓN
        if (!urlOriginal) {
            console.warn('⚠ URL no disponible para:', this.data.titulo);
            return { 
                enlace: '#', 
                texto: 'Sin enlace',
                icono: 'bi-exclamation-triangle',
                esTraducido: false
            };
        }

        // ⭐ LÓGICA GARANTIZADA
        const debeTraducir = this.necesitaTraduccion || 
                            (this.idiomaUsuario !== 'en' && urlOriginal.includes('dbpedia.org'));
        
        // DEBUG
        const tituloLower = (this.data.titulo || '').toLowerCase();
        if (tituloLower.includes('last of us') || 
            tituloLower.includes('god of war') ||
            tituloLower.includes('último') ||
            tituloLower.includes('dios') ||
            tituloLower.includes('ラスト')) {
            console.log(`🔗 [ENLACE] "${this.data.titulo}"`);
            console.log(`   URL: ${urlOriginal.substring(0, 60)}...`);
            console.log(`   Debe traducir: ${debeTraducir}`);
            console.log(`   Idioma: ${this.idiomaUsuario}`);
        }
        
        if (debeTraducir) {
            // ⭐ URL TRADUCIDA GARANTIZADA
            const urlTraducida = `https://translate.google.com/translate?sl=en&tl=${this.idiomaUsuario}&u=${encodeURIComponent(urlOriginal)}`;
            
            const nombreIdioma = obtenerNombreIdioma(this.idiomaUsuario);
            
            console.log(`   ✅ ENLACE TRADUCIDO: ${urlTraducida.substring(0, 100)}...`);
            
            return {
                enlace: urlTraducida,
                texto: `Ver en ${nombreIdioma}`,
                icono: 'bi-translate',
                esTraducido: true
            };
        }
        
        // Sin traducción
        return { 
            enlace: urlOriginal, 
            texto: 'Ver en DBpedia',
            icono: 'bi-box-arrow-up-right',
            esTraducido: false
        };
    }
    _originalLink(urlOriginal, esTraducido) {
        // Solo mostrar "Ver original" si hay traducción activa
        if (!esTraducido || this.idiomaUsuario === 'en') return '';
        
        return `<small>
            <a href="${urlOriginal}" 
               target="_blank" 
               class="text-muted text-decoration-none"
               title="Ver página original en inglés">
               <i class="bi bi-link-45deg"></i> Original
            </a>
        </small>`;
    }
    _cardClass() { return this.source === 'local' ? 'border-success' : 'border-warning'; }
}
class GameCardFactory {
    static create(data, source = 'local') { return new GameCard(data, source); }
    static renderArray(arr, source) { return arr.map(d => this.create(d, source).render()).join(''); }
}

// ⭐ VARIABLE GLOBAL PARA IDIOMA
window.idiomaBusquedaGlobal = 'en';

window.GameCard = GameCard;
window.GameCardFactory = GameCardFactory;

// Función auxiliar para obtener nombre de idioma
function obtenerNombreIdioma(codigo) {
    const idiomas = {
        'es': 'español',
        'en': 'inglés',
        'fr': 'français',
        'de': 'Deutsch',
        'it': 'italiano',
        'pt': 'português',
        'ja': '日本語',
        'zh': '中文',
        'ko': '한국어',
        'ru': 'русский'
    };
    return idiomas[codigo] || codigo.toUpperCase();
}

window.obtenerNombreIdioma = obtenerNombreIdioma;
