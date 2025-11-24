"""
Export - Exportación de datos a Excel y PDF
"""

import streamlit as st
from database import (
    get_all_teams, get_all_employees, get_employees_by_team,
    get_vacations_by_date_range, get_vacations_by_team_and_date
)
from utils.export import export_to_excel, export_to_pdf, generate_date_range
from utils.calendar_utils import (
    get_month_date_range, get_quarter_date_range, get_year_date_range,
    generate_calendar_data
)
from datetime import datetime, date
import calendar

st.set_page_config(page_title="Export", page_icon="📤", layout="wide")

st.title("📤 Exportar Datos")
st.markdown("Exporta calendarios de vacaciones a Excel o PDF")
st.markdown("---")

# Configuración de exportación
st.subheader("⚙️ Configuración de Exportación")

col1, col2 = st.columns(2)

with col1:
    # Filtro de equipo
    teams = get_all_teams()
    team_options = ["Todos los equipos"] + [team.name for team in teams]
    selected_team_filter = st.selectbox("Equipo:", team_options)

with col2:
    # Selector de período
    period_type = st.selectbox("Período:", ["Mes", "Trimestre", "Año", "Personalizado"])

# Año
current_year = datetime.now().year
year = st.number_input("Año:", min_value=2020, max_value=2030, value=current_year)

# Determinar rango de fechas
if period_type == "Mes":
    month = st.selectbox("Mes:", list(range(1, 13)), 
                        format_func=lambda x: calendar.month_name[x],
                        index=datetime.now().month - 1)
    start_date, end_date = get_month_date_range(year, month)
    period_name = f"{calendar.month_name[month]} {year}"

elif period_type == "Trimestre":
    quarter = st.selectbox("Trimestre:", [1, 2, 3, 4], 
                          format_func=lambda x: f"Q{x}")
    start_date, end_date = get_quarter_date_range(year, quarter)
    period_name = f"Q{quarter} {year}"

elif period_type == "Año":
    start_date, end_date = get_year_date_range(year)
    period_name = f"Año {year}"

else:  # Personalizado
    col_a, col_b = st.columns(2)
    with col_a:
        start_date = st.date_input("Fecha inicio:", value=date(year, 1, 1))
    with col_b:
        end_date = st.date_input("Fecha fin:", value=date(year, 12, 31))
    period_name = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

st.markdown("---")

# Vista previa
st.subheader("👁️ Vista Previa")

try:
    # Obtener datos
    if selected_team_filter == "Todos los equipos":
        employees = get_all_employees()
        vacations = get_vacations_by_date_range(start_date, end_date)
        export_title = f"Calendario de Vacaciones - {period_name}"
    else:
        selected_team = next((t for t in teams if t.name == selected_team_filter), None)
        if selected_team:
            employees = get_employees_by_team(selected_team.id)
            vacations = get_vacations_by_team_and_date(selected_team.id, start_date, end_date)
            export_title = f"Calendario de Vacaciones - {selected_team.name} - {period_name}"
        else:
            employees = []
            vacations = []
            export_title = f"Calendario de Vacaciones - {period_name}"
    
    if employees:
        # Generar datos del calendario
        calendar_data = generate_calendar_data(employees, vacations, start_date, end_date)
        
        # Mostrar resumen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Empleados", len(calendar_data))
        with col2:
            total_days = sum([item['total_days'] for item in calendar_data])
            st.metric("Total Días", total_days)
        with col3:
            dates = generate_date_range(start_date, end_date)
            st.metric("Días en Período", len(dates))
        with col4:
            avg_days = round(total_days / len(calendar_data), 1) if calendar_data else 0
            st.metric("Promedio/Empleado", avg_days)
        
        st.markdown("---")
        
        # Botones de exportación
        st.subheader("📥 Descargar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Excel")
            st.write("Formato editable con colores y totales")
            
            try:
                # Preparar datos para exportación
                export_data = []
                for item in calendar_data:
                    export_data.append({
                        'name': item['name'],
                        'role': item['role'],
                        'team': item['team'],
                        'vacations': item['vacations']
                    })
                
                # Generar Excel
                excel_bytes = export_to_excel(export_data, start_date, end_date)
                
                filename = f"vacaciones_{selected_team_filter.replace(' ', '_')}_{period_name.replace(' ', '_')}.xlsx"
                
                st.download_button(
                    label="⬇️ Descargar Excel",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generando Excel: {e}")
        
        with col2:
            st.markdown("### 📄 PDF")
            st.write("Formato profesional para imprimir")
            
            try:
                # Generar PDF
                pdf_bytes = export_to_pdf(export_data, start_date, end_date, export_title)
                
                filename = f"vacaciones_{selected_team_filter.replace(' ', '_')}_{period_name.replace(' ', '_')}.pdf"
                
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generando PDF: {e}")
        
        st.markdown("---")
        
        # Detalles de lo que se exportará
        with st.expander("📋 Ver Detalles de Exportación"):
            st.write(f"**Título:** {export_title}")
            st.write(f"**Período:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
            st.write(f"**Equipo:** {selected_team_filter}")
            st.write(f"**Empleados incluidos:** {len(calendar_data)}")
            st.write(f"**Total días de vacaciones:** {total_days}")
            
            st.markdown("#### Empleados:")
            for item in calendar_data:
                st.write(f"- {item['name']} ({item['team']}) - {item['total_days']} días")
    
    else:
        st.info("No hay empleados para exportar con los filtros seleccionados.")

except Exception as e:
    st.error(f"Error preparando exportación: {e}")
    st.exception(e)

# Información
with st.expander("ℹ️ Ayuda sobre Exportación"):
    st.markdown("""
    ### Exportar Datos
    
    **Formatos disponibles:**
    
    **📊 Excel (.xlsx)**
    - Formato editable
    - Colores para vacaciones y fines de semana
    - Totales automáticos
    - Compatible con Microsoft Excel, Google Sheets, LibreOffice
    
    **📄 PDF (.pdf)**
    - Formato profesional
    - Listo para imprimir
    - No editable
    - Compatible con cualquier visor de PDF
    
    **Configuración:**
    1. Selecciona el equipo (o todos)
    2. Elige el período (mes, trimestre, año o personalizado)
    3. Revisa la vista previa
    4. Haz clic en el botón de descarga correspondiente
    
    **Contenido exportado:**
    - Nombres de empleados
    - Roles y equipos
    - Fechas de vacaciones marcadas
    - Totales por empleado
    - Leyenda explicativa (solo PDF)
    
    **Nota:** Los archivos se generan al momento y se descargan directamente a tu navegador.
    """)
