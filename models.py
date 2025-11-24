"""
Database models for Holiday Management System
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Team(Base):
    """Team/Equipo model"""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employees = relationship("Employee", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"


class Employee(Base):
    """Employee/Empleado model"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    role = Column(String(50), nullable=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="employees")
    vacations = relationship("Vacation", back_populates="employee", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', team_id={self.team_id})>"


class Vacation(Base):
    """Vacation/Vacaciones model"""
    __tablename__ = 'vacations'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    vacation_type = Column(String(50), default='vacation')  # vacation, sick, personal, etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="vacations")
    
    def __repr__(self):
        return f"<Vacation(id={self.id}, employee_id={self.employee_id}, {self.start_date} to {self.end_date})>"


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """Drop all tables in the database"""
    Base.metadata.drop_all(engine)
