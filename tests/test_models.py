"""
Unit tests for database models
"""

import pytest
from models import Team, Employee, Vacation
from datetime import date, datetime


class TestTeamModel:
    """Tests for Team model"""
    
    def test_create_team(self, test_session):
        """Test creating a team"""
        team = Team(name="Test Team", description="Test description")
        test_session.add(team)
        test_session.commit()
        
        assert team.id is not None
        assert team.name == "Test Team"
        assert team.description == "Test description"
        assert isinstance(team.created_at, datetime)
    
    def test_team_unique_name(self, test_session, sample_team):
        """Test that team names must be unique"""
        duplicate_team = Team(name=sample_team.name, description="Different description")
        test_session.add(duplicate_team)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_session.commit()
    
    def test_team_employees_relationship(self, test_session, sample_team):
        """Test team-employees relationship"""
        emp1 = Employee(name="Employee 1", team_id=sample_team.id)
        emp2 = Employee(name="Employee 2", team_id=sample_team.id)
        test_session.add_all([emp1, emp2])
        test_session.commit()
        
        test_session.refresh(sample_team)
        assert len(sample_team.employees) == 2
    
    def test_team_cascade_delete(self, test_session, sample_team, sample_employee):
        """Test that deleting a team cascades to employees"""
        team_id = sample_team.id
        employee_id = sample_employee.id
        
        test_session.delete(sample_team)
        test_session.commit()
        
        # Employee should be deleted too
        deleted_employee = test_session.query(Employee).filter(Employee.id == employee_id).first()
        assert deleted_employee is None


class TestEmployeeModel:
    """Tests for Employee model"""
    
    def test_create_employee(self, test_session, sample_team):
        """Test creating an employee"""
        employee = Employee(
            name="Test Employee",
            email="test@example.com",
            role="Tester",
            team_id=sample_team.id
        )
        test_session.add(employee)
        test_session.commit()
        
        assert employee.id is not None
        assert employee.name == "Test Employee"
        assert employee.email == "test@example.com"
        assert employee.role == "Tester"
        assert employee.team_id == sample_team.id
        assert isinstance(employee.created_at, datetime)
    
    def test_employee_unique_email(self, test_session, sample_employee, sample_team):
        """Test that employee emails must be unique"""
        duplicate_employee = Employee(
            name="Different Name",
            email=sample_employee.email,
            team_id=sample_team.id
        )
        test_session.add(duplicate_employee)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_session.commit()
    
    def test_employee_team_relationship(self, test_session, sample_employee, sample_team):
        """Test employee-team relationship"""
        assert sample_employee.team.id == sample_team.id
        assert sample_employee.team.name == sample_team.name
    
    def test_employee_vacations_relationship(self, test_session, sample_employee):
        """Test employee-vacations relationship"""
        vac1 = Vacation(employee_id=sample_employee.id, start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))
        vac2 = Vacation(employee_id=sample_employee.id, start_date=date(2025, 2, 1), end_date=date(2025, 2, 3))
        test_session.add_all([vac1, vac2])
        test_session.commit()
        
        test_session.refresh(sample_employee)
        assert len(sample_employee.vacations) == 2


class TestVacationModel:
    """Tests for Vacation model"""
    
    def test_create_vacation(self, test_session, sample_employee):
        """Test creating a vacation"""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2025, 12, 22),
            end_date=date(2025, 12, 31),
            vacation_type="vacation",
            notes="Christmas break"
        )
        test_session.add(vacation)
        test_session.commit()
        
        assert vacation.id is not None
        assert vacation.employee_id == sample_employee.id
        assert vacation.start_date == date(2025, 12, 22)
        assert vacation.end_date == date(2025, 12, 31)
        assert vacation.vacation_type == "vacation"
        assert vacation.notes == "Christmas break"
        assert isinstance(vacation.created_at, datetime)
    
    def test_vacation_employee_relationship(self, test_session, sample_vacation, sample_employee):
        """Test vacation-employee relationship"""
        assert sample_vacation.employee.id == sample_employee.id
        assert sample_vacation.employee.name == sample_employee.name
    
    def test_vacation_default_type(self, test_session, sample_employee):
        """Test vacation default type"""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 5)
        )
        test_session.add(vacation)
        test_session.commit()
        
        assert vacation.vacation_type == "vacation"
    
    def test_vacation_cascade_delete(self, test_session, sample_employee, sample_vacation):
        """Test that deleting an employee cascades to vacations"""
        vacation_id = sample_vacation.id
        
        test_session.delete(sample_employee)
        test_session.commit()
        
        # Vacation should be deleted too
        deleted_vacation = test_session.query(Vacation).filter(Vacation.id == vacation_id).first()
        assert deleted_vacation is None
