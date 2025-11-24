"""
Calendar - Vista y gestión de calendario de vacaciones
"""

import streamlit as st
from database import (
    get_all_teams, get_all_employees, get_employees_by_team,
    get_vacations_by_date_range, get_vacations_by_team_and_date,
    create_vacation, update_vacation, delete_vacation, get_vacations_by_employee
)
from utils.calendar_utils import (
    get_month_date_range, get_quarter_date_range, get_year_date_range,
    generate_calendar_data, count_vacation_days, get_vacation_conflicts
)
from datetime import datetime, date, timedelta
import pandas as pd
import calendar

st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")

st.title("📅 Calendario de Vacaciones")
st.markdown("Visualiza y gestiona las vacaciones del equipo")
st.markdown("---")

# Tabs
tab1, tab2 = st.tabs(["📊 Cuadrante", "➕ Gestionar Vacaciones"])

with tab1:
    st.subheader("Cuadrante de Vacaciones")
    
    # Filtros
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Filtro de equipo
        teams = get_all_teams()
        team_options = ["Todos los equipos"] + [team.name for team in teams]
        # Default to Alfa if exists
        default_index = 0
        if "Alfa" in team_options:
            default_index = team_options.index("Alfa")
        selected_team_filter = st.selectbox("Equipo:", team_options, index=default_index)
    
    with col2:
        # Selector de período
        period_options = [
            "Navidad 2025 (22 Dic - 7 Ene)",
            "Verano 2025 (15 Jun - 15 Sep)",
            "Año Completo 2025",
            "Mes Actual",
            "Personalizado"
        ]
        period_type = st.selectbox("Período:", period_options)
    
    # Determinar rango de fechas
    today = date.today()
    year = 2025 # Default year as per request
    
    if "Navidad 2025" in period_type:
        start_date = date(2025, 12, 22)
        end_date = date(2026, 1, 7)
    elif "Verano 2025" in period_type:
        start_date = date(2025, 6, 15)
        end_date = date(2025, 9, 15)
    elif "Año Completo 2025" in period_type:
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)
    elif "Mes Actual" in period_type:
        start_date, end_date = get_month_date_range(today.year, today.month)
    else:  # Personalizado
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input("Fecha inicio:", value=date(year, 1, 1))
        with col_b:
            end_date = st.date_input("Fecha fin:", value=date(year, 12, 31))
    
    # Obtener datos
    try:
        if selected_team_filter == "Todos los equipos":
            employees = get_all_employees()
            vacations = get_vacations_by_date_range(start_date, end_date)
        else:
            selected_team = next((t for t in teams if t.name == selected_team_filter), None)
            if selected_team:
                employees = get_employees_by_team(selected_team.id)
                vacations = get_vacations_by_team_and_date(selected_team.id, start_date, end_date)
            else:
                employees = []
                vacations = []
        
        if employees:
            # Generar datos del calendario
            calendar_data = generate_calendar_data(employees, vacations, start_date, end_date)
            
            # --- VISTA CUADRANTE ---
            
            # Generar lista de fechas
            date_range = []
            curr = start_date
            while curr <= end_date:
                date_range.append(curr)
                curr += timedelta(days=1)
            
            # Crear estructura para DataFrame
            # Filas: Empleados
            # Columnas: Info + Fechas
            
            quadrant_data = []
            for item in calendar_data:
                row = {
                    "Nombre": item['name'],
                    "Rol": item['role'],
                    "Total Días": item['total_days']
                }
                
                # Marcar días
                for d in date_range:
                    col_name = d.strftime("%d-%b")
                    if d in item['vacation_dates']:
                        row[col_name] = "X"
                    else:
                        row[col_name] = ""
                
                quadrant_data.append(row)
            
            df_quadrant = pd.DataFrame(quadrant_data)
            
            # Configurar columnas
            column_config = {
                "Nombre": st.column_config.TextColumn("Nombre"),
                "Rol": st.column_config.TextColumn("Rol"),
                "Total Días": st.column_config.NumberColumn("Total")
            }
            
            st.dataframe(
                df_quadrant,
                use_container_width=True,
                hide_index=True,
                column_config=column_config,
                height=500
            )
            
            st.caption("Leyenda: 'X' indica día de vacaciones.")
            
            # --- FIN VISTA CUADRANTE ---
            
        else:
            st.info("No hay empleados en el equipo seleccionado.")
    
    except Exception as e:
        st.error(f"Error cargando calendario: {e}")

