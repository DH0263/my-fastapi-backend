from pydantic import BaseModel
from typing import Optional
import enum

class ScheduleType(str, enum.Enum):
    CLASS = "수업"
    COUNSEL = "상담"

class ChangeType(str, enum.Enum):
    NORMAL = "일반"
    CHANGED = "변경"
    SUPPLEMENT = "보강"

class TeacherBase(BaseModel):
    name: str
    subject: Optional[str] = None

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: int
    class Config:
        orm_mode = True

class RoomBase(BaseModel):
    name: str

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    name: str

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    class Config:
        orm_mode = True

class ScheduleBase(BaseModel):
    teacher_id: int
    room_id: int
    student_id: Optional[int] = None
    day_of_week: str
    start_time: str
    end_time: str
    type: ScheduleType
    is_regular: Optional[int] = 1
    change_type: Optional[ChangeType] = None

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    teacher: Optional[Teacher]
    room: Optional[Room]
    student: Optional[Student]
    class Config:
        orm_mode = True

class ScheduleBulkUpdateFilter(BaseModel):
    teacher_id: int
    student_id: int
    room_id: int
    day_of_week: str
    start_time: str
    end_time: str
    type: ScheduleType

class ScheduleUpdate(BaseModel):
    day_of_week: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room_id: Optional[int] = None
    teacher_id: Optional[int] = None
    student_id: Optional[int] = None
    type: Optional[ScheduleType] = None
    is_regular: Optional[int] = None
    change_type: Optional[ChangeType] = None
