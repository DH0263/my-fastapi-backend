from fastapi import FastAPI, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from . import models, schemas, crud, database
from .database import SessionLocal, create_tables
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status

models.Base.metadata.create_all(bind=database.engine_sync)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Teacher endpoints
@app.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = crud.get_teacher_by_name(db, name=teacher.name)
    if db_teacher:
        raise HTTPException(status_code=400, detail="Teacher already registered")
    return crud.create_teacher(db, teacher)

@app.get("/teachers/", response_model=List[schemas.Teacher])
def read_teachers(db: Session = Depends(get_db)):
    return crud.get_teachers(db)

@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = crud.get_teacher(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@app.delete("/teachers/{teacher_id}", status_code=204)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = crud.get_teacher(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    db.commit()
    return None

# Room endpoints
@app.post("/rooms/", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_name(db, name=room.name)
    if db_room:
        raise HTTPException(status_code=400, detail="Room already registered")
    return crud.create_room(db, room)

@app.get("/rooms/", response_model=List[schemas.Room])
def read_rooms(db: Session = Depends(get_db)):
    return crud.get_rooms(db)

@app.get("/rooms/{room_id}", response_model=schemas.Room)
def read_room(room_id: int, db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@app.delete("/rooms/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    db.delete(room)
    db.commit()
    return None

# Student endpoints
@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = crud.get_student_by_name(db, name=student.name)
    if db_student:
        raise HTTPException(status_code=400, detail="Student already registered")
    return crud.create_student(db, student)

@app.get("/students/", response_model=List[schemas.Student])
def read_students(db: Session = Depends(get_db)):
    return crud.get_students(db)

@app.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return None

# Schedule endpoints
@app.post("/schedules/", response_model=schemas.Schedule)
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    return crud.create_schedule(db, schedule)

@app.get("/schedules/", response_model=List[schemas.Schedule])
def read_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_schedules(db, skip=skip, limit=limit)

@app.patch("/schedules/{schedule_id}", response_model=schemas.Schedule)
def update_schedule(schedule_id: int, schedule_update: dict, db: Session = Depends(get_db)):
    updated = crud.update_schedule(db, schedule_id, schedule_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return updated

@app.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_schedule(db, schedule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return None

@app.put("/schedules/bulk_update_regular/")
def bulk_update_regular_schedules(
    filter: schemas.ScheduleBulkUpdateFilter = Body(...),
    update: schemas.ScheduleUpdate = Body(...),
    db: Session = Depends(get_db)
):
    q = db.query(models.Schedule).filter(
        models.Schedule.is_regular == 1,
        models.Schedule.teacher_id == filter.teacher_id,
        models.Schedule.student_id == filter.student_id,
        models.Schedule.room_id == filter.room_id,
        models.Schedule.day_of_week == filter.day_of_week,
        models.Schedule.start_time == filter.start_time,
        models.Schedule.end_time == filter.end_time,
        models.Schedule.type == filter.type,
    )
    count = 0
    for sch in q:
        for key, value in update.dict(exclude_unset=True).items():
            if value is not None:
                setattr(sch, key, value)
        count += 1
    db.commit()
    return {"updated": count}

@app.post("/schedules/bulk_update_regular/")
def bulk_update_regular_schedules_post(
    filter: schemas.ScheduleBulkUpdateFilter = Body(...),
    update: schemas.ScheduleUpdate = Body(...),
    db: Session = Depends(get_db)
):
    q = db.query(models.Schedule).filter(
        models.Schedule.is_regular == 1,
        models.Schedule.teacher_id == filter.teacher_id,
        models.Schedule.student_id == filter.student_id,
        models.Schedule.room_id == filter.room_id,
        models.Schedule.day_of_week == filter.day_of_week,
        models.Schedule.start_time == filter.start_time,
        models.Schedule.end_time == filter.end_time,
        models.Schedule.type == filter.type,
    )
    count = 0
    for sch in q:
        for key, value in update.dict(exclude_unset=True).items():
            if value is not None:
                setattr(sch, key, value)
        count += 1
    db.commit()
    return {"updated": count}

# Admin endpoints
@app.delete("/admin/schedules/delete_all", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_all_schedules(db: Session = Depends(get_db)):
    db.query(models.Schedule).delete()
    db.commit()
    return None

# 선생님별 주간 시간표
@app.get("/teachers/{teacher_id}/schedules", response_model=List[schemas.Schedule])
def get_teacher_weekly_schedule(teacher_id: int, db: Session = Depends(get_db)):
    teacher = crud.get_teacher(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return crud.get_schedules_by_teacher_week(db, teacher_id)

# 공간별 주간 시간표
@app.get("/rooms/{room_id}/schedules", response_model=List[schemas.Schedule])
def get_room_weekly_schedule(room_id: int, db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return crud.get_schedules_by_room_week(db, room_id)

# 공간 이름으로 주간 시간표 조회
@app.get("/rooms/by_name/{room_name}/schedules", response_model=List[schemas.Schedule])
def get_room_weekly_schedule_by_name(room_name: str, db: Session = Depends(get_db)):
    room = crud.get_room_by_name(db, name=room_name)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return crud.get_schedules_by_room_week(db, room.id)
