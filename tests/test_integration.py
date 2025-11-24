"""
Integration tests for complete workflows
"""

import pytest
from database import (
    create_team, create_employee, create_vacation,
    get_all_teams, get_all_employees, get_all_vacations,
    get_employees_by_team, get_vacations_by_employee,
    get_vacations_by_date_range, get_employee_vacation_days,
    update_team, update_employee, update_vacation,
    delete_team, delete_employee, delete_vacation
)
from datetime import date


class TestTeamWorkflow:
    """Integration tests for team management workflow"""
    
    def test_create_and_retrieve_team(self):
        """Test creating and retrieving a team"""
        team = create_team("Integration Test Team", "Test description")
        
        assert team.id is not None
        assert team.name == "Integration Test Team"
        
        teams = get_all_teams()
        assert len(teams) > 0
        assert any(t.name == "Integration Test Team" for t in teams)
    
    def test_update_team(self):
        """Test updating a team"""
        team = create_team("Original Name", "Original description")
        
        updated = update_team(team.id, name="Updated Name", description="Updated description")
        
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
    
    def test_delete_empty_team(self):
        """Test deleting a team with no employees"""
        team = create_team("Team to Delete")
        team_id = team.id
        
        result = delete_team(team_id)
        assert result == True
        
        teams = get_all_teams()
        assert not any(t.id == team_id for t in teams)


class TestEmployeeWorkflow:
    """Integration tests for employee management workflow"""
    
    def test_create_and_retrieve_employee(self):
        """Test creating and retrieving an employee"""
        team = create_team("Employee Test Team")
        
        employee = create_employee(
            name="Test Employee",
            team_id=team.id,
            email="test@example.com",
            role="Tester"
        )
        
        assert employee.id is not None
        assert employee.name == "Test Employee"
        assert employee.team_id == team.id
        
        employees = get_all_employees()
        assert any(e.name == "Test Employee" for e in employees)
    
    def test_get_employees_by_team(self):
        """Test retrieving employees by team"""
        team1 = create_team("Team 1")
        team2 = create_team("Team 2")
        
        emp1 = create_employee("Employee 1", team1.id)
        emp2 = create_employee("Employee 2", team1.id)
        emp3 = create_employee("Employee 3", team2.id)
        
        team1_employees = get_employees_by_team(team1.id)
        assert len(team1_employees) == 2
        assert all(e.team_id == team1.id for e in team1_employees)
        
        team2_employees = get_employees_by_team(team2.id)
        assert len(team2_employees) == 1
        assert team2_employees[0].id == emp3.id
    
    def test_update_employee(self):
        """Test updating an employee"""
        team = create_team("Test Team")
        employee = create_employee("Original Name", team.id)
        
        updated = update_employee(
            employee.id,
            name="Updated Name",
            email="updated@example.com",
            role="Updated Role"
        )
        
        assert updated.name == "Updated Name"
        assert updated.email == "updated@example.com"
        assert updated.role == "Updated Role"
    
    def test_transfer_employee_to_different_team(self):
        """Test transferring an employee to a different team"""
        team1 = create_team("Team 1")
        team2 = create_team("Team 2")
        
        employee = create_employee("Employee", team1.id)
        assert employee.team_id == team1.id
        
        updated = update_employee(employee.id, team_id=team2.id)
        assert updated.team_id == team2.id


class TestVacationWorkflow:
    """Integration tests for vacation management workflow"""
    
    def test_create_and_retrieve_vacation(self):
        """Test creating and retrieving a vacation"""
        team = create_team("Vacation Test Team")
        employee = create_employee("Employee", team.id)
        
        vacation = create_vacation(
            employee_id=employee.id,
            start_date=date(2025, 12, 22),
            end_date=date(2025, 12, 31),
            vacation_type="vacation",
            notes="Christmas holidays"
        )
        
        assert vacation.id is not None
        assert vacation.employee_id == employee.id
        
        vacations = get_all_vacations()
        assert any(v.id == vacation.id for v in vacations)
    
    def test_get_vacations_by_employee(self):
        """Test retrieving vacations for a specific employee"""
        team = create_team("Test Team")
        emp1 = create_employee("Employee 1", team.id)
        emp2 = create_employee("Employee 2", team.id)
        
        vac1 = create_vacation(emp1.id, date(2025, 1, 1), date(2025, 1, 5))
        vac2 = create_vacation(emp1.id, date(2025, 2, 1), date(2025, 2, 5))
        vac3 = create_vacation(emp2.id, date(2025, 1, 1), date(2025, 1, 5))
        
        emp1_vacations = get_vacations_by_employee(emp1.id)
        assert len(emp1_vacations) == 2
        assert all(v.employee_id == emp1.id for v in emp1_vacations)
    
    def test_get_vacations_by_date_range(self):
        """Test retrieving vacations within a date range"""
        team = create_team("Test Team")
        employee = create_employee("Employee", team.id)
        
        vac1 = create_vacation(employee.id, date(2025, 1, 1), date(2025, 1, 5))
        vac2 = create_vacation(employee.id, date(2025, 6, 1), date(2025, 6, 5))
        vac3 = create_vacation(employee.id, date(2025, 12, 1), date(2025, 12, 5))
        
        # Get vacations in first half of year
        vacations = get_vacations_by_date_range(date(2025, 1, 1), date(2025, 6, 30))
        assert len(vacations) == 2
        
        # Get vacations in second half of year
        vacations = get_vacations_by_date_range(date(2025, 7, 1), date(2025, 12, 31))
        assert len(vacations) == 1
    
    def test_update_vacation(self):
        """Test updating a vacation"""
        team = create_team("Test Team")
        employee = create_employee("Employee", team.id)
        
        vacation = create_vacation(employee.id, date(2025, 1, 1), date(2025, 1, 5))
        
        updated = update_vacation(
            vacation.id,
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 10),
            vacation_type="sick",
            notes="Updated notes"
        )
        
        assert updated.start_date == date(2025, 2, 1)
        assert updated.end_date == date(2025, 2, 10)
        assert updated.vacation_type == "sick"
        assert updated.notes == "Updated notes"
    
    def test_delete_vacation(self):
        """Test deleting a vacation"""
        team = create_team("Test Team")
        employee = create_employee("Employee", team.id)
        vacation = create_vacation(employee.id, date(2025, 1, 1), date(2025, 1, 5))
        
        vacation_id = vacation.id
        result = delete_vacation(vacation_id)
        assert result == True
        
        vacations = get_all_vacations()
        assert not any(v.id == vacation_id for v in vacations)


