// Detectar automáticamente el puerto desde la URL actual
const API_BASE = window.location.origin;

// Variable para el temporizador de debounce
let searchTimeout = null;

// Verificar conexión al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    verificarConexion();
    
    // Configurar event listeners
    const inputGeneral = document.getElementById('buscarGeneral');
    if (inputGeneral) {
        // Búsqueda en tiempo real mientras se escribe
        inputGeneral.addEventListener('input', function(e) {
            buscarGeneralTiempoReal();
        });
        
        // También mantener funcionalidad de Enter
        inputGeneral.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                // Cancelar debounce y buscar inmediatamente
                if (searchTimeout) {
                    clearTimeout(searchTimeout);
                }
                buscarGeneral();
            }
        });
    }
    
    // También para los otros campos de búsqueda
    const inputs = {
        'buscarTitulo': buscarPorTitulo,
        'buscarAnio': buscarPorAnio,
        'buscarDev': buscarPorDesarrollador
    };
    
    Object.keys(inputs).forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    inputs[id]();
                }
            });
        }
    });
});

// Verificar conexión con DBpedia
async function verificarConexion() {
    const statusBadge = document.getElementById('dbpedia-status');
    const connectionInfo = document.getElementById('connection-info');
    const localCount = document.getElementById('local-count');
    
    try {
        const response = await fetch(`${API_BASE}/api/verificar-dbpedia`);
        const data = await response.json();
        
        if (data.success) {
            if (data.dbpedia_disponible) {
                statusBadge.className = 'badge bg-success me-2';
                statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> DBpedia Online';
                connectionInfo.textContent = 'DBpedia disponible - Puedes poblar con datos en línea';
            } else {
                statusBadge.className = 'badge bg-warning me-2';
                statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> DBpedia Offline';
                connectionInfo.textContent = 'DBpedia no disponible - Usando datos locales y ejemplos';
            }
            
            localCount.textContent = `${data.videojuegos_locales} locales`;
        } else {
            statusBadge.className = 'badge bg-danger me-2';
            statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Error';
            connectionInfo.textContent = 'Error al verificar conexión';
        }
    } catch (error) {
        statusBadge.className = 'badge bg-danger me-2';
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Error';
        connectionInfo.textContent = 'Error de conexión con el servidor';
        console.error('Error:', error);
    }
}


// Función auxiliar para mostrar/ocultar loading
function toggleLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

// Función auxiliar para mostrar alertas
function mostrarAlerta(mensaje, tipo = 'info') {
    const alert = `
        <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById('resultados').innerHTML = alert + document.getElementById('resultados').innerHTML;
}

// Poblar ontología
async function poblarOntologia() {
    const limite = document.getElementById('limite').value || 10;
    toggleLoading(true);
    
    mostrarAlerta('Iniciando población de ontología...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/api/poblar`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({limite: parseInt(limite)})
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarAlerta(data.message, 'success');
            // Actualizar contador
            verificarConexion();
        } else {
            mostrarAlerta('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        mostrarAlerta('Error de conexión: ' + error, 'danger');
    } finally {
        toggleLoading(false);
    }
}

// NUEVO: Controlador de aborto para cancelar búsquedas
let currentSearchController = null;

