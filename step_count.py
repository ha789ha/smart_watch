from datetime import datetime, timedelta
import requests
from database import Session, StepCount
from config import access_token

headers = {
    'content-type': 'application/json',
    'Authorization': 'Bearer %s' % access_token
}

id = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"

def get_steps(datasource_id, days):
    session = Session()
    dates, steps = [], []
    
    for i in range(days):
        target_date = datetime.now().date() - timedelta(days=(days - 1 - i))
        
        # DB에서 데이터 확인
        db_record = session.query(StepCount).filter(StepCount.date == target_date).first()
        
        if db_record:
            step_count = db_record.steps


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
            print(data)
            try:
                step_count = data['bucket'][0]['dataset'][0]['point'][0]['value'][0]['intVal']
                # DB에 저장
                new_record = StepCount(date=target_date, steps=step_count)
                session.add(new_record)
                session.commit()
            except:
                step_count = 0

        dates.append(target_date.strftime('%Y-%m-%d'))
        steps.append(step_count)
    
    session.close()
    return dates, steps

def get_daily_steps(datasource_id):
    return get_steps(datasource_id, 1)

def get_weekly_steps(datasource_id):
    return get_steps(datasource_id, 7)

def get_monthly_steps(datasource_id):
    return get_steps(datasource_id, 30)