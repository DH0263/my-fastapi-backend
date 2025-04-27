from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Time
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class ScheduleType(str, enum.Enum):
    CLASS = "수업"
    COUNSEL = "상담"

class ChangeType(str, enum.Enum):
    NORMAL = "일반"
    CHANGED = "변경"
    SUPPLEMENT = "보강"

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    subject = Column(String, nullable=True)
    schedules = relationship("Schedule", back_populates="teacher")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    schedules = relationship("Schedule", back_populates="room")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    schedules = relationship("Schedule", back_populates="student")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    day_of_week = Column(String, nullable=False)  # "월요일" 등
    start_time = Column(String, nullable=False)   # "13:00"
    end_time = Column(String, nullable=False)     # "15:00"
    type = Column(Enum(ScheduleType), nullable=False)
    is_regular = Column(Integer, default=1)  # 1: 기본시간표, 0: 특별일정
    change_type = Column(Enum(ChangeType), nullable=True)  # 변경/보강/일반

    teacher = relationship("Teacher", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")
    student = relationship("Student", back_populates="schedules")