class TestCompleteScenario:
    """Integration tests for complete real-world scenarios"""
    
    def test_complete_team_setup_scenario(self):
        """Test a complete scenario: create team, add employees, add vacations"""
        # Create team
        team = create_team("Development Team", "Software development team")
        
        # Add employees
        emp1 = create_employee("Alice", team.id, "alice@example.com", "Senior Developer")
        emp2 = create_employee("Bob", team.id, "bob@example.com", "Junior Developer")
        emp3 = create_employee("Charlie", team.id, "charlie@example.com", "Tech Lead")
        
        # Add vacations for each employee
        vac1 = create_vacation(emp1.id, date(2025, 12, 22), date(2025, 12, 31), "vacation", "Christmas")
        vac2 = create_vacation(emp2.id, date(2025, 12, 24), date(2025, 12, 26), "vacation", "Christmas")
        vac3 = create_vacation(emp3.id, date(2026, 1, 15), date(2026, 1, 20), "personal", "Personal time")
        
        # Verify team has 3 employees
        team_employees = get_employees_by_team(team.id)
        assert len(team_employees) == 3
        
        # Verify total vacations
        all_vacations = get_all_vacations()
        assert len(all_vacations) >= 3
        
        # Verify vacation days for Alice
        alice_days = get_employee_vacation_days(emp1.id, 2025)
        assert alice_days == 10  # Dec 22-31
    
    def test_vacation_days_calculation(self):
        """Test calculating vacation days for an employee"""
        team = create_team("Test Team")
        employee = create_employee("Employee", team.id)
        
        # Add multiple vacations in 2025
        create_vacation(employee.id, date(2025, 1, 1), date(2025, 1, 5))  # 5 days
        create_vacation(employee.id, date(2025, 6, 1), date(2025, 6, 10))  # 10 days
        create_vacation(employee.id, date(2025, 12, 20), date(2025, 12, 31))  # 12 days
        
        # Add vacation in 2026 (should not count)
        create_vacation(employee.id, date(2026, 1, 1), date(2026, 1, 5))  # 5 days
        
        total_days_2025 = get_employee_vacation_days(employee.id, 2025)
        assert total_days_2025 == 27  # 5 + 10 + 12
        
        total_days_2026 = get_employee_vacation_days(employee.id, 2026)
        assert total_days_2026 == 5
    
    def test_cascade_delete_scenario(self):
        """Test that deleting a team cascades to employees and vacations"""
        # Create team with employees and vacations
        team = create_team("Team to Delete")
        emp1 = create_employee("Employee 1", team.id)
        emp2 = create_employee("Employee 2", team.id)
        
        vac1 = create_vacation(emp1.id, date(2025, 1, 1), date(2025, 1, 5))
        vac2 = create_vacation(emp2.id, date(2025, 2, 1), date(2025, 2, 5))
        
        # Store IDs
        team_id = team.id
        emp1_id = emp1.id
        emp2_id = emp2.id
        vac1_id = vac1.id
        vac2_id = vac2.id
        
        # Delete team
        delete_team(team_id)
        
        # Verify everything is deleted
        teams = get_all_teams()
        assert not any(t.id == team_id for t in teams)
        
        employees = get_all_employees()
        assert not any(e.id in [emp1_id, emp2_id] for e in employees)
        
        vacations = get_all_vacations()
        assert not any(v.id in [vac1_id, vac2_id] for v in vacations)
