from database import init_db, create_team, create_employee, get_session
from models import Team, Employee

def populate():
    print("Initializing database...")
    init_db()
    
    session = get_session()
    
    # Create Team Alfa
    print("Creating Team Alfa...")
    team_alfa = session.query(Team).filter_by(name="Alfa").first()
    if not team_alfa:
        team_alfa = Team(name="Alfa", description="Equipo Alfa")
        session.add(team_alfa)
        session.commit()
        session.refresh(team_alfa)
        print(f"Team Alfa created with ID: {team_alfa.id}")
    else:
        print(f"Team Alfa already exists with ID: {team_alfa.id}")
        
    # Employees data
    employees_data = [
        {"name": "Cesar Vicente", "role": "Product Owner"},
        {"name": "Jesus Rodríguez", "role": "Team Lead"},
        {"name": "Alan", "role": "Lider técnico"},
        {"name": "Felix", "role": "Programador Back-end"},
        {"name": "Erik", "role": "Programador Back-end"},
        {"name": "Adrian", "role": "Programador Front"}
    ]
    
    print("Creating employees...")
    for emp_data in employees_data:
        # Check if employee exists in this team
        existing_emp = session.query(Employee).filter_by(name=emp_data["name"], team_id=team_alfa.id).first()
        if not existing_emp:
            new_emp = Employee(
                name=emp_data["name"], 
                role=emp_data["role"], 
                team_id=team_alfa.id,
                email=None # Placeholder as requested
            )
            session.add(new_emp)
            print(f"Added employee: {emp_data['name']} - {emp_data['role']}")
        else:
            print(f"Employee {emp_data['name']} already exists.")
            
    session.commit()
    session.close()
    print("Database population completed successfully.")

if __name__ == "__main__":
    populate()
