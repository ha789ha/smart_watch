import sqlite3
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime

class HealthLLM:
    def __init__(self, db_path='health_data.db'):
        # LLM 모델 초기화
        self.model_name = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map='cuda'
        )
        self.model.eval()
        
        # 임베딩 모델 초기화 (RAG를 위한)
        self.embedding_model = SentenceTransformer('bespin-global/klue-sroberta-base-continue-learning-by-mnr')
        
        # 데이터베이스 연결 및 데이터 로드
        self.connect_to_database(db_path)
        
        # 초기 시스템 프롬프트
        self.system_prompt = {
            "role": "system",
            "content": """너는 헬스 및 건강 관련 정보를 제공하는 지능형 챗봇이야. 제공된 데이터를 바탕으로 정확하고 유용한 답변을 '반드시' 한국어로 제공해. 다만, 데이터에 관한 내용이 아니면 일상적인 대화를 해도 좋아. 또한 답변은 항상 간결하게 한문장 정도로 도출하도록 해."""
        }
        
        self.conversation_history = [self.system_prompt]
    
    def connect_to_database(self, db_path):
        """SQLite 데이터베이스 연결 및 데이터 로드"""
        try:
            # 데이터베이스 연결
            self.conn = sqlite3.connect(db_path)
            
            # 모든 테이블의 데이터를 로드하고 임베딩
            self.load_and_embed_data()
        except sqlite3.Error as e:
            print(f"데이터베이스 연결 중 오류 발생: {e}")
            self.conn = None
            self.embeddings = None
    
    def load_and_embed_data(self):
        """데이터베이스에서 모든 테이블 데이터 로드 및 임베딩"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        all_texts = []
        
        # 걸음수 데이터 처리
        cursor.execute("SELECT date, steps FROM step_counts ORDER BY date DESC")
        steps_data = cursor.fetchall()
        steps_text = "걸음수_데이터: " + ", ".join([
            f"{date} ({datetime.strptime(date, '%Y-%m-%d').strftime('%A')}) {steps}걸음" 
            for date, steps in steps_data
        ])
        all_texts.append(steps_text)
        
        # 심박수 데이터 처리
        cursor.execute("""
            SELECT date, avg_rate, max_rate, min_rate 
            FROM heart_rates 
            WHERE avg_rate > 0 
            ORDER BY date DESC 
        """)
        heart_data = cursor.fetchall()
        heart_text = "심박수_데이터: " + ", ".join([
            f"{date} ({datetime.strptime(date, '%Y-%m-%d').strftime('%A')}) 평균심박수 {avg:.2f} 최대심박수 {max_} 최소심박수 {min_}"
            for date, avg, max_, min_ in heart_data
        ])
        all_texts.append(heart_text)
        
        # 심장강화점수 데이터 처리
        cursor.execute("SELECT date, points FROM heart_points ORDER BY date DESC")
        points_data = cursor.fetchall()
        points_text = "심장강화점수_데이터: " + ", ".join([
            f"{date} ({datetime.strptime(date, '%Y-%m-%d').strftime('%A')}) {points}점" 
            for date, points in points_data
        ])
        all_texts.append(points_text)
        
        # 텍스트 임베딩 생성
        self.embeddings = self.embedding_model.encode(all_texts)
        self.texts = all_texts

    def retrieve_relevant_context(self, query, top_k=3):
        """쿼리와 가장 관련성 높은 컨텍스트 검색"""
        if self.embeddings is None:
            return ""
        
        # 쿼리 임베딩
        query_embedding = self.embedding_model.encode([query])[0]
        
        # 코사인 유사도 계산
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # 상위 k개 관련 문서 선택
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # 관련 컨텍스트 추출
        retrieved_contexts = [self.texts[idx] for idx in top_indices]
        
        return "\n".join(retrieved_contexts)
    
    def generate_response(self, user_input, history=None):     
        # 관련 컨텍스트 검색
        relevant_context = self.retrieve_relevant_context(user_input)
        
        # 시스템 프롬프트 업데이트
        system_content = f"""너는 헬스 및 건강 관련 정보를 제공하는 지능형 챗봇이야. 제공된 데이터를 바탕으로 정확하고 유용한 답변을 '반드시' 한국어로 제공해. 다만, 데이터에 관한 내용이 아니면 일상적인 대화를 해도 좋아. 또한 답변은 항상 간결하게 한문장 정도로 도출하도록 해.
        - 오늘은 {datetime.today()}이야. 이를 기준으로 항상 대답하도록해, 관련 정보를 볼 때 반드시 참고해 오늘이 며칠인지
        - 심장강화점수는 심박수나 움직임이 높아지면 좋아지는 점수야. 
        - 아래 표시되는 관련 정보는 심박수, 걸음 수, 심장강화점수에 대한 일 별 데이터를 모아놓은 거야. 
        - 분석할 때는 주어진 기간의 최대, 최소, 평균 수치와 특이점 등을 간략하게 말하면 돼
        - 관련 정보:
        {relevant_context}
        """
        
        # 대화 히스토리 재구성
        self.conversation_history[0]['content'] = system_content
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # 대화 템플릿 적용
        text = self.tokenizer.apply_chat_template(
            self.conversation_history,
            add_generation_prompt=True,
            return_tensors='pt'
        ).to(self.model.device)
        
        terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        
        # 응답 생성
        generated_ids = self.model.generate(
            text,
            max_new_tokens=512,
            eos_token_id=terminators,
            temperature=0.2
        )
        
        # 응답 디코딩
        response = self.tokenizer.decode(generated_ids[0][text.shape[-1]:], skip_special_tokens=True)
        
        # 대화 히스토리에 응답 추가
        self.conversation_history.append({"role": "assistant", "content": response})

        return response, self.conversation_history
    
    def __del__(self):
        # 데이터베이스 연결 종료
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
