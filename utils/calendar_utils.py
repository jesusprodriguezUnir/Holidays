"""
Calendar utility functions
"""

from datetime import date, timedelta
from typing import List, Dict, Tuple
import calendar


def get_month_date_range(year: int, month: int) -> Tuple[date, date]:
    """Get the first and last day of a month"""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day


def get_quarter_date_range(year: int, quarter: int) -> Tuple[date, date]:
    """Get the first and last day of a quarter"""
    if quarter == 1:
        return date(year, 1, 1), date(year, 3, 31)
    elif quarter == 2:
        return date(year, 4, 1), date(year, 6, 30)
    elif quarter == 3:
        return date(year, 7, 1), date(year, 9, 30)
    else:
        return date(year, 10, 1), date(year, 12, 31)


def get_year_date_range(year: int) -> Tuple[date, date]:
    """Get the first and last day of a year"""
    return date(year, 1, 1), date(year, 12, 31)


def generate_calendar_data(employees, vacations, start_date: date, end_date: date) -> List[Dict]:
    """
    Generate calendar data for display
    
    Returns list of dicts with employee info and vacation dates
    """
    calendar_data = []
    
    for employee in employees:
        emp_vacations = [v for v in vacations if v.employee_id == employee.id]
        
        # Create set of vacation dates
        vacation_dates = set()
        vacation_list = []
        
        for vacation in emp_vacations:
            current = vacation.start_date
            while current <= vacation.end_date:
                if start_date <= current <= end_date:
                    vacation_dates.add(current)
                current += timedelta(days=1)
            
            vacation_list.append({
                'start_date': vacation.start_date,
                'end_date': vacation.end_date,
                'type': vacation.vacation_type,
                'notes': vacation.notes
            })
        
        calendar_data.append({
            'id': employee.id,
            'name': employee.name,
            'role': employee.role or '',
            'team': employee.team.name if employee.team else '',
            'team_id': employee.team_id,
            'vacation_dates': vacation_dates,
            'vacations': vacation_list,
            'total_days': len(vacation_dates)
        })
    
    return calendar_data


def count_vacation_days(start_date: date, end_date: date, exclude_weekends: bool = False) -> int:
    """Count the number of days between two dates, optionally excluding weekends"""
    total_days = (end_date - start_date).days + 1
    
    if not exclude_weekends:
        return total_days
    
    # Count weekdays only
    weekdays = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Monday = 0, Sunday = 6
            weekdays += 1
        current += timedelta(days=1)
    
    return weekdays


def get_vacation_conflicts(employee_id: int, start_date: date, end_date: date, 
                          existing_vacations: List, exclude_vacation_id: int = None) -> List:
    """
    Check for vacation conflicts for an employee
    
    Returns list of conflicting vacations
    """
    conflicts = []
    
    for vacation in existing_vacations:
        if vacation.employee_id != employee_id:
            continue
        
        if exclude_vacation_id and vacation.id == exclude_vacation_id:
            continue
        
        # Check for overlap
        if (start_date <= vacation.end_date and end_date >= vacation.start_date):
            conflicts.append(vacation)
    
    return conflicts
