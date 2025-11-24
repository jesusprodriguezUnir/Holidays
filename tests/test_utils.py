"""
Unit tests for utility functions
"""

import pytest
from utils.calendar_utils import (
    get_month_date_range, get_quarter_date_range, get_year_date_range,
    count_vacation_days, get_vacation_conflicts, generate_calendar_data
)
from utils.export import generate_date_range, is_weekend
from datetime import date, timedelta
from models import Vacation


class TestDateRangeFunctions:
    """Tests for date range utility functions"""
    
    def test_get_month_date_range(self):
        """Test getting month date range"""
        start, end = get_month_date_range(2025, 1)
        assert start == date(2025, 1, 1)
        assert end == date(2025, 1, 31)
        
        start, end = get_month_date_range(2025, 2)
        assert start == date(2025, 2, 1)
        assert end == date(2025, 2, 28)
        
        # Leap year
        start, end = get_month_date_range(2024, 2)
        assert end == date(2024, 2, 29)
    
    def test_get_quarter_date_range(self):
        """Test getting quarter date range"""
        start, end = get_quarter_date_range(2025, 1)
        assert start == date(2025, 1, 1)
        assert end == date(2025, 3, 31)
        
        start, end = get_quarter_date_range(2025, 2)
        assert start == date(2025, 4, 1)
        assert end == date(2025, 6, 30)
        
        start, end = get_quarter_date_range(2025, 3)
        assert start == date(2025, 7, 1)
        assert end == date(2025, 9, 30)
        
        start, end = get_quarter_date_range(2025, 4)
        assert start == date(2025, 10, 1)
        assert end == date(2025, 12, 31)
    
    def test_get_year_date_range(self):
        """Test getting year date range"""
        start, end = get_year_date_range(2025)
        assert start == date(2025, 1, 1)
        assert end == date(2025, 12, 31)
    
    def test_generate_date_range(self):
        """Test generating date range"""
        start = date(2025, 1, 1)
        end = date(2025, 1, 5)
        dates = generate_date_range(start, end)
        
        assert len(dates) == 5
        assert dates[0] == start
        assert dates[-1] == end
        
        # Check consecutive dates
        for i in range(len(dates) - 1):
            assert dates[i+1] == dates[i] + timedelta(days=1)


class TestWeekendFunction:
    """Tests for weekend detection"""
    
    def test_is_weekend(self):
        """Test weekend detection"""
        # Saturday
        assert is_weekend(date(2025, 1, 4)) == True
        # Sunday
        assert is_weekend(date(2025, 1, 5)) == True
        # Monday
        assert is_weekend(date(2025, 1, 6)) == False
        # Friday
        assert is_weekend(date(2025, 1, 3)) == False


class TestVacationDaysCounting:
    """Tests for vacation days counting"""
    
    def test_count_vacation_days_simple(self):
        """Test counting vacation days"""
        start = date(2025, 1, 1)
        end = date(2025, 1, 5)
        
        days = count_vacation_days(start, end, exclude_weekends=False)
        assert days == 5
    
    def test_count_vacation_days_single_day(self):
        """Test counting single day vacation"""
        start = date(2025, 1, 1)
        end = date(2025, 1, 1)
        
        days = count_vacation_days(start, end, exclude_weekends=False)
        assert days == 1
    
    def test_count_vacation_days_exclude_weekends(self):
        """Test counting vacation days excluding weekends"""
        # Week from Monday to Sunday (5 weekdays + 2 weekend days)
        start = date(2025, 1, 6)  # Monday
        end = date(2025, 1, 12)   # Sunday
        
        days_all = count_vacation_days(start, end, exclude_weekends=False)
        assert days_all == 7
        
        days_weekdays = count_vacation_days(start, end, exclude_weekends=True)
        assert days_weekdays == 5


