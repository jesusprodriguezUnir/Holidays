"""
Test fixtures and configuration for pytest
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Team, Employee, Vacation
from datetime import date, datetime
import os


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session"""
    SessionLocal = scoped_session(sessionmaker(bind=test_engine))
    session = SessionLocal()
    yield session
    session.close()
    SessionLocal.remove()


@pytest.fixture
def sample_team(test_session):
    """Create a sample team for testing"""
    team = Team(name="Test Team", description="A test team")
    test_session.add(team)
    test_session.commit()
    test_session.refresh(team)
    return team


@pytest.fixture
def sample_teams(test_session):
    """Create multiple sample teams"""
    teams = [
        Team(name="Development", description="Dev team"),
        Team(name="Marketing", description="Marketing team"),
        Team(name="Sales", description="Sales team")
    ]
    for team in teams:
        test_session.add(team)
    test_session.commit()
    for team in teams:
        test_session.refresh(team)
    return teams


@pytest.fixture
def sample_employee(test_session, sample_team):
    """Create a sample employee for testing"""
    employee = Employee(
        name="John Doe",
        email="john@example.com",
        role="Developer",
        team_id=sample_team.id
    )
    test_session.add(employee)
    test_session.commit()
    test_session.refresh(employee)
    return employee


@pytest.fixture
def sample_employees(test_session, sample_teams):
    """Create multiple sample employees"""
    employees = [
        Employee(name="Alice Smith", email="alice@example.com", role="Developer", team_id=sample_teams[0].id),
        Employee(name="Bob Johnson", email="bob@example.com", role="Designer", team_id=sample_teams[0].id),
        Employee(name="Charlie Brown", email="charlie@example.com", role="Manager", team_id=sample_teams[1].id),
        Employee(name="Diana Prince", email="diana@example.com", role="Sales Rep", team_id=sample_teams[2].id)
    ]
    for emp in employees:
        test_session.add(emp)
    test_session.commit()
    for emp in employees:
        test_session.refresh(emp)
    return employees


@pytest.fixture
def sample_vacation(test_session, sample_employee):
    """Create a sample vacation for testing"""
    vacation = Vacation(
        employee_id=sample_employee.id,
        start_date=date(2025, 12, 22),
        end_date=date(2025, 12, 31),
        vacation_type="vacation",
        notes="Christmas holidays"
    )
    test_session.add(vacation)
    test_session.commit()
    test_session.refresh(vacation)
    return vacation


@pytest.fixture
def sample_vacations(test_session, sample_employees):
    """Create multiple sample vacations"""
    vacations = [
        Vacation(employee_id=sample_employees[0].id, start_date=date(2025, 12, 22), 
                end_date=date(2025, 12, 31), vacation_type="vacation"),
        Vacation(employee_id=sample_employees[0].id, start_date=date(2026, 1, 15), 
                end_date=date(2026, 1, 20), vacation_type="personal"),
        Vacation(employee_id=sample_employees[1].id, start_date=date(2025, 12, 24), 
                end_date=date(2025, 12, 26), vacation_type="vacation"),
        Vacation(employee_id=sample_employees[2].id, start_date=date(2026, 2, 1), 
                end_date=date(2026, 2, 7), vacation_type="sick")
    ]
    for vac in vacations:
        test_session.add(vac)
    test_session.commit()
    for vac in vacations:
        test_session.refresh(vac)
    return vacations


@pytest.fixture
def clean_test_db():
    """Clean up test database file if it exists"""
    test_db_file = "test_holidays.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)


@pytest.fixture(autouse=True)
def patch_database_session(test_engine):
    """Patch database session to use test engine"""
    import database
    from sqlalchemy.orm import sessionmaker, scoped_session
    
    # Save original
    original_session_local = database.SessionLocal
    original_engine = database.engine
    
    # Override
    database.engine = test_engine
    database.SessionLocal = scoped_session(sessionmaker(bind=test_engine))
    
    yield
    
    # Restore
    database.SessionLocal = original_session_local
    database.engine = original_engine
