"""
Employees - Gestión de empleados
"""

import streamlit as st
from database import (
    create_employee, get_all_employees, get_employee_by_id, update_employee, delete_employee,
    get_all_teams, get_employees_by_team, get_vacations_by_employee
)
import pandas as pd

st.set_page_config(page_title="Employees", page_icon="👤", layout="wide")

st.title("👤 Gestión de Empleados")
st.markdown("Administra los empleados de tu organización")
st.markdown("---")

# Tabs
tab1, tab2 = st.tabs(["📋 Lista de Empleados", "➕ Crear/Editar Empleado"])

with tab1:
    st.subheader("Empleados Existentes")
    
    # Filtro por equipo
    teams = get_all_teams()
    team_options = ["Todos"] + [team.name for team in teams]
    selected_team_filter = st.selectbox("Filtrar por equipo:", team_options)
    
    try:
        employees = get_all_employees()
        
        # Aplicar filtro
        if selected_team_filter != "Todos":
            selected_team = next((t for t in teams if t.name == selected_team_filter), None)
            if selected_team:
                employees = [emp for emp in employees if emp.team_id == selected_team.id]
        
        if employees:
            # Crear tabla de datos
            emp_data = []
            for emp in employees:
                vacations = get_vacations_by_employee(emp.id)
                emp_data.append({
                    "ID": emp.id,
                    "Nombre": emp.name,
                    "Email": emp.email or "-",
                    "Rol": emp.role or "-",
                    "Equipo": emp.team.name if emp.team else "-",
                    "Vacaciones": len(vacations)
                })
            
            df = pd.DataFrame(emp_data)
            
            # Mostrar tabla
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Acciones sobre empleados seleccionados
            st.subheader("Acciones")
            
            col1, col2 = st.columns(2)
            
            with col1:
                employee_names = [emp.name for emp in employees]
                selected_emp_name = st.selectbox("Seleccionar empleado:", employee_names)
                
                if selected_emp_name:
                    selected_emp = next((emp for emp in employees if emp.name == selected_emp_name), None)
                    
                    if selected_emp:
                        st.write(f"**Email:** {selected_emp.email or 'No especificado'}")
                        st.write(f"**Rol:** {selected_emp.role or 'No especificado'}")
                        st.write(f"**Equipo:** {selected_emp.team.name if selected_emp.team else 'Sin equipo'}")
                        
                        vacations = get_vacations_by_employee(selected_emp.id)
                        st.write(f"**Períodos de vacaciones:** {len(vacations)}")
            
            with col2:
                st.write("**Acciones disponibles:**")
                
                if st.button("✏️ Editar Empleado", use_container_width=True):
                    if selected_emp_name:
                        selected_emp = next((emp for emp in employees if emp.name == selected_emp_name), None)
                        if selected_emp:
                            st.session_state['edit_employee_id'] = selected_emp.id
                            st.rerun()
                
                if st.button("🗑️ Eliminar Empleado", use_container_width=True, type="secondary"):
                    if selected_emp_name:
                        selected_emp = next((emp for emp in employees if emp.name == selected_emp_name), None)
                        if selected_emp:
                            vacations = get_vacations_by_employee(selected_emp.id)
                            if vacations:
                                st.warning(f"⚠️ Este empleado tiene {len(vacations)} período(s) de vacaciones que también se eliminarán.")
                            
                            if st.button("⚠️ Confirmar Eliminación", type="primary"):
                                if delete_employee(selected_emp.id):
                                    st.success(f"Empleado '{selected_emp.name}' eliminado correctamente")
                                    st.rerun()
                                else:
                                    st.error("Error al eliminar el empleado")
        else:
            st.info("No hay empleados. Crea tu primer empleado en la pestaña 'Crear/Editar Empleado'.")
    
    except Exception as e:
        st.error(f"Error cargando empleados: {e}")

