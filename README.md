# Buscador Semántico de Videojuegos

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Una aplicación web semántica que permite buscar y explorar videojuegos usando ontologías OWL y datos de DBpedia**

[Características](#-características) •
[Instalación](#-instalación) •
[Uso](#-uso) •
[Tecnologías](#-tecnologías)

</div>

---

## Características

**Primera Entrega**
- Búsqueda por título, año de lanzamiento y desarrollador
- Consultas SPARQL sobre ontología OWL
- Integración con DBpedia para datos externos
- Ontología OWL personalizada
- Vocabulario RDF/RDFS
- Inferencias semánticas
- Compatibilidad con estándares W3C

**Segunda Entrega**
- Diseño responsive con Bootstrap 5
- Visualización en tarjetas interactivas
- Estadísticas en tiempo real
- Conexión a dbpedia

 **Tercera Entrega*
- Multilingualidad (sepa la bola)

---

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Navegador web moderno (Chrome, Firefox, Edge)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/videojuegos-ontology.git
cd videojuegos-ontology
```

### Paso 2: Crear Entorno Virtual (Recomendado)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r segundo-parcial/requirements.txt
```

**Dependencias principales:**
- `Flask==3.0.0` - Framework web
- `rdflib==7.0.0` - Manipulación de ontologías
- `SPARQLWrapper==2.0.0` - Consultas a DBpedia

---

## Uso

### Modo 1: Interfaz Web (Recomendado)

#### 1. Iniciar el Servidor

```bash
cd segundo-parcial
python app.py
```

#### 2. Ver Mensaje de Confirmación

Una vez iniciado el servidor, deberías ver un mensaje como este:

```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

#### 3. Abrir el Navegador

- Abre tu navegador web favorito.
- Ingresa la URL `http://127.0.0.1:5000/` en la barra de direcciones.
- Presiona `Enter`.

¡Listo! Ahora deberías ver la interfaz del buscador semántico de videojuegos.

### Modo 2: Línea de Comandos

Para los usuarios avanzados, también es posible interactuar con la aplicación a través de la línea de comandos usando `curl` o herramientas similares.

---

## Tecnologías

- **Backend:** Flask, rdflib, SPARQLWrapper
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Base de Datos:** SQLite (para desarrollo), PostgreSQL (producción)
- **Ontologías:** OWL, RDF/RDFS

---


