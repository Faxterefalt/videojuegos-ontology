// Detectar automáticamente el puerto desde la URL actual
const API_BASE = window.location.origin;

// Variable para el temporizador de debounce
let searchTimeout = null;

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
    
    try {
        const response = await fetch(`${API_BASE}/api/poblar`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({limite: parseInt(limite)})
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarAlerta(data.message, 'success');
        } else {
            mostrarAlerta('Error: ' + data.error, 'danger');
        }
    } catch (error) {
        mostrarAlerta('Error de conexión: ' + error, 'danger');
    } finally {
        toggleLoading(false);
    }
}

// Búsqueda general
async function buscarGeneral() {
    const termino = document.getElementById('buscarGeneral').value.trim();
    
    // Si el campo está vacío, limpiar resultados
    if (!termino) {
        document.getElementById('resultados').innerHTML = '';
        return;
    }
    
    // Mínimo 2 caracteres para buscar
    if (termino.length < 2) {
        document.getElementById('resultados').innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i> Ingresa al menos 2 caracteres para buscar
            </div>
        `;
        return;
    }
    
    toggleLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/buscar/general?q=${encodeURIComponent(termino)}`);
        const data = await response.json();
        toggleLoading(false);
        
        if (data.success) {
            mostrarResultados(data);
        } else {
            mostrarAlerta('Error en la búsqueda: ' + (data.error || 'Error desconocido'), 'danger');
        }
    } catch (error) {
        toggleLoading(false);
        mostrarAlerta('Error de conexión: ' + error, 'danger');
    }
}

// Función para búsqueda en tiempo real con debounce
function buscarGeneralTiempoReal() {
    // Cancelar búsqueda anterior si existe
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // Esperar 500ms después de que el usuario deje de escribir
    searchTimeout = setTimeout(() => {
        buscarGeneral();
    }, 500);
}

// Buscar por título
async function buscarPorTitulo() {
    const termino = document.getElementById('buscarTitulo').value;
    if (!termino) return mostrarAlerta('Ingresa un término de búsqueda', 'warning');
    
    toggleLoading(true);
    const response = await fetch(`${API_BASE}/api/buscar/titulo?q=${encodeURIComponent(termino)}`);
    const data = await response.json();
    toggleLoading(false);
    
    mostrarResultados(data);
}

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
    const response = await fetch(`${API_BASE}/api/buscar/desarrollador?q=${encodeURIComponent(termino)}`);
    const data = await response.json();
    toggleLoading(false);
    
    mostrarResultados(data);
}

// Listar todos
async function listarTodos() {
    toggleLoading(true);
    const response = await fetch('/api/listar');
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
                <i class="bi bi-info-circle"></i> No se encontraron resultados
            </div>
        `;
        return;
    }
    
    let html = `<h5 class="mb-3"><i class="bi bi-trophy"></i> ${data.count} resultado(s) encontrado(s)</h5>`;
    html += '<div class="row">';
    
    data.data.forEach(item => {
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
        
        html += `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">${item.titulo}</h5>
                        ${aniosHTML}
                        ${item.desarrollador ? `<p class="mb-2"><i class="bi bi-building"></i> ${item.desarrollador}</p>` : ''}
                        ${generosHTML}
                    </div>
                    <div class="card-footer bg-transparent">
                        <small class="text-muted">
                            <a href="${item.uri}" target="_blank" class="text-decoration-none">
                                <i class="bi bi-box-arrow-up-right"></i> Ver en DBpedia
                            </a>
                        </small>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Cargar estadísticas cuando se abre el modal
document.getElementById('statsModal').addEventListener('show.bs.modal', async function() {
    const content = document.getElementById('statsContent');
    content.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
    
    try {
        const response = await fetch('/api/estadisticas');
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

// Agregar event listener para Enter en el campo de búsqueda general
document.addEventListener('DOMContentLoaded', function() {
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
