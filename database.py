from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base 및 엔진 설정
Base = declarative_base()
engine = create_engine('sqlite:///health_data.db')
Session = sessionmaker(bind=engine)

# StepCount 모델
class StepCount(Base):
    __tablename__ = 'step_counts'
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    steps = Column(Integer)

# HeartRate 모델
class HeartRate(Base):
    __tablename__ = 'heart_rates'
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    avg_rate = Column(Float)
    max_rate = Column(Float)
    min_rate = Column(Float)

# HeartPoints 모델 추가
class HeartPoints(Base):
    __tablename__ = 'heart_points'
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    points = Column(Float)  # Heart Points 값

# 데이터베이스 초기화 함수
def init_db():
    Base.metadata.create_all(engine)
