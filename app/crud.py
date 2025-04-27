from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

def get_teacher(db: Session, teacher_id: int):
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()

def get_teacher_by_name(db: Session, name: str):
    return db.query(models.Teacher).filter(models.Teacher.name == name).first()

def get_teachers(db: Session):
    return db.query(models.Teacher).all()

def create_teacher(db: Session, teacher: schemas.TeacherCreate):
    db_teacher = models.Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def get_room(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()

def get_room_by_name(db: Session, name: str):
    return db.query(models.Room).filter(models.Room.name == name).first()

def get_rooms(db: Session):
    return db.query(models.Room).all()

def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_student_by_name(db: Session, name: str):
    return db.query(models.Student).filter(models.Student.name == name).first()

def get_students(db: Session):
    return db.query(models.Student).all()

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_schedule(db: Session, schedule_id: int):
    return db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()

def get_schedules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Schedule).offset(skip).limit(limit).all()

def create_schedule(db: Session, schedule: schemas.ScheduleCreate):
    # 겹침 검사
    if is_overlap(db,
        teacher_id=schedule.teacher_id,
        room_id=schedule.room_id,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time
    ):
        raise Exception("해당 시간에 이미 공간 또는 선생님이 배정되어 있습니다. (단체수업/특정 선생님 제외)")
    db_schedule = models.Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_schedule(db: Session, schedule_id: int, schedule_update: dict):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not schedule:
        return None
    # 겹침 검사
    teacher_id = schedule_update.get('teacher_id', schedule.teacher_id)
    room_id = schedule_update.get('room_id', schedule.room_id)
    day_of_week = schedule_update.get('day_of_week', schedule.day_of_week)
    start_time = schedule_update.get('start_time', schedule.start_time)
    end_time = schedule_update.get('end_time', schedule.end_time)
    if is_overlap(db,
        teacher_id=teacher_id,
        room_id=room_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        exclude_schedule_id=schedule_id
    ):
        raise Exception("해당 시간에 이미 공간 또는 선생님이 배정되어 있습니다. (단체수업/특정 선생님 제외)")
    for key, value in schedule_update.items():
        setattr(schedule, key, value)
    db.commit()
    db.refresh(schedule)
    return schedule

def delete_schedule(db: Session, schedule_id: int):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not schedule:
        return None
    db.delete(schedule)
    db.commit()
    return schedule

# 선생님별 주간 시간표

def get_schedules_by_teacher_week(db: Session, teacher_id: int) -> List[models.Schedule]:
    return db.query(models.Schedule).filter(models.Schedule.teacher_id == teacher_id).all()

# 공간별 주간 시간표

def get_schedules_by_room_week(db: Session, room_id: int) -> List[models.Schedule]:
    return db.query(models.Schedule).filter(models.Schedule.room_id == room_id).all()

def is_overlap(db: Session, *, teacher_id: int, room_id: int, day_of_week: str, start_time: str, end_time: str, exclude_schedule_id: int = None) -> bool:
    # 겹치는 시간대가 있는지 검사 (단, 단체수업/특정 선생님은 예외)
    # 1. 같은 공간, 같은 요일, 시간이 겹치는 수업
    q = db.query(models.Schedule).filter(
        models.Schedule.day_of_week == day_of_week,
        models.Schedule.room_id == room_id
    )
    if exclude_schedule_id:
        q = q.filter(models.Schedule.id != exclude_schedule_id)
    for sch in q:
        # 시간 겹침 판정
        if not (end_time <= sch.start_time or start_time >= sch.end_time):
            # 단체수업 예외
            if sch.type == models.ScheduleType.CLASS and sch.teacher and sch.teacher.name in ["김현철", "한태희"]:
                continue
            return True
    # 2. 같은 선생님, 같은 요일, 시간이 겹치는 수업
    q2 = db.query(models.Schedule).filter(
        models.Schedule.day_of_week == day_of_week,
        models.Schedule.teacher_id == teacher_id
    )
    if exclude_schedule_id:
        q2 = q2.filter(models.Schedule.id != exclude_schedule_id)
    for sch in q2:
        if not (end_time <= sch.start_time or start_time >= sch.end_time):
            # 단체수업 예외
            if sch.type == models.ScheduleType.CLASS and sch.teacher and sch.teacher.name in ["김현철", "한태희"]:
                continue
            return True
    return False