// Búsqueda general OPTIMIZADA
async function buscarGeneral() {
    const termino = document.getElementById('buscarGeneral').value.trim();
    
    if (!termino) {
        document.getElementById('resultados').innerHTML = '';
        return;
    }
    
    if (termino.length < 2) {
        document.getElementById('resultados').innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i> Ingresa al menos 2 caracteres
            </div>
        `;
        return;
    }
    
    // CANCELAR búsqueda anterior si existe
    if (currentSearchController) {
        currentSearchController.abort();
    }
    
    currentSearchController = new AbortController();
    
    toggleLoading(true);
    
    // MOSTRAR resultados inmediatamente de caché si existen
    const cachedResults = sessionStorage.getItem(`search_${termino}`);
    if (cachedResults) {
        const data = JSON.parse(cachedResults);
        mostrarResultados(data);
        mostrarAlerta('Resultados desde caché (instantáneo)', 'info');
        toggleLoading(false);
        return;
    }
    
    try {
        const startTime = performance.now();
        
        const response = await fetch(
            `${API_BASE}/api/buscar/general?q=${encodeURIComponent(termino)}`,
            { signal: currentSearchController.signal }
        );
        
        const data = await response.json();
        const endTime = performance.now();
        const searchTime = ((endTime - startTime) / 1000).toFixed(2);
        
        toggleLoading(false);
        
        if (data.success) {
            // Guardar en caché
            sessionStorage.setItem(`search_${termino}`, JSON.stringify(data));
            
            mostrarResultados(data);
            console.log(`⚡ Búsqueda completada en ${searchTime}s`);
        } else {
            mostrarAlerta('Error: ' + (data.error || 'Error desconocido'), 'danger');
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Búsqueda cancelada');
        } else {
            toggleLoading(false);
            mostrarAlerta('Error de conexión: ' + error, 'danger');
        }
    }
}

// Búsqueda en tiempo real OPTIMIZADA
function buscarGeneralTiempoReal() {
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // AUMENTADO de 500ms a 800ms para reducir requests
    searchTimeout = setTimeout(() => {
        buscarGeneral();
    }, 800);
}

// Buscar por título OPTIMIZADO
async function buscarPorTitulo() {
    const termino = document.getElementById('buscarTitulo').value;
    if (!termino) return mostrarAlerta('Ingresa un término', 'warning');
    
    // Verificar caché
    const cachedResults = sessionStorage.getItem(`titulo_${termino}`);
    if (cachedResults) {
        mostrarResultados(JSON.parse(cachedResults));
        mostrarAlerta('⚡ Resultados desde caché', 'success');
        return;
    }
    
    toggleLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/buscar/titulo?q=${encodeURIComponent(termino)}&hybrid=true`);
        const data = await response.json();
        
        // Guardar en caché
        if (data.success) {
            sessionStorage.setItem(`titulo_${termino}`, JSON.stringify(data));
        }
        
        toggleLoading(false);
        mostrarResultados(data);
    } catch (error) {
        toggleLoading(false);
        mostrarAlerta('Error: ' + error, 'danger');
    }
}

// NUEVO: Limpiar caché después de 5 minutos
setInterval(() => {
    const now = Date.now();
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && key.startsWith('search_')) {
            // Limpiar cachés antiguos
            try {
                const data = JSON.parse(sessionStorage.getItem(key));
                if (data.timestamp && (now - data.timestamp > 300000)) { // 5 min
                    sessionStorage.removeItem(key);
                }
            } catch (e) {}
        }
    }
}, 60000); // Cada minuto

// Buscar por año
async function buscarPorAnio() {
    const anio = document.getElementById('buscarAnio').value;
    if (!anio) return mostrarAlerta('Ingresa un año', 'warning');
    
    toggleLoading(true);
    const response = await fetch(`${API_BASE}/api/buscar/anio?anio=${anio}`);
    const data = await response.json();
    toggleLoading(false);
    
    mostrarResultados(data);
}

// Buscar por desarrollador
async function buscarPorDesarrollador() {
    const termino = document.getElementById('buscarDev').value;
    if (!termino) return mostrarAlerta('Ingresa un desarrollador', 'warning');
    
    toggleLoading(true);
    const response = await fetch(`${API_BASE}/api/buscar/desarrollador?q=${encodeURIComponent(termino)}&hybrid=true`);
    const data = await response.json();
    toggleLoading(false);
    
    mostrarResultados(data);
}

// Listar todos
async function listarTodos() {
    toggleLoading(true);
    const response = await fetch(`${API_BASE}/api/listar`);
    const data = await response.json();
    toggleLoading(false);
    
    mostrarResultados(data);
}

