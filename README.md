# 🚀 FastAPI Car Rental Service (SpeedRide)

## 📌 Project Description
This project is a fully functional backend application built using FastAPI that simulates a real-world car rental system called **SpeedRide Car Rentals**.

The system allows users to browse cars, check availability, rent vehicles, and return them through well-structured REST APIs. It implements complete CRUD operations, real-world business logic, and advanced API features.

---

## 🎯 Features Implemented

### ✅ Day 1 – GET APIs
- Home route (`/`)
- Get all cars (`/cars`)
- Get car by ID (`/cars/{id}`)
- Car summary (`/cars/summary`)
- Get all rentals (`/rentals`)

---

### ✅ Day 2 – POST + Pydantic Validation
- Rental creation with validation
- Field constraints (min_length, gt, le)
- Error handling for invalid inputs

---

### ✅ Day 3 – Helper Functions
- `find_car()` → find car by ID  
- `find_rental()` → find rental by ID  
- `calculate_rental_cost()` → cost calculation with:
  - Discounts (7+ days → 15%, 15+ days → 25%)
  - Insurance cost (₹500/day)
  - Driver cost (₹800/day)
- `filter_cars_logic()` → filtering logic

---

### ✅ Day 4 – CRUD Operations
- POST `/cars` → add new car  
- PUT `/cars/{id}` → update car  
- DELETE `/cars/{id}` → delete car  
- Proper status codes (201, 404, 400)

---

### ✅ Day 5 – Multi-Step Workflow
- Rent car → POST `/rentals`
- View rental → GET `/rentals/{id}`
- Return car → POST `/return/{id}`
- Rental history → `/rentals/by-car/{car_id}`
- Active rentals → `/rentals/active`
- Unavailable cars → `/cars/unavailable`

---

### ✅ Day 6 – Advanced APIs
- Search → `/cars/search`
- Filter → `/cars/filter`
- Sort → `/cars/sort`
- Pagination → `/cars/page`
- Combined browsing → `/cars/browse`
- Rental search/sort/pagination

---

## 🛠️ Tech Stack
- FastAPI  
- Python  
- Pydantic  
- Uvicorn  

---

## ▶️ How to Run the Project

### 1. Clone the repository
```bash
git clone https://github.com/kartikpatade/fastapi-car-rental-service.git
cd fastapi-car-rental-service