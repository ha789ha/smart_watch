from datetime import datetime, timedelta
import requests
from database import Session, HeartRate
from config import access_token

headers = {
    'content-type': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

id = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"

def fetch_heart_rate_from_api(datasource_id, start_millis, end_millis, duration_millis):
    body = {
        "aggregateBy": [{"dataSourceId": datasource_id}],
        "bucketByTime": {"durationMillis": duration_millis},
        "startTimeMillis": start_millis,
        "endTimeMillis": end_millis
    }
    response = requests.post(
        'https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate',
        headers=headers, json=body
    )
    return response.json()

def get_hourly_heart_rate(datasource_id):
    session = Session()
    times, rates = [], []

    target_date = datetime.now().date()
    start_time = datetime.combine(target_date, datetime.min.time())
    end_time = datetime.now()

    start_millis = int(start_time.timestamp() * 1000)
    end_millis = int(end_time.timestamp() * 1000)

    data = fetch_heart_rate_from_api(datasource_id, start_millis, end_millis, 3600000)

    try:
        for bucket in data['bucket']:
            if bucket['dataset'][0]['point']:
                point = bucket['dataset'][0]['point'][0]['value']
                time_str = datetime.fromtimestamp(int(bucket['startTimeMillis']) / 1000).strftime('%H:%M')
                times.append(time_str)
                rates.append([point[0]['fpVal'], point[1]['fpVal'], point[2]['fpVal']])
    except KeyError:
        pass

    session.close()
    return times, rates

def get_heart_rate(datasource_id, days):
    session = Session()
    dates, rates = [], []

    for i in range(days):
        target_date = datetime.now().date() - timedelta(days=(days - 1 - i))
        db_record = session.query(HeartRate).filter(HeartRate.date == target_date).first()

        if db_record:
            heart_rate = [db_record.avg_rate, db_record.max_rate, db_record.min_rate]
            print(heart_rate)
        else:
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = start_time + timedelta(days=1)

            start_millis = int(start_time.timestamp() * 1000)
            end_millis = int(end_time.timestamp() * 1000)

            data = fetch_heart_rate_from_api(datasource_id, start_millis, end_millis, 86400000)

            try:
                figure = data['bucket'][0]['dataset'][0]['point'][0]['value']
                heart_rate = [figure[0]['fpVal'], figure[1]['fpVal'], figure[2]['fpVal']]
            except (KeyError, IndexError):
                heart_rate = [0, 0, 0]

            new_record = HeartRate(
                date=target_date,
                avg_rate=heart_rate[0],
                max_rate=heart_rate[1],
                min_rate=heart_rate[2]
            )

            session.add(new_record)
            session.commit()

        dates.append(target_date.strftime('%Y-%m-%d'))
        rates.append(heart_rate)

    session.close()
    return dates, rates

def get_daily_heart_rate(datasource_id):
    return get_heart_rate(datasource_id, 1)

def get_weekly_heart_rate(datasource_id):
    return get_heart_rate(datasource_id, 7)

def get_monthly_heart_rate(datasource_id):
    return get_heart_rate(datasource_id, 30)
