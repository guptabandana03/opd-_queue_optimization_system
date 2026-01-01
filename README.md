# 🏥 OPD Queue Optimization System

A Flask-based web application designed to optimize OPD (Out Patient Department) queues by intelligently prioritizing patients based on **emergency level, age, and fairness**, while ensuring transparency for patients and doctors.

---

## 📌 Problem Statement

In traditional OPD systems:
- Patients wait indefinitely without clarity
- Emergency cases disrupt fairness
- Doctors manually decide whom to serve next
- Patients do not know their real position in queue

This project solves these issues by implementing a **smart, rule-based queue optimization system**.

---

## 🎯 Key Features

### 👤 Patient Interface
- Patient registration with auto-generated token number
- Status check using token number
- Estimated waiting time display

### 🩺 Doctor Dashboard
- View next highest-priority patient
- Serve patients with one click
- Emergency override support
- Fair handling of old vs new emergency cases

### 📺 Display Screen (Public View)
- Live queue display
- Estimated waiting time for each patient
- Automatic updates as queue changes

### ⚙️ Backend Logic
- Priority-based queue calculation
- Emergency throttling logic
- Fairness ensured using token gap
- SQLite database integration

---

## 🧠 Queue Prioritization Logic

Each patient is assigned a **priority score** based on:

| Factor | Rule |
|-----|-----|
Emergency (New) | +5 |
Emergency (Old) | +3 |
Normal Visit | +1 |
Waiting too long (token gap ≥ 5) | +2 |
Senior Citizen (≥60) or Child (≤10) | +1 |

👉 Queue is sorted by:
1. Higher priority score  
2. Lower token number (fairness)

---

## 🏗️ System Architecture
                   
                   
                    Patient Interface 
                           │ 
                           ▼
Doctor Dashboard  ──▶Flask Backend ──▶ Display Screen
                          │  ↑
                          ▼  │ 
                      SQLite Database
│
## 🛠️ Tech Stack

Backend: Python, Flask

Database: SQLite

Frontend: HTML, CSS, Jinja2

Deployment: Render (Gunicorn)

## 👩‍💻 Author

Bandana Gupta  
B.Tech CSE, Kalinga University