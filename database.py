"""
Database configuration and CRUD operations
"""

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Team, Employee, Vacation
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import os

# Database configuration
DATABASE_URL = "sqlite:///holidays.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = scoped_session(sessionmaker(bind=engine))


def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(engine)


def get_session():
    """Get database session"""
    return SessionLocal()


# ==================== TEAM CRUD ====================

def create_team(name: str, description: str = None) -> Team:
    """Create a new team"""
    session = get_session()
    try:
        team = Team(name=name, description=description)
        session.add(team)
        session.commit()
        session.refresh(team)
        return team
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_teams() -> List[Team]:
    """Get all teams"""
    session = get_session()
    try:
        return session.query(Team).all()
    finally:
        session.close()


def get_team_by_id(team_id: int) -> Optional[Team]:
    """Get team by ID"""
    session = get_session()
    try:
        return session.query(Team).filter(Team.id == team_id).first()
    finally:
        session.close()


def update_team(team_id: int, name: str = None, description: str = None) -> Optional[Team]:
    """Update team information"""
    session = get_session()
    try:
        team = session.query(Team).filter(Team.id == team_id).first()
        if team:
            if name:
                team.name = name
            if description is not None:
                team.description = description
            session.commit()
            session.refresh(team)
        return team
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_team(team_id: int) -> bool:
    """Delete a team"""
    session = get_session()
    try:
        team = session.query(Team).filter(Team.id == team_id).first()
        if team:
            session.delete(team)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== EMPLOYEE CRUD ====================

def create_employee(name: str, team_id: int, email: str = None, role: str = None) -> Employee:
    """Create a new employee"""
    session = get_session()
    try:
        employee = Employee(name=name, team_id=team_id, email=email, role=role)
        session.add(employee)
        session.commit()
        session.refresh(employee)
        return employee
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_employees() -> List[Employee]:
    """Get all employees"""
    session = get_session()
    try:
        return session.query(Employee).all()
    finally:
        session.close()


def get_employees_by_team(team_id: int) -> List[Employee]:
    """Get all employees in a team"""
    session = get_session()
    try:
        return session.query(Employee).filter(Employee.team_id == team_id).all()
    finally:
        session.close()


def get_employee_by_id(employee_id: int) -> Optional[Employee]:
    """Get employee by ID"""
    session = get_session()
    try:
        return session.query(Employee).filter(Employee.id == employee_id).first()
    finally:
        session.close()


def update_employee(employee_id: int, name: str = None, email: str = None, 
                   role: str = None, team_id: int = None) -> Optional[Employee]:
    """Update employee information"""
    session = get_session()
    try:
        employee = session.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            if name:
                employee.name = name
            if email is not None:
                employee.email = email
            if role is not None:
                employee.role = role
            if team_id:
                employee.team_id = team_id
            session.commit()
            session.refresh(employee)
        return employee
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_employee(employee_id: int) -> bool:
    """Delete an employee"""
    session = get_session()
    try:
        employee = session.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            session.delete(employee)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== VACATION CRUD ====================

def create_vacation(employee_id: int, start_date: date, end_date: date,
                   vacation_type: str = 'vacation', notes: str = None) -> Vacation:
    """Create a new vacation period"""
    session = get_session()
    try:
        vacation = Vacation(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            vacation_type=vacation_type,
            notes=notes
        )
        session.add(vacation)
        session.commit()
        session.refresh(vacation)
        return vacation
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_vacations() -> List[Vacation]:
    """Get all vacations"""
    session = get_session()
    try:
        return session.query(Vacation).all()
    finally:
        session.close()


def get_vacations_by_employee(employee_id: int) -> List[Vacation]:
    """Get all vacations for an employee"""
    session = get_session()
    try:
        return session.query(Vacation).filter(Vacation.employee_id == employee_id).all()
    finally:
        session.close()


def get_vacations_by_date_range(start_date: date, end_date: date) -> List[Vacation]:
    """Get all vacations within a date range"""
    session = get_session()
    try:
        return session.query(Vacation).filter(
            or_(
                and_(Vacation.start_date >= start_date, Vacation.start_date <= end_date),
                and_(Vacation.end_date >= start_date, Vacation.end_date <= end_date),
                and_(Vacation.start_date <= start_date, Vacation.end_date >= end_date)
            )
        ).all()
    finally:
        session.close()


def get_vacations_by_team_and_date(team_id: int, start_date: date, end_date: date) -> List[Vacation]:
    """Get all vacations for a team within a date range"""
    session = get_session()
    try:
        return session.query(Vacation).join(Employee).filter(
            Employee.team_id == team_id,
            or_(
                and_(Vacation.start_date >= start_date, Vacation.start_date <= end_date),
                and_(Vacation.end_date >= start_date, Vacation.end_date <= end_date),
                and_(Vacation.start_date <= start_date, Vacation.end_date >= end_date)
            )
        ).all()
    finally:
        session.close()


def update_vacation(vacation_id: int, start_date: date = None, end_date: date = None,
                   vacation_type: str = None, notes: str = None) -> Optional[Vacation]:
    """Update vacation information"""
    session = get_session()
    try:
        vacation = session.query(Vacation).filter(Vacation.id == vacation_id).first()
        if vacation:
            if start_date:
                vacation.start_date = start_date
            if end_date:
                vacation.end_date = end_date
            if vacation_type:
                vacation.vacation_type = vacation_type
            if notes is not None:
                vacation.notes = notes
            session.commit()
            session.refresh(vacation)
        return vacation
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_vacation(vacation_id: int) -> bool:
    """Delete a vacation"""
    session = get_session()
    try:
        vacation = session.query(Vacation).filter(Vacation.id == vacation_id).first()
        if vacation:
            session.delete(vacation)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== UTILITY FUNCTIONS ====================

def get_employee_vacation_days(employee_id: int, year: int = None) -> int:
    """Get total vacation days for an employee in a year"""
    session = get_session()
    try:
        query = session.query(Vacation).filter(Vacation.employee_id == employee_id)
        
        if year:
            start_of_year = date(year, 1, 1)
            end_of_year = date(year, 12, 31)
            query = query.filter(
                or_(
                    and_(Vacation.start_date >= start_of_year, Vacation.start_date <= end_of_year),
                    and_(Vacation.end_date >= start_of_year, Vacation.end_date <= end_of_year),
                    and_(Vacation.start_date <= start_of_year, Vacation.end_date >= end_of_year)
                )
            )
        
        vacations = query.all()
        total_days = 0
        
        for vacation in vacations:
            days = (vacation.end_date - vacation.start_date).days + 1
            total_days += days
        
        return total_days
    finally:
        session.close()


def is_employee_on_vacation(employee_id: int, check_date: date) -> bool:
    """Check if an employee is on vacation on a specific date"""
    session = get_session()
    try:
        vacation = session.query(Vacation).filter(
            Vacation.employee_id == employee_id,
            Vacation.start_date <= check_date,
            Vacation.end_date >= check_date
        ).first()
        return vacation is not None
    finally:
        session.close()
