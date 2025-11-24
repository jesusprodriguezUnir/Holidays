"""
Dashboard - Vista general del sistema
"""

import streamlit as st
from database import (
    get_all_teams, get_all_employees, get_all_vacations,
    get_employee_vacation_days
)
from datetime import datetime, date
import pandas as pd

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.markdown("Vista general del sistema de vacaciones")
st.markdown("---")

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

try:
    teams = get_all_teams()
    employees = get_all_employees()
    vacations = get_all_vacations()
    
    with col1:
        st.metric("Total Equipos", len(teams), delta=None)
    
    with col2:
        st.metric("Total Empleados", len(employees), delta=None)
    
    with col3:
        st.metric("Períodos de Vacaciones", len(vacations), delta=None)
    
    with col4:
        # Calcular días totales de vacaciones este año
        current_year = datetime.now().year
        total_days = sum([get_employee_vacation_days(emp.id, current_year) for emp in employees])
        st.metric(f"Días de Vacaciones {current_year}", total_days, delta=None)
    
    st.markdown("---")
    
    # Sección de equipos
    st.subheader("👥 Equipos")
    
    if teams:
        team_data = []
        for team in teams:
            team_employees = [emp for emp in employees if emp.team_id == team.id]
            team_data.append({
                "Equipo": team.name,
                "Descripción": team.description or "-",
                "Empleados": len(team_employees),
                "Creado": team.created_at.strftime("%d/%m/%Y")
            })
        
        df_teams = pd.DataFrame(team_data)
        st.dataframe(df_teams, use_container_width=True, hide_index=True)
    else:
        st.info("No hay equipos creados. Ve a la página de Teams para crear uno.")
    
    st.markdown("---")
    
    # Sección de próximas vacaciones
    st.subheader("📅 Próximas Vacaciones")
    
    if vacations:
        today = date.today()
        upcoming_vacations = [v for v in vacations if v.start_date >= today]
        upcoming_vacations.sort(key=lambda x: x.start_date)
        
        if upcoming_vacations[:10]:  # Mostrar las próximas 10
            vacation_data = []
            for vacation in upcoming_vacations[:10]:
                employee = next((emp for emp in employees if emp.id == vacation.employee_id), None)
                if employee:
                    days = (vacation.end_date - vacation.start_date).days + 1
                    vacation_data.append({
                        "Empleado": employee.name,
                        "Equipo": employee.team.name if employee.team else "-",
                        "Inicio": vacation.start_date.strftime("%d/%m/%Y"),
                        "Fin": vacation.end_date.strftime("%d/%m/%Y"),
                        "Días": days,
                        "Tipo": vacation.vacation_type
                    })
            
            df_vacations = pd.DataFrame(vacation_data)
            st.dataframe(df_vacations, use_container_width=True, hide_index=True)
        else:
            st.info("No hay vacaciones programadas próximamente.")
    else:
        st.info("No hay vacaciones registradas. Ve a la página de Calendar para añadir vacaciones.")
    
    st.markdown("---")
    
    # Estadísticas por equipo
    st.subheader("📈 Estadísticas por Equipo")
    
    if teams and employees:
        stats_data = []
        current_year = datetime.now().year
        
        for team in teams:
            team_employees = [emp for emp in employees if emp.team_id == team.id]
            team_vacations = sum([get_employee_vacation_days(emp.id, current_year) for emp in team_employees])
            
            stats_data.append({
                "Equipo": team.name,
                "Empleados": len(team_employees),
                f"Días de Vacaciones {current_year}": team_vacations,
                "Promedio por Empleado": round(team_vacations / len(team_employees), 1) if team_employees else 0
            })
        
        df_stats = pd.DataFrame(stats_data)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)
        
        # Gráfico de barras
        if stats_data:
            st.bar_chart(df_stats.set_index("Equipo")["Empleados"])
    else:
        st.info("Crea equipos y empleados para ver estadísticas.")

except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.exception(e)

# Información adicional
with st.expander("ℹ️ Acerca del Dashboard"):
    st.markdown("""
    El dashboard proporciona una vista general rápida de:
    
    - **Métricas principales**: Número de equipos, empleados y vacaciones
    - **Equipos**: Lista de todos los equipos con su información
    - **Próximas vacaciones**: Las 10 próximas vacaciones programadas
    - **Estadísticas**: Análisis de vacaciones por equipo
    
    Los datos se actualizan automáticamente al recargar la página.
    """)
