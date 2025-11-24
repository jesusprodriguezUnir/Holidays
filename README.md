# Holiday Management System - Web Edition

Sistema completo de gestión de vacaciones para equipos con interfaz web.

## 🚀 Inicio Rápido

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar Aplicación

```bash
# Iniciar aplicación Streamlit
python -m streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov

# Ejecutar tests específicos
pytest tests/test_models.py
pytest tests/test_utils.py
pytest tests/test_integration.py
```

## 📋 Características

### ✅ Gestión Completa
- **Múltiples Equipos**: Crea y gestiona diferentes equipos de trabajo
- **Empleados**: Añade empleados y asígnalos a equipos
- **Vacaciones**: Gestiona vacaciones durante todo el año
- **Tipos de Ausencia**: Vacaciones, enfermedad, asuntos personales, otros

### 📊 Visualización
- **Dashboard**: Vista general con métricas y estadísticas
- **Calendario**: Visualiza vacaciones por mes, trimestre o año
- **Filtros**: Filtra por equipo y período
- **Resúmenes**: Totales y promedios automáticos

### 📤 Exportación
- **Excel**: Formato editable con colores y totales
- **PDF**: Formato profesional listo para imprimir

### 🔍 Detección de Conflictos
- Detecta automáticamente solapamientos de fechas
- Previene conflictos de vacaciones

### 💾 Persistencia
- Base de datos SQLite
- Datos guardados automáticamente

## 📁 Estructura del Proyecto

```
Holidays/
├── app.py                      # Aplicación principal Streamlit
├── models.py                   # Modelos de base de datos
├── database.py                 # Operaciones CRUD
├── requirements.txt            # Dependencias
├── pytest.ini                  # Configuración de tests
├── pages/                      # Páginas de Streamlit
│   ├── 1_📊_Dashboard.py
│   ├── 2_👥_Teams.py
│   ├── 3_👤_Employees.py
│   ├── 4_📅_Calendar.py
│   └── 5_📤_Export.py
├── utils/                      # Utilidades
│   ├── export.py              # Exportación Excel/PDF
│   └── calendar_utils.py      # Utilidades de calendario
└── tests/                      # Tests
    ├── conftest.py            # Fixtures de pytest
    ├── test_models.py         # Tests de modelos
    ├── test_utils.py          # Tests de utilidades
    └── test_integration.py    # Tests de integración
```

## 🛠️ Tecnologías

- **Streamlit**: Framework web en Python
- **SQLAlchemy**: ORM para base de datos
- **SQLite**: Base de datos
- **openpyxl**: Exportación a Excel
- **reportlab**: Generación de PDF
- **pandas**: Manipulación de datos
- **pytest**: Framework de testing

## 📖 Uso

### 1. Crear un Equipo
1. Ve a la página **Teams**
2. Introduce el nombre y descripción
3. Haz clic en "Guardar"

### 2. Añadir Empleados
1. Ve a la página **Employees**
2. Introduce los datos del empleado
3. Selecciona el equipo
4. Haz clic en "Guardar"

### 3. Gestionar Vacaciones
1. Ve a la página **Calendar**
2. Selecciona "Gestionar Vacaciones"
3. Elige el empleado y las fechas
4. Haz clic en "Guardar"

### 4. Exportar Datos
1. Ve a la página **Export**
2. Selecciona equipo y período
3. Descarga en Excel o PDF

## 🧪 Testing

El proyecto incluye tests completos:

- **Tests de Modelos**: Verifican la integridad de los modelos de base de datos
- **Tests de Utilidades**: Prueban funciones de calendario y exportación
- **Tests de Integración**: Validan flujos de trabajo completos

### Cobertura de Tests

Los tests cubren:
- ✅ Creación, lectura, actualización y eliminación (CRUD)
- ✅ Relaciones entre modelos
- ✅ Validaciones y constraints
- ✅ Detección de conflictos
- ✅ Cálculo de días de vacaciones
- ✅ Generación de rangos de fechas
- ✅ Exportación a Excel y PDF

## 🔄 Migración desde Versión Desktop

Si tienes datos de la versión anterior (Tkinter), los datos en `holiday_data.json` pueden ser migrados manualmente:

1. Crea los equipos en la nueva aplicación
2. Añade los empleados
3. Añade las vacaciones correspondientes

## 📝 Notas

- Los nombres de equipos deben ser únicos
- Los emails de empleados deben ser únicos (si se especifican)
- El sistema detecta automáticamente conflictos de fechas
- Los fines de semana se marcan automáticamente en las exportaciones
- Al eliminar un equipo, se eliminan sus empleados y sus vacaciones

## 🆘 Solución de Problemas

### La aplicación no inicia
```bash
# Verifica que las dependencias estén instaladas
pip install -r requirements.txt

# Verifica la versión de Python (requiere 3.8+)
python --version
```

### Error de base de datos
```bash
# Elimina la base de datos y reinicia
rm holidays.db
python -m streamlit run app.py
```

### Tests fallan
```bash
# Instala dependencias de desarrollo
pip install pytest pytest-cov

# Ejecuta tests con más detalle
pytest -vv
```

## 📄 Licencia

Este proyecto es de uso interno.

## 👥 Autor

Desarrollado para la gestión de vacaciones del equipo.
