"""
Teams - Gestión de equipos
"""

import streamlit as st
from database import (
    create_team, get_all_teams, get_team_by_id, update_team, delete_team,
    get_employees_by_team
)
import pandas as pd

st.set_page_config(page_title="Teams", page_icon="👥", layout="wide")

st.title("👥 Gestión de Equipos")
st.markdown("Crea y administra equipos de trabajo")
st.markdown("---")

# Tabs para organizar
tab1, tab2 = st.tabs(["📋 Lista de Equipos", "➕ Crear/Editar Equipo"])

with tab1:
    st.subheader("Equipos Existentes")
    
    try:
        teams = get_all_teams()
        
        if teams:
            # Mostrar equipos en cards
            for team in teams:
                with st.expander(f"**{team.name}**", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Descripción:** {team.description or 'Sin descripción'}")
                        st.write(f"**Creado:** {team.created_at.strftime('%d/%m/%Y %H:%M')}")
                        
                        # Mostrar empleados del equipo
                        employees = get_employees_by_team(team.id)
                        st.write(f"**Empleados:** {len(employees)}")
                        
                        if employees:
                            emp_names = ", ".join([emp.name for emp in employees])
                            st.info(f"👤 {emp_names}")
                    
                    with col2:
                        # Botones de acción
                        if st.button("✏️ Editar", key=f"edit_{team.id}"):
                            st.session_state['edit_team_id'] = team.id
                            st.session_state['active_tab'] = 1
                            st.rerun()
                        
                        if st.button("🗑️ Eliminar", key=f"delete_{team.id}"):
                            if employees:
                                st.error("No puedes eliminar un equipo con empleados. Elimina o reasigna los empleados primero.")
                            else:
                                if delete_team(team.id):
                                    st.success(f"Equipo '{team.name}' eliminado correctamente")
                                    st.rerun()
                                else:
                                    st.error("Error al eliminar el equipo")
        else:
            st.info("No hay equipos creados. Crea tu primer equipo en la pestaña 'Crear/Editar Equipo'.")
    
    except Exception as e:
        st.error(f"Error cargando equipos: {e}")

with tab2:
    # Verificar si estamos editando
    edit_mode = 'edit_team_id' in st.session_state and st.session_state.get('edit_team_id')
    
    if edit_mode:
        st.subheader("✏️ Editar Equipo")
        team = get_team_by_id(st.session_state['edit_team_id'])
        
        if team:
            default_name = team.name
            default_desc = team.description or ""
        else:
            st.error("Equipo no encontrado")
            if st.button("Cancelar"):
                del st.session_state['edit_team_id']
                st.rerun()
            st.stop()
    else:
        st.subheader("➕ Crear Nuevo Equipo")
        default_name = ""
        default_desc = ""
    
    with st.form("team_form"):
        name = st.text_input("Nombre del Equipo *", value=default_name, max_chars=100)
        description = st.text_area("Descripción", value=default_desc, height=100)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submit = st.form_submit_button("💾 Guardar", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submit:
            if not name.strip():
                st.error("El nombre del equipo es obligatorio")
            else:
                try:
                    if edit_mode:
                        # Actualizar equipo existente
                        updated_team = update_team(
                            st.session_state['edit_team_id'],
                            name=name.strip(),
                            description=description.strip() if description.strip() else None
                        )
                        if updated_team:
                            st.success(f"✅ Equipo '{name}' actualizado correctamente")
                            del st.session_state['edit_team_id']
                            st.rerun()
                        else:
                            st.error("Error al actualizar el equipo")
                    else:
                        # Crear nuevo equipo
                        new_team = create_team(
                            name=name.strip(),
                            description=description.strip() if description.strip() else None
                        )
                        st.success(f"✅ Equipo '{name}' creado correctamente")
                        st.rerun()
                
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        st.error(f"Ya existe un equipo con el nombre '{name}'")
                    else:
                        st.error(f"Error: {e}")
        
        if cancel:
            if edit_mode:
                del st.session_state['edit_team_id']
            st.rerun()

# Información
with st.expander("ℹ️ Ayuda"):
    st.markdown("""
    ### Gestión de Equipos
    
    **Crear un equipo:**
    1. Ve a la pestaña "Crear/Editar Equipo"
    2. Introduce el nombre del equipo (obligatorio)
    3. Opcionalmente añade una descripción
    4. Haz clic en "Guardar"
    
    **Editar un equipo:**
    1. En la lista de equipos, haz clic en "Editar"
    2. Modifica los datos
    3. Haz clic en "Guardar"
    
    **Eliminar un equipo:**
    - Solo puedes eliminar equipos sin empleados
    - Primero debes eliminar o reasignar los empleados del equipo
    
    **Nota:** Los nombres de equipos deben ser únicos.
    """)
