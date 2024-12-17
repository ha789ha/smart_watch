import os
from llm import HealthLLM
from flask import Flask, jsonify, render_template, request
from heart_rate import (
    get_weekly_heart_rate, 
    get_daily_heart_rate, 
    get_monthly_heart_rate, 
    get_hourly_heart_rate,  # 추가
    id as heart_rate_id
)
from step_count import get_weekly_steps, get_daily_steps, get_monthly_steps, id as steps_id
from heart_score import get_daily_heart_points, get_weekly_heart_points, get_monthly_heart_points, id as heart_points_id


app = Flask(__name__)

health_llm = HealthLLM('health_data.db')

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/daily_stats")
def daily_stats():
    _, steps = get_daily_steps(steps_id)
    _, heart_points = get_daily_heart_points(heart_points_id)
    return jsonify({
        "steps": steps[0] if steps else 0,
        "heart_points": heart_points[0] if heart_points else 0
    })

@app.route("/api/hourly_heart_rate")
def hourly_heart_rate():
    times, rates = get_hourly_heart_rate(heart_rate_id)
    return jsonify({"times": times, "rates": rates})

@app.route("/api/heart_rate/<period>")
def heart_rate(period):
    if period == 'daily':
        dates, rates = get_daily_heart_rate(heart_rate_id)
    elif period == 'weekly':
        dates, rates = get_weekly_heart_rate(heart_rate_id)
    else:
        dates, rates = get_monthly_heart_rate(heart_rate_id)
    return jsonify({"dates": dates, "rates": rates})

@app.route("/api/steps/<period>")
def steps(period):
    if period == 'daily':
        dates, steps = get_daily_steps(steps_id)
    elif period == 'weekly':
        dates, steps = get_weekly_steps(steps_id)
    else:
        dates, steps = get_monthly_steps(steps_id)
    return jsonify({"dates": dates, "steps": steps})

@app.route("/api/heart_points/<period>")
def heart_points(period):
    if period == 'daily':
        dates, points = get_daily_heart_points(heart_points_id)
    elif period == 'weekly':
        dates, points = get_weekly_heart_points(heart_points_id)
    else:
        dates, points = get_monthly_heart_points(heart_points_id)
        
    return jsonify({"dates": dates, "heart_points": points})

@app.route("/chat", methods=['POST'])
def chat():
    message = request.json['message']
    response, history = health_llm.generate_response(message)
    return jsonify({
        "response": response,
        "history": history  # 히스토리도 함께 반환
    })

if __name__ == "__main__":
    app.run(debug=True)
    
    
