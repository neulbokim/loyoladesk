# --- 필요한 라이브러리 설치 ---
# 터미널(명령 프롬프트)에서 아래 명령어를 실행해주세요.
# pip install Flask Flask-Cors

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json

# --- Flask 애플리케이션 생성 ---
app = Flask(__name__)

# --- CORS 설정 ---
# 다른 주소(GitHub Pages)에서 오는 요청을 허용하기 위해 반드시 필요합니다.
CORS(app)

# --- 데이터베이스 초기 설정 ---
def init_db():
    """데이터베이스 파일을 생성하고, 필요한 테이블을 만듭니다."""
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # 학생별 근무 가능 시간 저장 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            day INTEGER NOT NULL,
            time TEXT NOT NULL,
            type TEXT NOT NULL 
        )
    ''')
    
    # 학생별 수업 시간 저장 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_class_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            day INTEGER NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# --- API 엔드포인트 생성 ---
# 이 주소로 학생들이 제출한 데이터가 전송됩니다.
@app.route('/api/submit-schedule', methods=['POST'])
def submit_schedule():
    """학생들이 제출한 시간표 데이터를 받아 처리합니다."""
    
    # 1. 전송된 데이터 받기
    try:
        data = request.get_json()
        student_id = data.get('studentId')
        availability = data.get('availability', [])
        class_schedule = data.get('classSchedule', [])

        if not student_id:
            # 학번이 없는 경우 에러 처리
            return jsonify({"status": "error", "message": "학번이 필요합니다."}), 400

    except Exception as e:
        print(f"데이터 수신 오류: {e}")
        return jsonify({"status": "error", "message": "잘못된 요청 형식입니다."}), 400

    # 2. 받은 데이터를 터미널에 출력 (확인용)
    print("\n--- 새로운 데이터 수신 ---")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 3. 데이터베이스에 저장
    try:
        conn = sqlite3.connect('schedule.db')
        cursor = conn.cursor()
        
        # 이전 데이터 삭제 (선택적): 동일한 학생이 다시 제출할 경우, 이전 기록을 지웁니다.
        cursor.execute("DELETE FROM student_availability WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM student_class_schedule WHERE student_id = ?", (student_id,))

        # 근무 가능/희망 시간 저장
        for item in availability:
            cursor.execute(
                "INSERT INTO student_availability (student_id, day, time, type) VALUES (?, ?, ?, ?)",
                (student_id, item['day'], item['time'], item['type'])
            )
            
        # 수업 시간 저장
        for item in class_schedule:
            cursor.execute(
                "INSERT INTO student_class_schedule (student_id, day, time) VALUES (?, ?, ?)",
                (student_id, item['day'], item['time'])
            )
            
        conn.commit()
        conn.close()
        
        print(f"성공: {student_id} 학생의 데이터를 데이터베이스에 저장했습니다.")

    except Exception as e:
        print(f"데이터베이스 저장 오류: {e}")
        return jsonify({"status": "error", "message": "데이터베이스 처리 중 오류가 발생했습니다."}), 500

    # 4. 성공 응답 보내기
    return jsonify({"status": "success", "message": "데이터가 성공적으로 처리되었습니다."})


# --- 서버 실행 ---
if __name__ == '__main__':
    init_db() # 서버 시작 시 데이터베이스 초기화
    # host='0.0.0.0'은 내 컴퓨터의 어떤 주소로든 접속을 허용한다는 의미입니다.
    app.run(host='0.0.0.0', port=5000, debug=True)
