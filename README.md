# Real-Time Financial Data & Prediction Platform

A **cloud-based, real-time financial monitoring and alerting platform** that streams live market data, allows user-defined alerts, and uses machine learning to predict price trends.  

This project demonstrates **full-stack development, distributed systems, cloud infrastructure, and applied machine learning** in a unified platform.

---

## **Table of Contents**
- [Features](#features)
- [Architecture](#architecture)
- [Microservices](#microservices)
- [API Endpoints](#api-endpoints)
- [Data Sources](#data-sources)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [License](#license)

---

## **Features**

### User Features
- Register and login  
- Skip authentication to quickly view charts  
- View live prices for selected assets (BTC, ETH, AAPL, SPY)  
- Create, edit, and delete alerts  
- Receive notifications via web push or email  
- See AI-based short-term price predictions  
- Add assets to favorites  

### System Features
- Fetch historical and real-time market data  
- Stream live data via WebSocket  
- Evaluate user-defined alerts and trigger notifications  
- Predict prices using ML models  
- Cache latest data for fast retrieval  

---

## **Architecture**

**Microservices:**
- **User Service:** Handles authentication, user profiles, and alert configurations  
- **Ingestion Service:** Fetches historical data (REST) and streams real-time prices (WebSockets), caches data in Redis  
- **Alerting Service:** Evaluates alert conditions, sends messages to the queue  
- **Notification Service:** Sends web push notifications and emails  
- **ML Prediction Service:** Trains and serves prediction models  

**Databases & Cache:**
- PostgreSQL for user & alert storage  
- Redis for caching latest market prices  

**Communication:**
- REST for CRUD operations  
- WebSockets for live streaming  
- Message Queue (SQS/RabbitMQ) for asynchronous alert processing  

---
## **API Endpoints**

### **User Service**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/users/register` | Create new account |
| POST   | `/api/users/login` | Authenticate user, returns JWT |
| GET    | `/api/users/profile` | Get user info (auth required) |
| GET    | `/api/users/favorites` | Get favorite assets (auth required) |
| POST   | `/api/users/favorites/:id` | Add asset to favorites (auth required) |
| DELETE | `/api/users/favorites/:id` | Remove asset from favorites (auth required) |

### **Ingestion Service**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/data/:symbol/historical` | Get historical data for a symbol from cache |
| WS     | `/ws/stream` | Live stream of BTC, ETH, AAPL, SPY prices |

### **Alerting Service**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/alerts` | Get all alerts for user |
| POST   | `/api/alerts` | Create new alert |
| PUT    | `/api/alerts/:id` | Edit alert |
| DELETE | `/api/alerts/:id` | Delete alert |

### **ML Prediction Service**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/predict?symbol=` | Get latest price prediction |
| POST   | `/api/train?symbol=` | Trigger manual retraining of model |
| GET    | `/api/models` | Retrieve model metadata/performance |

---

## **Data Sources**
| Asset | Source | Type | Update Frequency |
|-------|--------|------|-----------------|
| BTC / ETH | Binance | WebSocket (real-time) | 5s |
| AAPL / SPY | Alpha Vantage | REST polling | 25s |

- **Historical data:** fetched via REST endpoints  
- **Real-time data:** streamed via WebSocket (Binance) or polling (Alpha Vantage)  
- **Caching:** Redis stores latest points to reduce wait times  

---

## **Tech Stack**
- **Backend:** Python, FastAPI, Uvicorn  
- **Frontend:** React (dashboard, charts, alerts)  
- **Database:** PostgreSQL  
- **Cache:** Redis (local for free-tier MVP)  
- **Messaging Queue:** AWS SQS / RabbitMQ (async alerts)  
- **Machine Learning:** LSTM / Prophet (for price predictions)  
- **Cloud / Deployment:** AWS ECS, SES (email), CloudWatch (monitoring)  
- **Version Control:** Git + GitHub  

---

## **Setup**
1. Clone the repo:
```bash
git clone https://github.com/username/financial-monitor.git
cd financial-monitor
```

2. Create a virtual environment for each service:
```bash
cd services/user-service
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Copy .env.example to .env and fill in your API keys and secrets

4. Run FastAPI server:
```bash
uvicorn app:app --reload
```