with tab2:
    st.subheader("Gestionar Vacaciones")
    
    # Selector de acción
    action = st.radio("Acción:", ["Añadir Vacaciones", "Editar/Eliminar Vacaciones"], horizontal=True)
    
    if action == "Añadir Vacaciones":
        st.markdown("### ➕ Añadir Nuevo Período de Vacaciones")
        
        employees = get_all_employees()
        if not employees:
            st.warning("No hay empleados. Crea empleados primero.")
            st.stop()
        
        with st.form("add_vacation_form"):
            # Selector de empleado
            emp_names = [f"{emp.name} ({emp.team.name if emp.team else 'Sin equipo'})" for emp in employees]
            selected_emp_name = st.selectbox("Empleado:", emp_names)
            selected_emp = employees[emp_names.index(selected_emp_name)]
            
            col1, col2 = st.columns(2)
            with col1:
                start_date_input = st.date_input("Fecha inicio:", value=date.today())
            with col2:
                end_date_input = st.date_input("Fecha fin:", value=date.today())
            
            vacation_type = st.selectbox("Tipo:", ["vacation", "sick", "personal", "other"])
            notes = st.text_area("Notas (opcional):", height=100)
            
            # Mostrar días
            if start_date_input and end_date_input and start_date_input <= end_date_input:
                days = count_vacation_days(start_date_input, end_date_input)
                st.info(f"📊 Total: {days} días")
            
            submit = st.form_submit_button("💾 Guardar Vacaciones", use_container_width=True)
            
            if submit:
                if start_date_input > end_date_input:
                    st.error("La fecha de inicio debe ser anterior o igual a la fecha de fin")
                else:
                    # Verificar conflictos
                    all_vacations = get_vacations_by_employee(selected_emp.id)
                    conflicts = get_vacation_conflicts(selected_emp.id, start_date_input, end_date_input, all_vacations)
                    
                    if conflicts:
                        st.error(f"⚠️ Conflicto detectado: Este empleado ya tiene vacaciones en estas fechas")
                        for conflict in conflicts:
                            st.write(f"  - {conflict.start_date} a {conflict.end_date}")
                    else:
                        try:
                            new_vacation = create_vacation(
                                employee_id=selected_emp.id,
                                start_date=start_date_input,
                                end_date=end_date_input,
                                vacation_type=vacation_type,
                                notes=notes.strip() if notes.strip() else None
                            )
                            st.success(f"✅ Vacaciones añadidas para {selected_emp.name}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
    
    else:  # Editar/Eliminar
        st.markdown("### ✏️ Editar o Eliminar Vacaciones")
        
        employees = get_all_employees()
        if not employees:
            st.warning("No hay empleados.")
            st.stop()
        
        # Selector de empleado
        emp_names = [f"{emp.name} ({emp.team.name if emp.team else 'Sin equipo'})" for emp in employees]
        selected_emp_name = st.selectbox("Seleccionar empleado:", emp_names, key="edit_emp_select")
        selected_emp = employees[emp_names.index(selected_emp_name)]
        
        # Obtener vacaciones del empleado
        vacations = get_vacations_by_employee(selected_emp.id)
        
        if vacations:
            # Mostrar vacaciones
            vac_options = []
            for vac in vacations:
                days = (vac.end_date - vac.start_date).days + 1
                vac_str = f"{vac.start_date.strftime('%d/%m/%Y')} - {vac.end_date.strftime('%d/%m/%Y')} ({days} días) [{vac.vacation_type}]"
                vac_options.append(vac_str)
            
            selected_vac_str = st.selectbox("Seleccionar período:", vac_options)
            selected_vac = vacations[vac_options.index(selected_vac_str)]
            
            # Mostrar detalles
            st.write(f"**Tipo:** {selected_vac.vacation_type}")
            st.write(f"**Notas:** {selected_vac.notes or 'Sin notas'}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ Editar", use_container_width=True):
                    st.session_state['editing_vacation_id'] = selected_vac.id
            
            with col2:
                if st.button("🗑️ Eliminar", use_container_width=True, type="secondary"):
                    if delete_vacation(selected_vac.id):
                        st.success("Vacaciones eliminadas correctamente")
                        st.rerun()
                    else:
                        st.error("Error al eliminar")
            
            # Formulario de edición
            if st.session_state.get('editing_vacation_id') == selected_vac.id:
                st.markdown("---")
                st.markdown("#### Editar Vacaciones")
                
                with st.form("edit_vacation_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_start = st.date_input("Nueva fecha inicio:", value=selected_vac.start_date)
                    with col2:
                        new_end = st.date_input("Nueva fecha fin:", value=selected_vac.end_date)
                    
                    new_type = st.selectbox("Tipo:", ["vacation", "sick", "personal", "other"],
                                          index=["vacation", "sick", "personal", "other"].index(selected_vac.vacation_type))
                    new_notes = st.text_area("Notas:", value=selected_vac.notes or "", height=100)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        save = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
                    with col_b:
                        cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
                    
                    if save:
                        if new_start > new_end:
                            st.error("La fecha de inicio debe ser anterior o igual a la fecha de fin")
                        else:
                            # Verificar conflictos (excluyendo la vacación actual)
                            all_vacations = get_vacations_by_employee(selected_emp.id)
                            conflicts = get_vacation_conflicts(selected_emp.id, new_start, new_end, 
                                                             all_vacations, exclude_vacation_id=selected_vac.id)
                            
                            if conflicts:
                                st.error("⚠️ Conflicto: Estas fechas se solapan con otras vacaciones")
                            else:
                                try:
                                    update_vacation(
                                        selected_vac.id,
                                        start_date=new_start,
                                        end_date=new_end,
                                        vacation_type=new_type,
                                        notes=new_notes.strip() if new_notes.strip() else None
                                    )
                                    st.success("✅ Vacaciones actualizadas")
                                    del st.session_state['editing_vacation_id']
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                    
                    if cancel:
                        del st.session_state['editing_vacation_id']
                        st.rerun()
        else:
            st.info(f"No hay vacaciones registradas para {selected_emp.name}")