class TestVacationConflicts:
    """Tests for vacation conflict detection"""
    
    def test_no_conflicts(self, test_session, sample_employee):
        """Test when there are no conflicts"""
        # Existing vacation
        vac1 = Vacation(employee_id=sample_employee.id, 
                       start_date=date(2025, 1, 1), 
                       end_date=date(2025, 1, 5))
        test_session.add(vac1)
        test_session.commit()
        
        # New vacation with no overlap
        conflicts = get_vacation_conflicts(
            sample_employee.id,
            date(2025, 2, 1),
            date(2025, 2, 5),
            [vac1]
        )
        
        assert len(conflicts) == 0
    
    def test_exact_overlap(self, test_session, sample_employee):
        """Test exact date overlap"""
        vac1 = Vacation(employee_id=sample_employee.id, 
                       start_date=date(2025, 1, 1), 
                       end_date=date(2025, 1, 5))
        test_session.add(vac1)
        test_session.commit()
        
        conflicts = get_vacation_conflicts(
            sample_employee.id,
            date(2025, 1, 1),
            date(2025, 1, 5),
            [vac1]
        )
        
        assert len(conflicts) == 1
        assert conflicts[0].id == vac1.id
    
    def test_partial_overlap(self, test_session, sample_employee):
        """Test partial date overlap"""
        vac1 = Vacation(employee_id=sample_employee.id, 
                       start_date=date(2025, 1, 1), 
                       end_date=date(2025, 1, 10))
        test_session.add(vac1)
        test_session.commit()
        
        # Overlaps at the end
        conflicts = get_vacation_conflicts(
            sample_employee.id,
            date(2025, 1, 8),
            date(2025, 1, 15),
            [vac1]
        )
        assert len(conflicts) == 1
        
        # Overlaps at the start
        conflicts = get_vacation_conflicts(
            sample_employee.id,
            date(2024, 12, 28),
            date(2025, 1, 3),
            [vac1]
        )
        assert len(conflicts) == 1
    
    def test_exclude_vacation_id(self, test_session, sample_employee):
        """Test excluding a specific vacation from conflict check"""
        vac1 = Vacation(employee_id=sample_employee.id, 
                       start_date=date(2025, 1, 1), 
                       end_date=date(2025, 1, 5))
        test_session.add(vac1)
        test_session.commit()
        test_session.refresh(vac1)
        
        # Should not conflict with itself when excluded
        conflicts = get_vacation_conflicts(
            sample_employee.id,
            date(2025, 1, 1),
            date(2025, 1, 5),
            [vac1],
            exclude_vacation_id=vac1.id
        )
        
        assert len(conflicts) == 0
    
    def test_different_employee_no_conflict(self, test_session, sample_employees):
        """Test that vacations from different employees don't conflict"""
        emp1 = sample_employees[0]
        emp2 = sample_employees[1]
        
        vac1 = Vacation(employee_id=emp1.id, 
                       start_date=date(2025, 1, 1), 
                       end_date=date(2025, 1, 5))
        test_session.add(vac1)
        test_session.commit()
        
        # Same dates but different employee
        conflicts = get_vacation_conflicts(
            emp2.id,
            date(2025, 1, 1),
            date(2025, 1, 5),
            [vac1]
        )
        
        assert len(conflicts) == 0


class TestGenerateCalendarData:
    """Tests for calendar data generation"""
    
    def test_generate_calendar_data_empty(self):
        """Test with no employees"""
        data = generate_calendar_data([], [], date(2025, 1, 1), date(2025, 1, 31))
        assert len(data) == 0
    
    def test_generate_calendar_data_no_vacations(self, sample_employees):
        """Test with employees but no vacations"""
        data = generate_calendar_data(
            sample_employees, 
            [], 
            date(2025, 1, 1), 
            date(2025, 1, 31)
        )
        
        assert len(data) == len(sample_employees)
        for item in data:
            assert item['total_days'] == 0
            assert len(item['vacation_dates']) == 0
            assert len(item['vacations']) == 0
    
    def test_generate_calendar_data_with_vacations(self, sample_employees, sample_vacations):
        """Test with employees and vacations"""
        data = generate_calendar_data(
            sample_employees,
            sample_vacations,
            date(2025, 12, 1),
            date(2026, 1, 31)
        )
        
        assert len(data) > 0
        
        # Find employee with vacations
        emp_with_vac = next((item for item in data if item['total_days'] > 0), None)
        assert emp_with_vac is not None
        assert len(emp_with_vac['vacation_dates']) > 0
        assert len(emp_with_vac['vacations']) > 0
