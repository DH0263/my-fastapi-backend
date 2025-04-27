import re
from app import models, database
from sqlalchemy.orm import Session

def parse_schedule_text(text):
    teachers = {}
    rooms = set()
    students = set()
    schedules = []
    current_teacher = None
    current_subject = None
    current_day = None
    day_map = {
        '월요일': '월요일', '화요일': '화요일', '수요일': '수요일',
        '목요일': '목요일', '금요일': '금요일', '토요일': '토요일', '일요일': '일요일'
    }
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'─+ (.+) 선생님 \((.+)\)', line)
        if m:
            current_teacher = m.group(1)
            current_subject = m.group(2)
            teachers[current_teacher] = current_subject
            continue
        if line in day_map:
            current_day = day_map[line]
            continue
        m = re.match(r'•?\s*(\d{1,2}:\d{2}) – (\d{1,2}:\d{2}): (수업|상담) – ([^\(]+) \(([^\)]+)\)', line)
        if m:
            start, end, typ, student, room = m.groups()
            room = room.strip()
            rooms.add(room)
            students.add(student.strip())
            schedules.append({
                'teacher': current_teacher,
                'subject': current_subject,
                'day': current_day,
                'start': start,
                'end': end,
                'type': typ,
                'student': student.strip(),
                'room': room
            })
            continue
        # 여러명 수업 (ex: "09:00 – 12:00: 수업 – 오현택, 강영준 ... (대강의실)")
        m = re.match(r'•?\s*(\d{1,2}:\d{2}) – (\d{1,2}:\d{2}): (수업|상담) – ([^\(]+)\(([^\)]+)\)', line)
        if m:
            start, end, typ, student_list, room = m.groups()
            room = room.strip()
            students_list = [s.strip() for s in student_list.split(',') if s.strip()]
            for student in students_list:
                rooms.add(room)
                students.add(student)
                schedules.append({
                    'teacher': current_teacher,
                    'subject': current_subject,
                    'day': current_day,
                    'start': start,
                    'end': end,
                    'type': typ,
                    'student': student,
                    'room': room
                })
    return teachers, rooms, students, schedules

