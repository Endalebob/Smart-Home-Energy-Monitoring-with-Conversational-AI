# Smart Home Energy Monitoring with Conversational AI

A full-stack application for monitoring smart home energy usage, featuring a conversational AI assistant, real-time dashboard, and device management.

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Endalebob/Smart-Home-Energy-Monitoring-with-Conversational-AI.git
cd Smart-Home-Energy-Monitoring-with-Conversational-AI
```

### 2. Create Your Environment File
Copy the example environment file and set your OpenAI API key:
```bash
cp env_example.txt .env
# Edit .env and set your OPENAI_API_KEY
```
- **OPENAI_API_KEY** is required for the AI chat assistant to work.

### 3. Start the App with Docker
```bash
docker-compose up --build
```
- This will start **FastAPI** backend (port **8000**) and **Next.js** frontend (port **3000**).

### 4. Access the Application
- **Backend API (FastAPI):** [http://localhost:8000](http://localhost:8000)
- **API Docs:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend (Next.js):** [http://localhost:3000](http://localhost:3000)

### 5. Default Admin User
On first run, the app automatically creates an admin user:
- **Email:** `admin@smart-home.com`
- **Password:** `admin123`

You can log in with these credentials immediately after startup.

### 6. Populate with Sample Data (Recommended)
To see the dashboard and AI chat in action, run:
```bash
python simulate_telemetry.py
```
- This will create sample devices and 24 hours of telemetry data.

---

## 🏠 What Can You Do?
- **Dashboard:** Visualize your home's energy usage in real time
- **Device Management:** Add, edit, and remove smart devices
- **Conversational AI:** Ask natural language questions about your energy usage
- **Authentication:** Secure login/register system

---

## ⚡ API Endpoints
- `POST /api/auth/register` — User registration
- `POST /api/auth/login` — User login
- `GET /api/auth/me` — Get current user info
- `POST /api/devices/` — Create device
- `GET /api/devices/` — List user devices
- `GET /api/telemetry/summary` — Energy usage summary
- `POST /api/chat/query` — AI chat interface

---

## 🛠️ Requirements
- **Backend:** Python 3.9+, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** Node.js 18+, Next.js, React, TypeScript
- **Database:** PostgreSQL 15

---

## 💡 Tips
- Make sure your `.env` file is present and contains a valid `OPENAI_API_KEY` for chat features.
- You can customize database and API settings in `.env` as needed.
- For development, you can run backend and frontend separately (see comments in the file).

---

Enjoy your smart home energy dashboard! 🎉 
