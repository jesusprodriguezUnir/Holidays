"""
Holiday Management System - Streamlit Application
Sistema de gestión de vacaciones para equipos
"""

import streamlit as st
from database import init_db, get_all_teams, get_all_employees
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Holiday Management System",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar base de datos
init_db()

# Título principal
st.title("🏖️ Sistema de Gestión de Vacaciones")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Navegación")
    st.markdown("""
    Usa el menú de páginas arriba para navegar entre:
    
    - 📊 **Dashboard** - Vista general
    - 👥 **Teams** - Gestión de equipos
    - 👤 **Employees** - Gestión de empleados
    - 📅 **Calendar** - Vista de calendario
    - 📤 **Export** - Exportar datos
    """)
    
    st.markdown("---")
    
    # Estadísticas rápidas
    st.subheader("Estadísticas")
    
    try:
        teams = get_all_teams()
        employees = get_all_employees()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Equipos", len(teams))
        with col2:
            st.metric("Empleados", len(employees))
    except Exception as e:
        st.error(f"Error cargando estadísticas: {e}")

# Contenido principal
st.header("Bienvenido al Sistema de Gestión de Vacaciones")

st.markdown("""
### 🎯 Características principales

- **Gestión de Equipos**: Crea y administra múltiples equipos de trabajo
- **Gestión de Empleados**: Añade empleados y asígnalos a equipos
- **Calendario de Vacaciones**: Visualiza y gestiona vacaciones durante todo el año
- **Exportación**: Exporta calendarios a Excel y PDF
- **Multi-equipo**: Gestiona vacaciones de diferentes equipos simultáneamente

### 🚀 Cómo empezar

1. **Crea un equipo** en la página de Teams
2. **Añade empleados** al equipo en la página de Employees
3. **Gestiona vacaciones** en la página de Calendar
4. **Exporta** los datos cuando lo necesites

### 📋 Navegación

Usa el menú lateral izquierdo para navegar entre las diferentes secciones de la aplicación.
""")

# Información adicional
with st.expander("ℹ️ Información del sistema"):
    st.markdown(f"""
    **Versión**: 2.0.0 (Web Edition)
    
    **Base de datos**: SQLite
    
    **Última actualización**: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    
    **Tecnologías**:
    - Streamlit
    - SQLAlchemy
    - openpyxl (Excel)
    - reportlab (PDF)
    """)

# Footer
st.markdown("---")
st.markdown("*Sistema de Gestión de Vacaciones - Desarrollado con Streamlit*")
