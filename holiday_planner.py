"""
Holiday Planner Application
Gestión de vacaciones del equipo usando SQLite
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta, date
import json
import os
from typing import List, Dict, Set
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# Import database functions
from database import (
    get_session, get_employees_by_team, 
    create_employee, update_employee, delete_employee,
    get_vacations_by_employee
)
from models import Team, Employee, Vacation

class TeamMember:
    """Representa un miembro del equipo con sus días de vacaciones"""
    
    def __init__(self, id: int, name: str, role: str = "", vacation_days: Set[str] = None):
        self.id = id
        self.name = name
        self.role = role
        self.vacation_days = vacation_days if vacation_days else set()
    
    def add_vacation_day(self, date_str: str):
        """Añade un día de vacaciones"""
        self.vacation_days.add(date_str)
    
    def remove_vacation_day(self, date_str: str):
        """Elimina un día de vacaciones"""
        self.vacation_days.discard(date_str)
    
    def is_on_vacation(self, date_str: str) -> bool:
        """Verifica si está de vacaciones en una fecha"""
        return date_str in self.vacation_days


class HolidayPlanner:
    """Gestor principal del planificador de vacaciones conectado a BD"""
    
    def __init__(self, team_name: str = "Alfa"):
        self.team_name = team_name
        self.team_id = None
        self.team_members: List[TeamMember] = []
        
        # Default period (Navidad 2025)
        self.start_date = datetime(2025, 12, 22)
        self.end_date = datetime(2026, 1, 7)
        self.dates = []
        self.update_dates()
        
        self.init_db_connection()
        self.load_data()

    def init_db_connection(self):
        session = get_session()
        try:
            team = session.query(Team).filter_by(name=self.team_name).first()
            if team:
                self.team_id = team.id
            else:
                # Create team if not exists (though populate_db should have done it)
                print(f"Team {self.team_name} not found. Please run populate_db.py first.")
        finally:
            session.close()

    def set_period(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
        self.update_dates()

    def update_dates(self):
        self.dates = []
        current = self.start_date
        while current <= self.end_date:
            self.dates.append(current)
            current += timedelta(days=1)

    def load_data(self):
        """Carga los datos desde la base de datos"""
        if not self.team_id:
            return False
        
        self.team_members = []
        employees = get_employees_by_team(self.team_id)
        
        for emp in employees:
            vacations = get_vacations_by_employee(emp.id)
            vacation_days = set()
            for vac in vacations:
                # Expand vacation range to days
                curr = vac.start_date
                # Ensure we handle date objects correctly
                if isinstance(curr, date) and not isinstance(curr, datetime):
                    curr = datetime.combine(curr, datetime.min.time())
                
                end = vac.end_date
                if isinstance(end, date) and not isinstance(end, datetime):
                    end = datetime.combine(end, datetime.min.time())

                while curr <= end:
                    vacation_days.add(curr.strftime("%Y-%m-%d"))
                    curr += timedelta(days=1)
            
            self.team_members.append(TeamMember(emp.id, emp.name, emp.role, vacation_days))
        return True
    
    def add_member(self, name: str, role: str) -> bool:
        """Añade un miembro al equipo en la BD"""
        if not self.team_id:
            return False
        try:
            emp = create_employee(name, self.team_id, role=role)
            self.team_members.append(TeamMember(emp.id, emp.name, emp.role))
            return True
        except Exception as e:
            print(f"Error adding member: {e}")
            return False
    
    def remove_member(self, member_id: int) -> bool:
        """Elimina un miembro del equipo de la BD"""
        try:
            if delete_employee(member_id):
                self.team_members = [m for m in self.team_members if m.id != member_id]
                return True
            return False
        except Exception as e:
            print(f"Error removing member: {e}")
            return False
            
    def update_member(self, member: TeamMember) -> bool:
        """Actualiza la información de un miembro en la BD"""
        try:
            update_employee(member.id, name=member.name, role=member.role)
            return True
        except Exception as e:
            print(f"Error updating member: {e}")
            return False
    
    def get_member(self, name: str) -> TeamMember:
        """Obtiene un miembro por nombre"""
        for member in self.team_members:
            if member.name == name:
                return member
        return None
    
    def is_weekend(self, date_obj: datetime) -> bool:
        """Verifica si una fecha es fin de semana"""
        return date_obj.weekday() >= 5  # 5=Sábado, 6=Domingo
    
    def save_data(self):
        """Guarda los cambios de vacaciones en la BD"""
        session = get_session()
        try:
            for member in self.team_members:
                # 1. Delete ALL vacations for the employee to avoid fragmentation issues
                session.query(Vacation).filter(Vacation.employee_id == member.id).delete()
                
                # 2. Reconstruct vacations from the set
                sorted_days = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in member.vacation_days])
                
                if not sorted_days:
                    continue
                
                # Group into ranges
                ranges = []
                start = sorted_days[0]
                prev = sorted_days[0]
                
                for d in sorted_days[1:]:
                    if (d - prev).days > 1:
                        ranges.append((start, prev))
                        start = d
                    prev = d
                ranges.append((start, prev))
                
                # Create new vacations
                for start_date, end_date in ranges:
                    vac = Vacation(
                        employee_id=member.id,
                        start_date=start_date,
                        end_date=end_date,
                        vacation_type='vacation'
                    )
                    session.add(vac)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving data: {e}")
            return False
        finally:
            session.close()
    
    def export_to_excel(self, filename: str):
        """Exporta el calendario a Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Vacaciones"
        
        # Estilos
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        weekend_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
        vacation_fill = PatternFill(start_color="92D050", end_color="92D050", fill_type="solid")
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        center_align = Alignment(horizontal='center', vertical='center')
        
        # Headers
        ws['A1'] = "Nombre"
        ws['B1'] = "Rol"
        
        # Fechas como headers
        for col_idx, date_obj in enumerate(self.dates, start=3):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = date_obj.strftime("%d-%b")
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = border
            ws.column_dimensions[cell.column_letter].width = 10
        
        # Aplicar estilo a headers de nombre y rol
        for cell_name in ['A1', 'B1']:
            ws[cell_name].fill = header_fill
            ws[cell_name].font = header_font
            ws[cell_name].alignment = center_align
            ws[cell_name].border = border
        
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        
        # Datos de miembros
        for row_idx, member in enumerate(self.team_members, start=2):
            ws.cell(row=row_idx, column=1, value=member.name).border = border
            ws.cell(row=row_idx, column=2, value=member.role).border = border
            
            for col_idx, date_obj in enumerate(self.dates, start=3):
                cell = ws.cell(row=row_idx, column=col_idx)
                date_str = date_obj.strftime("%Y-%m-%d")
                
                if member.is_on_vacation(date_str):
                    cell.value = "X"
                    cell.fill = vacation_fill
                    cell.alignment = center_align
                elif self.is_weekend(date_obj):
                    cell.fill = weekend_fill
                
                cell.border = border
        
        wb.save(filename)
    
    def export_to_pdf(self, filename: str):
        """Exporta el calendario a PDF"""
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#4472C4'), spaceAfter=30, alignment=1)
        title = Paragraph("Cuadrante de Vacaciones", title_style)
        elements.append(title)
        
        subtitle = Paragraph(f"Período: {self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')}", styles['Normal'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.5*cm))
        
        table_data = []
        headers = ["Nombre", "Rol"] + [d.strftime("%d-%b") for d in self.dates] + ["Total"]
        table_data.append(headers)
        
        for member in self.team_members:
            row = [member.name, member.role]
            count = 0
            for d in self.dates:
                date_str = d.strftime("%Y-%m-%d")
                if member.is_on_vacation(date_str):
                    row.append("X")
                    count += 1
                else:
                    row.append("")
            row.append(str(count))
            table_data.append(row)
        
        table = Table(table_data)
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        
        # Resaltar fines de semana y vacaciones (simplificado)
        for col_idx, d in enumerate(self.dates, start=2):
            if self.is_weekend(d):
                table_style.add('BACKGROUND', (col_idx, 1), (col_idx, -1), colors.HexColor('#E7E6E6'))
        
        for row_idx, member in enumerate(self.team_members, start=1):
            for col_idx, d in enumerate(self.dates, start=2):
                if member.is_on_vacation(d.strftime("%Y-%m-%d")):
                    table_style.add('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.HexColor('#92D050'))
        
        table.setStyle(table_style)
        elements.append(table)
        doc.build(elements)


class HolidayPlannerGUI:
    """Interfaz gráfica de la aplicación"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Planificador de Vacaciones - Equipo Alfa")
        self.root.geometry("1200x700")
        
        self.planner = HolidayPlanner("Alfa")
        
        self.selected_member = None
        
        self.create_widgets()
        self.refresh_grid()
    
    def create_widgets(self):
        # Frame superior
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(top_frame, text="Cuadrante de Vacaciones", font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Selector de Periodo
        period_frame = ttk.Frame(top_frame)
        period_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(period_frame, text="Periodo:").pack(side=tk.LEFT)
        
        self.period_var = tk.StringVar(value="Navidad 2025")
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var, state="readonly")
        period_combo['values'] = ("Año Completo 2025", "Verano 2025", "Navidad 2025")
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.on_period_change)
        
        # Botones
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="💾 Guardar", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Exportar Excel", command=self.export_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Exportar PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        
        # Main Frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Grid Frame (Left)
        grid_frame = ttk.Frame(main_frame)
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(grid_frame)
        v_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        self.grid_container = ttk.Frame(canvas)
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas.create_window((0, 0), window=self.grid_container, anchor=tk.NW)
        self.grid_container.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Side Panel (Right)
        self.create_side_panel(main_frame)
        
    def create_side_panel(self, parent):
        side_panel = ttk.LabelFrame(parent, text="Gestión de Equipo", padding="10")
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Label(side_panel, text="Miembro seleccionado:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.selected_label = ttk.Label(side_panel, text="Ninguno", foreground="gray")
        self.selected_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Add Member
        ttk.Label(side_panel, text="Nuevo miembro:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(side_panel, text="Nombre:").pack(anchor=tk.W)
        self.new_name_entry = ttk.Entry(side_panel, width=25)
        self.new_name_entry.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(side_panel, text="Rol:").pack(anchor=tk.W)
        self.new_role_entry = ttk.Entry(side_panel, width=25)
        self.new_role_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(side_panel, text="➕ Añadir Miembro", command=self.add_member).pack(fill=tk.X)
        
        ttk.Separator(side_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Edit Member
        ttk.Label(side_panel, text="Editar miembro:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(side_panel, text="Nombre:").pack(anchor=tk.W)
        self.edit_name_entry = ttk.Entry(side_panel, width=25)
        self.edit_name_entry.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(side_panel, text="Rol:").pack(anchor=tk.W)
        self.edit_role_entry = ttk.Entry(side_panel, width=25)
        self.edit_role_entry.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(side_panel, text="💾 Actualizar Info", command=self.update_member_info).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(side_panel, text="🗑️ Eliminar Miembro", command=self.delete_member).pack(fill=tk.X)

    def on_period_change(self, event):
        period = self.period_var.get()
        if period == "Año Completo 2025":
            start = datetime(2025, 1, 1)
            end = datetime(2025, 12, 31)
        elif period == "Verano 2025":
            start = datetime(2025, 6, 15)
            end = datetime(2025, 9, 15)
        else: # Navidad 2025
            start = datetime(2025, 12, 22)
            end = datetime(2026, 1, 7)
            
        self.planner.set_period(start, end)
        self.refresh_grid()

    def refresh_grid(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()
            
        header_style = {'background': '#4472C4', 'foreground': 'white', 'font': ('Arial', 9, 'bold')}
        
        tk.Label(self.grid_container, text="Nombre", width=15, **header_style).grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        tk.Label(self.grid_container, text="Rol", width=12, **header_style).grid(row=0, column=1, sticky='nsew', padx=1, pady=1)
        
        for col_idx, date_obj in enumerate(self.planner.dates, start=2):
            date_text = date_obj.strftime("%d\n%b")
            bg_color = '#E7E6E6' if self.planner.is_weekend(date_obj) else '#4472C4'
            fg_color = 'black' if self.planner.is_weekend(date_obj) else 'white'
            tk.Label(self.grid_container, text=date_text, width=6, background=bg_color, foreground=fg_color, font=('Arial', 8, 'bold')).grid(row=0, column=col_idx, sticky='nsew', padx=1, pady=1)
            
        for row_idx, member in enumerate(self.planner.team_members, start=1):
            name_label = tk.Label(self.grid_container, text=member.name, width=15, background='white', cursor='hand2', relief=tk.RAISED, borderwidth=1)
            name_label.grid(row=row_idx, column=0, sticky='nsew', padx=1, pady=1)
            name_label.bind('<Button-1>', lambda e, m=member: self.select_member(m))
            
            tk.Label(self.grid_container, text=member.role, width=12, background='white', relief=tk.RAISED, borderwidth=1).grid(row=row_idx, column=1, sticky='nsew', padx=1, pady=1)
            
            for col_idx, date_obj in enumerate(self.planner.dates, start=2):
                date_str = date_obj.strftime("%Y-%m-%d")
                is_vacation = member.is_on_vacation(date_str)
                is_weekend = self.planner.is_weekend(date_obj)
                
                bg_color = '#92D050' if is_vacation else ('#E7E6E6' if is_weekend else 'white')
                text = 'X' if is_vacation else ''
                
                cell = tk.Label(self.grid_container, text=text, width=6, background=bg_color, relief=tk.RAISED, borderwidth=1, cursor='hand2')
                cell.grid(row=row_idx, column=col_idx, sticky='nsew', padx=1, pady=1)
                cell.bind('<Button-1>', lambda e, m=member, d=date_str: self.toggle_vacation(m, d))

    def select_member(self, member):
        self.selected_member = member
        self.selected_label.config(text=member.name, foreground="blue")
        self.edit_name_entry.delete(0, tk.END)
        self.edit_name_entry.insert(0, member.name)
        self.edit_role_entry.delete(0, tk.END)
        self.edit_role_entry.insert(0, member.role)

    def toggle_vacation(self, member, date_str):
        if member.is_on_vacation(date_str):
            member.remove_vacation_day(date_str)
        else:
            member.add_vacation_day(date_str)
        self.refresh_grid()

    def add_member(self):
        name = self.new_name_entry.get().strip()
        role = self.new_role_entry.get().strip()
        if name:
            if self.planner.add_member(name, role):
                self.new_name_entry.delete(0, tk.END)
                self.new_role_entry.delete(0, tk.END)
                self.refresh_grid()
                messagebox.showinfo("Éxito", f"Miembro {name} añadido")
            else:
                messagebox.showerror("Error", "No se pudo añadir el miembro")

    def update_member_info(self):
        if self.selected_member:
            self.selected_member.name = self.edit_name_entry.get().strip()
            self.selected_member.role = self.edit_role_entry.get().strip()
            if self.planner.update_member(self.selected_member):
                self.refresh_grid()
                messagebox.showinfo("Éxito", "Información actualizada")

    def delete_member(self):
        if self.selected_member and messagebox.askyesno("Confirmar", f"¿Eliminar a {self.selected_member.name}?"):
            if self.planner.remove_member(self.selected_member.id):
                self.selected_member = None
                self.refresh_grid()
                messagebox.showinfo("Éxito", "Miembro eliminado")

    def save_data(self):
        if self.planner.save_data():
            messagebox.showinfo("Éxito", "Datos guardados correctamente")
        else:
            messagebox.showerror("Error", "Error al guardar datos")

    def export_excel(self):
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if filename:
            try:
                self.planner.export_to_excel(filename)
                messagebox.showinfo("Éxito", "Exportado a Excel")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_pdf(self):
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filename:
            try:
                self.planner.export_to_pdf(filename)
                messagebox.showinfo("Éxito", "Exportado a PDF")
            except Exception as e:
                messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    app = HolidayPlannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