# 실제 시간표 텍스트를 여기에 복사/붙여넣기
schedule_text = '''
──────────────────────────── 김윤아 선생님 (국어)
월요일
• 13:00 – 15:00: 수업 – 이동현 (컨설팅룸1)
• 15:00 – 15:30: 상담 – 홍수민 (컨설팅룸1)
• 15:30 – 16:00: 상담 – 이다경 (컨설팅룸1)
• 16:00 – 16:30: 상담 – 고건우 (컨설팅룸1)
• 16:30 – 17:00: 상담 – 남영서 (컨설팅룸1)
• 17:00 – 17:30: 상담 – 김유건 (컨설팅룸1)
• 17:30 – 18:00: 상담 – 최진혁 (컨설팅룸1)
• 19:00 – 21:00: 수업 – 김영인 (컨설팅룸1)
화요일
• 13:00 – 15:00: 수업 – 이동현 (컨설팅룸1)
• 15:00 – 17:00: 수업 – 이다경 (컨설팅룸1)
• 17:00 – 17:30: 상담 – 권규빈 (컨설팅룸1)
• 17:30 – 18:00: 상담 – 김수영 (컨설팅룸1)
수요일
• 13:00 – 15:00: 수업 – 김영인 (컨설팅룸1)
• 15:00 – 17:00: 수업 – 이다경 (컨설팅룸1)
• 17:00 – 17:30: 상담 – 안성빈 (컨설팅룸1)
──────────────────────────── 최호대 선생님 (국어)
화요일
• 16:00 – 18:00: 수업 – 강우진 (컨설팅룸2)
• 19:00 – 21:00: 수업 – 김수민 (컨설팅룸2)
• 21:00 – 21:30: 상담 – 박민우 (컨설팅룸2)
• 21:30 – 22:00: 상담 – 최준후 (컨설팅룸2)
수요일
• 19:00 – 21:00: 수업 – 백은솔 (컨설팅룸2)
• 21:00 – 21:30: 상담 – 장세훈 (컨설팅룸2)
목요일
• 16:00 – 18:00: 수업 – 강우진 (컨설팅룸2)
• 19:00 – 21:00: 수업 – 김수민 (컨설팅룸2)
• 21:00 – 21:30: 상담 – 정규민 (컨설팅룸2)
• 21:30 – 22:00: 상담 – 홍경은 (컨설팅룸2)
금요일
• 19:00 – 21:00: 수업 – 백은솔 (컨설팅룸2)
• 21:00 – 21:30: 상담 – 이주호 (컨설팅룸2)
• 21:30 – 22:00: 상담 – 윤준 (컨설팅룸2)
──────────────────────────── 최민재 선생님 (수학)
월요일
• 13:30 – 14:00: 상담 – 권동현 (컨설팅룸2)
• 14:00 – 14:30: 상담 – 이승운 (컨설팅룸2)
• 15:00 – 15:30: 상담 – 전찬 (컨설팅룸2)
• 16:00 – 18:00: 수업 – 이동현 (컨설팅룸2)
• 19:00 – 20:30: 수업 – 홍경은 (컨설팅룸2)
화요일
• 13:00 – 13:30: 상담 – 강우진 (컨설팅룸2)
• 13:30 – 14:00: 상담 – 김규민 (컨설팅룸2)
• 14:00 – 14:30: 상담 – 박재현 (컨설팅룸2)
• 14:30 – 15:00: 상담 – 장예원 (컨설팅룸2)
• 15:00 – 15:30: 상담 – 박현민 (컨설팅룸2)
• 16:00 – 18:00: 수업 – 이동현 (컨설팅룸2)
• 19:00 – 20:30: 수업 – 홍경은 (컨설팅룸2)
수요일
• 13:00 – 13:30: 상담 – 이채은 (컨설팅룸2)
• 13:30 – 14:00: 상담 – 박나율 (컨설팅룸2)
• 14:00 – 14:30: 상담 – 박기령 (컨설팅룸2)
• 14:30 – 15:00: 상담 – 조현민 (컨설팅룸2)
• 15:00 – 15:30: 상담 – 김영인 (컨설팅룸2)
• 16:00 – 18:00: 수업 – 이동현 (컨설팅룸2)
• 19:00 – 20:30: 수업 – 홍경은 (컨설팅룸2)
──────────────────────────── 정신희 선생님 (수학)
월요일
• 13:00 – 15:00: 수업 – 이다경 (컨설팅룸4)
• 15:00 – 17:00: 수업 – 오현택 (컨설팅룸4)
• 17:00 – 17:30: 상담 – 정지훈 (컨설팅룸4)
• 17:30 – 18:00: 상담 – 권영회 (컨설팅룸4)
• 19:00 – 20:30: 수업 – 김예은 (컨설팅룸4)
수요일
• 13:00 – 15:00: 수업 – 이다경 (컨설팅룸4)
• 15:00 – 16:30: 수업 – 김예은 (컨설팅룸4)
• 17:00 – 17:30: 상담 – 김수민 (컨설팅룸4)
• 17:30 – 18:00: 상담 – 최다찬 (컨설팅룸4)
목요일
13:00 – 15:00: 수업 – 오현택 (컨설팅룸4)
금요일
• 13:00 – 15:00: 수업 – 이다경 (컨설팅룸4)
• 15:00 – 16:30: 수업 – 김예은 (컨설팅룸4)
• 17:00 – 17:30: 상담 – 이수정 (컨설팅룸4)
• 17:30 – 18:00: 상담 – 신동준 (컨설팅룸4)
• 19:30 – 20:00: 상담 – 김관우 (컨설팅룸4)
• 20:00 – 20:30: 상담 – 황채영 (컨설팅룸4)
• 20:30 – 21:00: 상담 – 차지훈 (컨설팅룸4)
• 21:00 – 21:30: 상담 – 백은솔 (컨설팅룸4)
• 21:30 – 22:00: 상담 – 서지은 (컨설팅룸4)
'''

def main():
    database.create_tables()
    db = Session(bind=database.engine_sync)
    teachers, rooms, students, schedules = parse_schedule_text(schedule_text)
    # Insert teachers
    teacher_objs = {}
    for t, subj in teachers.items():
        obj = models.Teacher(name=t, subject=subj)
        db.add(obj)
        teacher_objs[t] = obj
    # Insert rooms
    room_objs = {}
    for r in rooms:
        obj = models.Room(name=r)
        db.add(obj)
        room_objs[r] = obj
    # Insert students
    student_objs = {}
    for s in students:
        obj = models.Student(name=s)
        db.add(obj)
        student_objs[s] = obj
    db.commit()
    # Insert schedules
    for sch in schedules:
        db.add(models.Schedule(
            teacher_id=teacher_objs[sch['teacher']].id,
            room_id=room_objs[sch['room']].id,
            student_id=student_objs[sch['student']].id,
            day_of_week=sch['day'],
            start_time=sch['start'],
            end_time=sch['end'],
            type=sch['type']
        ))
    db.commit()
    print("✅ 시간표 데이터가 성공적으로 입력되었습니다!")

if __name__ == '__main__':
    main()
