## 프로젝트 주제
- 건강상태 분석을 위한 스마트워치 데이터 분석 Chatbot
<br>

## 프로젝트 목표
- 스마트워치에서 신체/건강 데이터 수집 및 분석 기능 개발
- 데이터를 기반으로 한 RAG Chatbot 개발

<br>

## 환경 설정
1. Python = 3.10.15
2. Git으로 Repository 클론
```shell
git clone https://github.com/ha789ha/smart_watch.git
cd smart_watch
```
3. Python Requirements 설치
```shell
pip install -r requirements
```
4. config.py
```shell
access_token = "your google cloud api access token"
```  
4. app.py 실행
```shell
python app.py
``` 
<br>

## 아키텍처 구조

![아키텍쳐1](https://github.com/user-attachments/assets/14035666-bfd0-476e-8f53-ae047cfbee7f)

<br>

## 프로젝트 사용 모델
- [Llama3-korean-blossom-8B](https://huggingface.co/MLP-KTLim/llama-3-Korean-Bllossom-8B)
- [klue-sroberta-base-continue-learning-by-mnr](https://huggingface.co/bespin-global/klue-sroberta-base-continue-learning-by-mnr)
<br>


