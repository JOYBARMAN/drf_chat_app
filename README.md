# 💬 Real-Time Chat System (Django + WebSockets)

🚀 A **scalable real-time chat application** built with **Django, Django REST Framework, and WebSockets**, designed to handle concurrent users with persistent messaging and production-ready architecture.

---

## 🧠 Overview

This project demonstrates how to build a **real-time communication system** using modern backend patterns.
It supports **instant messaging, authentication, and scalable architecture design** suitable for SaaS applications.

---

## ⚙️ Tech Stack

**Backend:**

* Django
* Django REST Framework
* Django Channels (WebSockets)

**Database:**

* PostgreSQL (recommended)

**Caching / Realtime Layer:**

* Redis (for channel layer & pub/sub)

**Other Tools:**

* Docker (optional)
* Git

---

## 🏗️ System Architecture

This application follows a **service-oriented backend architecture**:

* REST APIs handle **authentication & data operations**
* WebSockets handle **real-time bidirectional communication**
* Redis acts as a **message broker for scaling WebSocket connections**

### 🔄 Flow

1. User authenticates via REST API
2. Client connects to WebSocket endpoint
3. Messages are sent/received in real-time
4. Data is persisted in the database
5. Redis ensures scalability across multiple instances

---

## 🔥 Features

* 💬 Real-time messaging using WebSockets
* 🔐 Token-based authentication (JWT/session-based)
* 🧾 Persistent chat history
* 👥 Multi-user support
* ⚡ Low-latency communication
* 📦 Scalable architecture using Redis
* 🧩 Clean and modular backend structure

---

## 📂 Project Structure

```
drf_chat_app/
│── apps/
│   ├── chat/
│   ├── users/
│── config/
│── requirements/
│── manage.py
```

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```
git clone https://github.com/JOYBARMAN/drf_chat_app.git
cd drf_chat_app
```

---

### 2️⃣ Create virtual environment

```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Setup environment variables

Create a `.env` file and configure:

```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
REDIS_URL=redis://localhost:6379
```

---

### 5️⃣ Run migrations

```
python manage.py migrate
```

---

### 6️⃣ Start Redis

```
redis-server
```

---

### 7️⃣ Run the server

```
python manage.py runserver
```

---

## 🔌 WebSocket Endpoint

```
ws://localhost:8000/ws/chat/
```

---

## 📸 Demo (Optional)

*Add screenshots or GIFs here to showcase real-time messaging*

---

## 📈 Scalability & Improvements

* Deploy with **ASGI server (Daphne / Uvicorn)**
* Use **Redis Cluster** for large-scale systems
* Add **message queues (Celery)** for background jobs
* Implement **read receipts & typing indicators**
* Horizontal scaling with **load balancers**

---

## 🧪 Testing

* Unit testing with `pytest`
* Integration testing for API & WebSocket flows

---

## 🧩 Use Cases

* SaaS chat systems
* Customer support platforms
* Real-time collaboration tools
* Messaging backends for mobile/web apps

---

## 📫 Author

**Joy Barman**

* GitHub: https://github.com/JOYBARMAN
* LinkedIn: https://linkedin.com/in/joy-barman/

---

## ⚡

> “Real-time systems are not just about speed — they are about consistency, scalability, and reliability.”

---

⭐ If you find this useful, consider giving it a star!
