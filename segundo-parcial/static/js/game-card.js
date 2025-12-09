class GameCard {
    constructor(data, source = 'local') {
        this.data = data;
        this.source = source;
        this.necesitaTraduccion = data.necesita_traduccion || false;
        this.idiomaContenido = data.idioma_contenido || 'en';
        this.idiomaBusqueda = data.idioma_busqueda || 'en';
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
        if (this.source !== 'local' && this.necesitaTraduccion) {
            out += ' <span class="badge bg-info mb-2"><i class="bi bi-translate"></i> Traducido</span>';
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
        const urlOriginal = this.data.uri || this.data.game;
        const { enlace, texto } = this._dbpediaLink(urlOriginal);
        return `
        <div class="card-footer bg-transparent">
            <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">
                    <a href="${enlace}" target="_blank" class="text-decoration-none">
                        <i class="bi bi-box-arrow-up-right"></i> ${texto}
                    </a>
                </small>
                ${this._originalLink(urlOriginal)}
            </div>
        </div>`;
    }
    _dbpediaLink(urlOriginal) {
        if (this.necesitaTraduccion && this.source === 'dbpedia') {
            return {
                enlace: `https://translate.google.com/translate?sl=${this.idiomaContenido}&tl=${this.idiomaBusqueda}&u=${encodeURIComponent(urlOriginal)}`,
                texto: `Ver en DBpedia (traducido a ${obtenerNombreIdioma(this.idiomaBusqueda)})`
            };
        }
        return { enlace: urlOriginal, texto: 'Ver en DBpedia' };
    }
    _originalLink(urlOriginal) {
        if (!this.necesitaTraduccion) return '';
        return `<small>
            <a href="${urlOriginal}" target="_blank" class="text-muted text-decoration-none"
               title="Ver original en ${obtenerNombreIdioma(this.idiomaContenido)}">
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
window.GameCard = GameCard;
window.GameCardFactory = GameCardFactory;
