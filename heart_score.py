from database import init_db
from datetime import datetime, timedelta
import requests
from database import Session, HeartPoints
from config import access_token

headers = {
    'content-type': 'application/json',
    'Authorization': 'Bearer %s' % access_token
}

# Heart Points 데이터 소스 ID
id = "derived:com.google.heart_minutes:com.google.android.gms:merge_heart_minutes"

def get_heart_points(datasource_id, days):
    session = Session()
    dates, heart_points = [], []  # heart_points 리스트 초기화
    
    for i in range(days):
        target_date = datetime.now().date() - timedelta(days=(days - 1 - i))
        # DB에서 데이터 확인
        db_record = session.query(HeartPoints).filter(HeartPoints.date == target_date).first()
        
        if db_record:
            heart_point = db_record.points
        else:
            # API에서 데이터 가져오기
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = start_time + timedelta(days=1)
            start_millis = int(start_time.timestamp() * 1000)
            end_millis = int(end_time.timestamp() * 1000)

            body = {
                "aggregateBy": [{"dataSourceId": datasource_id}],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_millis,
                "endTimeMillis": end_millis
            }

            response = requests.post(
                'https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate',
                headers=headers, json=body
            )

            data = response.json()
            try:
                heart_point = data['bucket'][0]['dataset'][0]['point'][0]['value'][0]['fpVal']  # HeartPoints 값 추출
                # DB에 저장
                new_record = HeartPoints(date=target_date, points=heart_point)
                session.add(new_record)
                session.commit()
            except (KeyError, IndexError):
                heart_point = 0  # HeartPoints 값이 없으면 기본값 0 설정

        dates.append(target_date.strftime('%Y-%m-%d'))
        heart_points.append(heart_point)
    
    session.close()
    return dates, heart_points

def get_daily_heart_points(datasource_id):
    return get_heart_points(datasource_id, 1)

def get_weekly_heart_points(datasource_id):
    return get_heart_points(datasource_id, 7)

def get_monthly_heart_points(datasource_id):
    return get_heart_points(datasource_id, 30)

