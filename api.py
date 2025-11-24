from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from typing import List, Optional
import uvicorn

from database import (
    get_all_teams, get_employees_by_team, get_all_employees,
    get_vacations_by_team_and_date, create_vacation, 
    delete_vacation, get_vacations_by_employee,
    is_employee_on_vacation, get_session,
    create_team, update_team, delete_team,
    create_employee, update_employee, delete_employee
)
from models import Vacation, Team, Employee

app = FastAPI(title="Holiday Planner API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# --- Pydantic Models ---
class VacationToggleRequest(BaseModel):
    employee_id: int
    date: date

class VacationRangeRequest(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    type: str = "vacation"
    notes: Optional[str] = None

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class EmployeeCreate(BaseModel):
    name: str
    role: Optional[str] = None
    team_id: int
    email: Optional[str] = None

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    team_id: Optional[int] = None
    email: Optional[str] = None

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- TEAMS ---
@app.get("/api/teams")
async def read_teams():
    teams = get_all_teams()
    return [{"id": t.id, "name": t.name, "description": t.description} for t in teams]

@app.post("/api/teams")
async def create_new_team(team: TeamCreate):
    try:
        new_team = create_team(name=team.name, description=team.description)
        return {"id": new_team.id, "name": new_team.name, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/teams/{team_id}")
async def update_existing_team(team_id: int, team: TeamUpdate):
    try:
        updated = update_team(team_id, name=team.name, description=team.description)
        if not updated:
            raise HTTPException(status_code=404, detail="Team not found")
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/teams/{team_id}")
async def delete_existing_team(team_id: int):
    try:
        success = delete_team(team_id)
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- EMPLOYEES ---
@app.get("/api/employees")
async def read_all_employees(team_id: Optional[int] = None):
    if team_id:
        employees = get_employees_by_team(team_id)
    else:
        employees = get_all_employees()
    
    return [{
        "id": e.id, 
        "name": e.name, 
        "role": e.role, 
        "team_id": e.team_id,
        "team_name": e.team.name if e.team else ""
    } for e in employees]

@app.post("/api/employees")
async def create_new_employee(emp: EmployeeCreate):
    try:
        new_emp = create_employee(
            name=emp.name, 
            team_id=emp.team_id, 
            role=emp.role, 
            email=emp.email
        )
        return {"id": new_emp.id, "name": new_emp.name, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/employees/{emp_id}")
async def update_existing_employee(emp_id: int, emp: EmployeeUpdate):
    try:
        updated = update_employee(
            emp_id, 
            name=emp.name, 
            role=emp.role, 
            team_id=emp.team_id,
            email=emp.email
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/employees/{emp_id}")
async def delete_existing_employee(emp_id: int):
    try:
        success = delete_employee(emp_id)
        if not success:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- VACATIONS ---
@app.get("/api/vacations")
async def read_vacations(
    team_id: int, 
    start_date: date, 
    end_date: date
):
    vacations = get_vacations_by_team_and_date(team_id, start_date, end_date)
    
    result = []
    for v in vacations:
        curr = v.start_date
        while curr <= v.end_date:
            if start_date <= curr <= end_date:
                result.append({
                    "employee_id": v.employee_id,
                    "date": curr.isoformat(),
                    "type": v.vacation_type,
                    "vacation_id": v.id
                })
            curr += timedelta(days=1)
            
    return result

@app.post("/api/vacations/range")
async def create_vacation_range(data: VacationRangeRequest):
    try:
        # Simple creation without complex conflict checks for now
        # Ideally we should check for overlaps and merge or reject
        create_vacation(
            employee_id=data.employee_id,
            start_date=data.start_date,
            end_date=data.end_date,
            vacation_type=data.type,
            notes=data.notes
        )
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/vacations/toggle")
async def toggle_vacation(data: VacationToggleRequest):
    session = get_session()
    try:
        existing_vacation = session.query(Vacation).filter(
            Vacation.employee_id == data.employee_id,
            Vacation.start_date <= data.date,
            Vacation.end_date >= data.date
        ).first()
        
        if existing_vacation:
            # Logic to remove day (split or delete)
            original_start = existing_vacation.start_date
            original_end = existing_vacation.end_date
            vac_type = existing_vacation.vacation_type
            notes = existing_vacation.notes
            
            session.delete(existing_vacation)
            session.commit()
            
            if original_start < data.date:
                left_end = data.date - timedelta(days=1)
                v1 = Vacation(
                    employee_id=data.employee_id,
                    start_date=original_start,
                    end_date=left_end,
                    vacation_type=vac_type,
                    notes=notes
                )
                session.add(v1)
                
            if original_end > data.date:
                right_start = data.date + timedelta(days=1)
                v2 = Vacation(
                    employee_id=data.employee_id,
                    start_date=right_start,
                    end_date=original_end,
                    vacation_type=vac_type,
                    notes=notes
                )
                session.add(v2)
                
            session.commit()
            return {"status": "removed", "date": data.date}
            
        else:
            new_vacation = Vacation(
                employee_id=data.employee_id,
                start_date=data.date,
                end_date=data.date,
                vacation_type="vacation"
            )
            session.add(new_vacation)
            session.commit()
            return {"status": "added", "date": data.date}
            
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
