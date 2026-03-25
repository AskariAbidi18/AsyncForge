# AsyncForge

AsyncForge is a distributed task processing system built in Python, designed to handle asynchronous workloads using a queue-based architecture.

It combines Redis for fast task queuing and PostgreSQL as the source of truth to ensure reliable task execution, retries, and state management.

---

## 🚀 Overview

AsyncForge enables clients to submit tasks that are processed asynchronously by worker processes.

Core flow:

Client/API  
→ Task creation  
→ PostgreSQL (persistent storage)  
→ Redis queue (transport)  
→ Worker execution  
→ Status update  

---

## ⚙️ Key Features

- **Asynchronous task execution** using worker-based architecture  
- **Redis-backed queue system** (LPUSH / BRPOP) for efficient task distribution  
- **PostgreSQL persistence** as the single source of truth  
- **Retry system with delayed execution** using Redis Sorted Sets (ZSET)  
- **Task-level locking** to prevent duplicate execution  
- **Pluggable task handlers** for flexible execution logic  
- **Modular architecture** with clear separation of concerns  

---

## 🧱 Architecture

### Core Components

#### 1. API Layer
- Handles task creation, status retrieval, and listing
- Thin layer delegating logic to services

#### 2. Service Layer
- Central control unit
- Handles validation, task creation, queueing, and updates

#### 3. Database (PostgreSQL)
- Stores all task metadata and state
- Acts as the **source of truth**

#### 4. Queue System (Redis)

- **Main Queue**  
  `LPUSH` → producer  
  `BRPOP` → worker  

- **Retry Queue (ZSET)**  
  Used for delayed retries based on timestamps  

- **Lock System**  
  Prevents duplicate execution using TTL-based locks  

#### 5. Worker System

- Pulls tasks from Redis  
- Fetches task data from PostgreSQL  
- Executes handlers  
- Updates task status  

Task lifecycle:
# AsyncForge

AsyncForge is a distributed task processing system built in Python, designed to handle asynchronous workloads using a queue-based architecture.

It combines Redis for fast task queuing and PostgreSQL as the source of truth to ensure reliable task execution, retries, and state management.

---

## 🚀 Overview

AsyncForge enables clients to submit tasks that are processed asynchronously by worker processes.

Core flow:

Client/API  
→ Task creation  
→ PostgreSQL (persistent storage)  
→ Redis queue (transport)  
→ Worker execution  
→ Status update  

---

## ⚙️ Key Features

- **Asynchronous task execution** using worker-based architecture  
- **Redis-backed queue system** (LPUSH / BRPOP) for efficient task distribution  
- **PostgreSQL persistence** as the single source of truth  
- **Retry system with delayed execution** using Redis Sorted Sets (ZSET)  
- **Task-level locking** to prevent duplicate execution  
- **Pluggable task handlers** for flexible execution logic  
- **Modular architecture** with clear separation of concerns  

---

## 🧱 Architecture

### Core Components

#### 1. API Layer
- Handles task creation, status retrieval, and listing
- Thin layer delegating logic to services

#### 2. Service Layer
- Central control unit
- Handles validation, task creation, queueing, and updates

#### 3. Database (PostgreSQL)
- Stores all task metadata and state
- Acts as the **source of truth**

#### 4. Queue System (Redis)

- **Main Queue**  
  `LPUSH` → producer  
  `BRPOP` → worker  

- **Retry Queue (ZSET)**  
  Used for delayed retries based on timestamps  

- **Lock System**  
  Prevents duplicate execution using TTL-based locks  

#### 5. Worker System

- Pulls tasks from Redis  
- Fetches task data from PostgreSQL  
- Executes handlers  
- Updates task status  

Task lifecycle:
PENDING → RUNNING → COMPLETED
↓
FAILED → RETRY → DEAD


---

## 🔁 Retry Mechanism

- Failed tasks increment retry count  
- If retries remain:
  - Task is pushed to Redis ZSET with delay  
- Retry worker moves tasks back to main queue when ready  

---

## 📁 Project Structure

AsyncForge/
│
├── worker.py
├── test_run.py
│
└── app/
├── config.py
├── database.py
├── redis_client.py
│
├── api/
│ └── tasks.py
│
├── models/
│ └── task.py
│
├── schemas/
│ └── task.py
│
├── services/
│ └── task_service.py
│
├── queue/
│ ├── producer.py
│ ├── consumer.py
│ └── retry_queue.py
│
├── workers/
│ ├── worker.py
│ ├── handlers.py
│ └── retry_worker.py
│
└── utils/
├── constants.py
└── time.py


---

## 🧠 Design Principles

- **Separation of concerns**  
  API ≠ business logic ≠ execution  

- **Redis as transport, not storage**  
  Keeps system fast and stateless  

- **PostgreSQL as source of truth**  
  Ensures consistency and recoverability  

- **Stateless workers**  
  Enables horizontal scaling  

---

## ⚠️ Notes

- AsyncForge is designed as a **learning and experimental system** inspired by distributed task queues (e.g., Celery)  
- Focus is on understanding system design, reliability, and async processing  
- Not intended as a production-ready replacement (yet)

---

## 🚀 Future Improvements

- Task prioritization  
- Monitoring and dashboard  
- Distributed worker scaling  
- Dead-letter queue management UI  

---

## 👨‍💻 Author

Askari Abidi

---

## 📌 Summary

AsyncForge is a modular distributed task processing system that:

- Uses Redis for queuing and PostgreSQL for persistence  
- Supports retries, delayed execution, and fault tolerance  
- Demonstrates core backend and system design principles  