with tab2:
    # Verificar si estamos editando
    edit_mode = 'edit_employee_id' in st.session_state and st.session_state.get('edit_employee_id')
    
    if edit_mode:
        st.subheader("✏️ Editar Empleado")
        employee = get_employee_by_id(st.session_state['edit_employee_id'])
        
        if employee:
            default_name = employee.name
            default_email = employee.email or ""
            default_role = employee.role or ""
            default_team_id = employee.team_id
        else:
            st.error("Empleado no encontrado")
            if st.button("Cancelar"):
                del st.session_state['edit_employee_id']
                st.rerun()
            st.stop()
    else:
        st.subheader("➕ Crear Nuevo Empleado")
        default_name = ""
        default_email = ""
        default_role = ""
        default_team_id = None
    
    # Verificar que hay equipos
    teams = get_all_teams()
    if not teams:
        st.warning("⚠️ Primero debes crear al menos un equipo en la página de Teams.")
        st.stop()
    
    with st.form("employee_form"):
        name = st.text_input("Nombre *", value=default_name, max_chars=100)
        email = st.text_input("Email", value=default_email, max_chars=100)
        role = st.text_input("Rol", value=default_role, max_chars=50, 
                            placeholder="ej: Developer, Manager, Designer")
        
        # Selector de equipo
        team_names = [team.name for team in teams]
        team_ids = [team.id for team in teams]
        
        if edit_mode and default_team_id:
            default_index = team_ids.index(default_team_id) if default_team_id in team_ids else 0
        else:
            default_index = 0
        
        selected_team_name = st.selectbox("Equipo *", team_names, index=default_index)
        selected_team_id = team_ids[team_names.index(selected_team_name)]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submit = st.form_submit_button("💾 Guardar", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submit:
            if not name.strip():
                st.error("El nombre del empleado es obligatorio")
            elif not selected_team_id:
                st.error("Debes seleccionar un equipo")
            else:
                try:
                    if edit_mode:
                        # Actualizar empleado existente
                        updated_emp = update_employee(
                            st.session_state['edit_employee_id'],
                            name=name.strip(),
                            email=email.strip() if email.strip() else None,
                            role=role.strip() if role.strip() else None,
                            team_id=selected_team_id
                        )
                        if updated_emp:
                            st.success(f"✅ Empleado '{name}' actualizado correctamente")
                            del st.session_state['edit_employee_id']
                            st.rerun()
                        else:
                            st.error("Error al actualizar el empleado")
                    else:
                        # Crear nuevo empleado
                        new_emp = create_employee(
                            name=name.strip(),
                            team_id=selected_team_id,
                            email=email.strip() if email.strip() else None,
                            role=role.strip() if role.strip() else None
                        )
                        st.success(f"✅ Empleado '{name}' creado correctamente")
                        st.rerun()
                
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        st.error(f"Ya existe un empleado con el email '{email}'")
                    else:
                        st.error(f"Error: {e}")
        
        if cancel:
            if edit_mode:
                del st.session_state['edit_employee_id']
            st.rerun()

# Información
with st.expander("ℹ️ Ayuda"):
    st.markdown("""
    ### Gestión de Empleados
    
    **Crear un empleado:**
    1. Ve a la pestaña "Crear/Editar Empleado"
    2. Introduce el nombre (obligatorio)
    3. Opcionalmente añade email y rol
    4. Selecciona el equipo al que pertenece
    5. Haz clic en "Guardar"
    
    **Editar un empleado:**
    1. En la lista, selecciona el empleado
    2. Haz clic en "Editar Empleado"
    3. Modifica los datos
    4. Haz clic en "Guardar"
    
    **Eliminar un empleado:**
    - Al eliminar un empleado, también se eliminarán todas sus vacaciones
    - Esta acción no se puede deshacer
    
    **Filtros:**
    - Puedes filtrar la lista por equipo usando el selector superior
    
    **Nota:** Los emails deben ser únicos si se especifican.
    """)