// Mostrar resultados en formato de cards
function mostrarResultados(data) {
    const container = document.getElementById('resultados');
    
    if (!data.success || data.count === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i> ${data.message || 'No se encontraron resultados'}
            </div>
        `;
        return;
    }
    
    // NUEVO: Verificar si son resultados híbridos
    if (data.source === 'hybrid') {
        mostrarResultadosHibridos(data);
        return;
    }
    
    // Fallback: mostrar resultados normales (legacy)
    mostrarResultadosSimples(data);
}

// NUEVA FUNCIÓN: Mostrar resultados híbridos (local + DBpedia)
function mostrarResultadosHibridos(data) {
    const container = document.getElementById('resultados');
    let html = '';
    
    // Encabezado general
    html += `
        <div class="alert alert-info">
            <i class="bi bi-lightbulb"></i> 
            <strong>Búsqueda Híbrida Completa</strong> - 
            Mostrando resultados de tu ontología local Y de DBpedia
        </div>
    `;
    
    html += `<h5 class="mb-3"><i class="bi bi-trophy"></i> ${data.count} resultado(s) total(es)</h5>`;
    
    // SECCIÓN 1: RESULTADOS LOCALES (arriba)
    if (data.count_local > 0) {
        html += `
            <div class="mb-4">
                <h6 class="text-success">
                    <i class="bi bi-hdd-fill"></i> 
                    Resultados Locales (${data.count_local})
                </h6>
                <hr class="mb-3">
                <div class="row">
        `;
        
        data.local.forEach(item => {
            html += crearCardJuego(item, 'local');
        });
        
        html += '</div></div>';
    }
    
    // SECCIÓN 2: RESULTADOS DE DBPEDIA (abajo)
    if (data.count_dbpedia > 0) {
        html += `
            <div class="mb-4">
                <h6 class="text-warning">
                    <i class="bi bi-cloud-fill"></i> 
                    Resultados de DBpedia (${data.count_dbpedia})
                    <button class="btn btn-sm btn-primary ms-3" onclick="agregarTodosDesdeDBpedia(${JSON.stringify(data.dbpedia).replace(/"/g, '&quot;')})">
                        <i class="bi bi-download"></i> Agregar todos a ontología local
                    </button>
                </h6>
                <hr class="mb-3">
                <div class="row">
        `;
        
        data.dbpedia.forEach(item => {
            html += crearCardJuego(item, 'dbpedia');
        });
        
        html += '</div></div>';
    }
    
    // Si no hay ningún resultado
    if (data.count_local === 0 && data.count_dbpedia === 0) {
        html += `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> 
                No se encontraron resultados ni en local ni en DBpedia
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// NUEVA FUNCIÓN: Crear card de juego con origen
function crearCardJuego(item, source) {
    // Formatear años
    let aniosHTML = '';
    if (item.anios && item.anios.length > 0) {
        if (item.anios.length === 1) {
            aniosHTML = `<p class="text-muted mb-2"><i class="bi bi-calendar"></i> ${item.anios[0]}</p>`;
        } else {
            const aniosFormatted = item.anios.join(', ');
            aniosHTML = `<p class="text-muted mb-2"><i class="bi bi-calendar-range"></i> ${aniosFormatted}</p>`;
        }
    }
    
    // Formatear géneros
    let generosHTML = '';
    if (item.generos && item.generos.length > 0) {
        generosHTML = item.generos.map(g => 
            `<span class="badge bg-primary me-1">${g}</span>`
        ).join('');
    }
    
    // Badge de origen y botón de agregar
    let originBadge = '';
    let cardClass = '';
    let addButton = '';
    
    if (source === 'local') {
        originBadge = '<span class="badge bg-success mb-2"><i class="bi bi-hdd"></i> Local</span>';
        cardClass = 'border-success';
    } else {
        originBadge = '<span class="badge bg-warning text-dark mb-2"><i class="bi bi-cloud"></i> DBpedia</span>';
        cardClass = 'border-warning';
        
        // Botón para agregar individualmente
        const juegoJSON = JSON.stringify(item).replace(/"/g, '&quot;');
        addButton = `
            <button class="btn btn-sm btn-primary w-100 mt-2" onclick='agregarJuegoIndividual(${juegoJSON})'>
                <i class="bi bi-download"></i> Agregar a local
            </button>
        `;
    }
    
    return `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card h-100 shadow-sm ${cardClass}">
                <div class="card-body">
                    ${originBadge}
                    <h5 class="card-title">${item.titulo}</h5>
                    ${aniosHTML}
                    ${item.desarrollador ? `<p class="mb-2"><i class="bi bi-building"></i> ${item.desarrollador}</p>` : ''}
                    ${generosHTML}
                    ${addButton}
                </div>
                <div class="card-footer bg-transparent">
                    <small class="text-muted">
                        <a href="${item.uri || item.game}" target="_blank" class="text-decoration-none">
                            <i class="bi bi-box-arrow-up-right"></i> Ver en DBpedia
                        </a>
                    </small>
                </div>
            </div>
        </div>
    `;
}

// Función legacy para resultados simples (por si acaso)
function mostrarResultadosSimples(data) {
    const container = document.getElementById('resultados');
    
    // Mostrar badge de origen
    let sourceBadge = '';
    if (data.source === 'dbpedia') {
        sourceBadge = `
            <div class="alert alert-warning">
                <i class="bi bi-cloud"></i> 
                <strong>Resultados de DBpedia Online</strong>
                <button class="btn btn-sm btn-primary ms-3" onclick="agregarTodosDesdeDBpedia(${JSON.stringify(data.data).replace(/"/g, '&quot;')})">
                    <i class="bi bi-download"></i> Agregar todos
                </button>
            </div>
        `;
    } else if (data.source === 'local') {
        sourceBadge = `
            <div class="alert alert-success">
                <i class="bi bi-hdd"></i> 
                <strong>Resultados Locales</strong>
            </div>
        `;
    }
    
    let html = sourceBadge;
    html += `<h5 class="mb-3"><i class="bi bi-trophy"></i> ${data.count} resultado(s)</h5>`;
    html += '<div class="row">';
    
    const items = data.data || [];
    items.forEach(item => {
        html += crearCardJuego(item, data.source || 'local');
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Agregar todos los resultados de DBpedia a la ontología local
async function agregarTodosDesdeDBpedia(juegos) {
    // Validar que juegos sea un array
    if (!Array.isArray(juegos) || juegos.length === 0) {
        mostrarAlerta('No hay juegos válidos para agregar', 'warning');
        return;
    }
    
    // Sanitizar datos antes de enviar
    const juegosSanitizados = juegos.map(juego => ({
        game: juego.game || juego.uri || '',
        titulo: juego.titulo || 'Sin título',
        anios: Array.isArray(juego.anios) ? juego.anios : [],
        desarrollador: juego.desarrollador || null,
        generos: Array.isArray(juego.generos) ? juego.generos : []
    })).filter(j => j.game); // Filtrar solo los que tienen URI
    
    if (juegosSanitizados.length === 0) {
        mostrarAlerta('No hay juegos válidos para agregar', 'warning');
        return;
    }
    
    if (!confirm(`¿Deseas agregar ${juegosSanitizados.length} juego(s) a tu ontología local?`)) {
        return;
    }
    
    toggleLoading(true);
    
    try {
        console.log('Enviando juegos:', juegosSanitizados); // Debug
        
        const response = await fetch(`${API_BASE}/api/agregar-desde-dbpedia`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ juegos: juegosSanitizados })
        });
        
        const data = await response.json();
        
        console.log('Respuesta del servidor:', data); // Debug
        
        if (data.success) {
            mostrarAlerta(data.message, 'success');
            verificarConexion(); // Actualizar contador
            
            // Limpiar caché para forzar actualización
            sessionStorage.clear();
            
            // Recargar resultados después de 1 segundo
            setTimeout(() => {
                const terminoBusqueda = document.getElementById('buscarGeneral').value;
                if (terminoBusqueda) {
                    buscarGeneral();
                }
            }, 1000);
        } else {
            mostrarAlerta('Error: ' + (data.error || 'Error desconocido'), 'danger');
            console.error('Error del servidor:', data);
        }
    } catch (error) {
        mostrarAlerta('Error de conexión: ' + error.message, 'danger');
        console.error('Error completo:', error);
    } finally {
        toggleLoading(false);
    }
}

// NUEVA FUNCIÓN: Agregar un solo juego
async function agregarJuegoIndividual(juego) {
    const juegoSanitizado = {
        game: juego.game || juego.uri || '',
        titulo: juego.titulo || 'Sin título',
        anios: Array.isArray(juego.anios) ? juego.anios : [],
        desarrollador: juego.desarrollador || null,
        generos: Array.isArray(juego.generos) ? juego.generos : []
    };
    
    if (!juegoSanitizado.game) {
        mostrarAlerta('Juego inválido', 'warning');
        return;
    }
    
    if (!confirm(`¿Agregar "${juegoSanitizado.titulo}" a tu ontología local?`)) {
        return;
    }
    
    toggleLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/agregar-desde-dbpedia`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ juegos: [juegoSanitizado] })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarAlerta(`✓ "${juegoSanitizado.titulo}" agregado exitosamente`, 'success');
            verificarConexion();
            sessionStorage.clear();
        } else {
            mostrarAlerta('Error: ' + (data.error || 'No se pudo agregar'), 'danger');
        }
    } catch (error) {
        mostrarAlerta('Error: ' + error.message, 'danger');
    } finally {
        toggleLoading(false);
    }
}

// Cargar estadísticas cuando se abre el modal
document.getElementById('statsModal').addEventListener('show.bs.modal', async function() {
    const content = document.getElementById('statsContent');
    content.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/estadisticas`);
        const data = await response.json();
        
        let html = `
            <div class="text-center mb-4">
                <h1 class="display-4">${data.total}</h1>
                <p class="text-muted">Videojuegos en la ontología</p>
            </div>
            <h6>Géneros más populares:</h6>
            <ul class="list-group">
        `;
        
        data.generos_populares.forEach(g => {
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    ${g.nombre}
                    <span class="badge bg-primary rounded-pill">${g.count}</span>
                </li>
            `;
        });
        
        html += '</ul>';
        content.innerHTML = html;
    } catch (error) {
        content.innerHTML = '<div class="alert alert-danger">Error al cargar estadísticas</div>';
    }
});
