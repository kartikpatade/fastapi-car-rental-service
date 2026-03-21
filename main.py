from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()


# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────

cars = [
    {"id": 1, "model": "Swift",     "brand": "Maruti",  "type": "Hatchback", "price_per_day": 800,  "fuel_type": "Petrol",  "is_available": True},
    {"id": 2, "model": "City",      "brand": "Honda",   "type": "Sedan",     "price_per_day": 1200, "fuel_type": "Petrol",  "is_available": True},
    {"id": 3, "model": "Creta",     "brand": "Hyundai", "type": "SUV",       "price_per_day": 1800, "fuel_type": "Diesel",  "is_available": True},
    {"id": 4, "model": "Nexon",     "brand": "Tata",    "type": "SUV",       "price_per_day": 1500, "fuel_type": "Electric", "is_available": True},
    {"id": 5, "model": "Camry",     "brand": "Toyota",  "type": "Luxury",    "price_per_day": 3000, "fuel_type": "Petrol",  "is_available": False},
    {"id": 6, "model": "Baleno",    "brand": "Maruti",  "type": "Hatchback", "price_per_day": 900,  "fuel_type": "Petrol",  "is_available": True},
]

rentals        = []
rental_counter = 1


# ─────────────────────────────────────────────
#  PYDANTIC MODELS
# ─────────────────────────────────────────────

class RentalRequest(BaseModel):
    customer_name:  str  = Field(..., min_length=2)
    car_id:         int  = Field(..., gt=0)
    days:           int  = Field(..., gt=0, le=30)
    license_number: str  = Field(..., min_length=8)
    insurance:      bool = False
    driver_required: bool = False


class NewCar(BaseModel):
    model:        str  = Field(..., min_length=2)
    brand:        str  = Field(..., min_length=2)
    type:         str  = Field(..., min_length=2)
    price_per_day: int = Field(..., gt=0)
    fuel_type:    str  = Field(..., min_length=2)
    is_available: bool = True


# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────

def find_car(car_id: int):
    for c in cars:
        if c["id"] == car_id:
            return c
    return None


def find_rental(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            return r
    return None


def calculate_rental_cost(price_per_day: int, days: int, insurance: bool, driver_required: bool):
    base_cost = price_per_day * days

    if days >= 15:
        discount_pct = 25
    elif days >= 7:
        discount_pct = 15
    else:
        discount_pct = 0

    discount_amount = int(base_cost * discount_pct / 100)
    after_discount  = base_cost - discount_amount

    insurance_cost = 500 * days if insurance else 0
    driver_cost    = 800 * days if driver_required else 0

    total = after_discount + insurance_cost + driver_cost

    return {
        "base_cost":       base_cost,
        "discount_pct":    discount_pct,
        "discount_amount": discount_amount,
        "insurance_cost":  insurance_cost,
        "driver_cost":     driver_cost,
        "total_cost":      total,
    }


def filter_cars_logic(type=None, brand=None, fuel_type=None, max_price=None, is_available=None):
    result = cars[:]
    if type is not None:
        result = [c for c in result if c["type"] == type]
    if brand is not None:
        result = [c for c in result if c["brand"].lower() == brand.lower()]
    if fuel_type is not None:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]
    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]
    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]
    return result


# ═════════════════════════════════════════════
#  DAY 1 — Q1   Home Route
# ═════════════════════════════════════════════

@app.get("/")
def home():
    return {"message": "Welcome to SpeedRide Car Rentals"}


# ═════════════════════════════════════════════
#  DAY 1 — Q2   Get All Cars
# ═════════════════════════════════════════════

@app.get("/cars")
def get_all_cars():
    available_count = len([c for c in cars if c["is_available"]])
    return {"cars": cars, "total": len(cars), "available_count": available_count}


# ═════════════════════════════════════════════
#  DAY 1 — Q4   Get All Rentals
# ═════════════════════════════════════════════

@app.get("/rentals")
def get_all_rentals():
    return {"rentals": rentals, "total": len(rentals)}


# ═════════════════════════════════════════════
#  DAY 1 — Q5   Car Summary  (above /{car_id})
# ═════════════════════════════════════════════

@app.get("/cars/summary")
def car_summary():
    available = [c for c in cars if c["is_available"]]
    type_breakdown      = {}
    fuel_breakdown      = {}
    for c in cars:
        type_breakdown[c["type"]]      = type_breakdown.get(c["type"], 0) + 1
        fuel_breakdown[c["fuel_type"]] = fuel_breakdown.get(c["fuel_type"], 0) + 1
    cheapest   = min(cars, key=lambda c: c["price_per_day"])
    expensive  = max(cars, key=lambda c: c["price_per_day"])
    return {
        "total_cars":      len(cars),
        "available_count": len(available),
        "type_breakdown":  type_breakdown,
        "fuel_breakdown":  fuel_breakdown,
        "cheapest_car":    {"model": cheapest["model"],  "price_per_day": cheapest["price_per_day"]},
        "most_expensive":  {"model": expensive["model"], "price_per_day": expensive["price_per_day"]},
    }


# ═════════════════════════════════════════════
#  DAY 3 — Q10  Filter Cars  (above /{car_id})
# ═════════════════════════════════════════════

@app.get("/cars/filter")
def filter_cars(
    type:         str  = Query(None, description="Hatchback / Sedan / SUV / Luxury"),
    brand:        str  = Query(None, description="Car brand"),
    fuel_type:    str  = Query(None, description="Petrol / Diesel / Electric"),
    max_price:    int  = Query(None, description="Max price per day"),
    is_available: bool = Query(None, description="Available cars only"),
):
    result = filter_cars_logic(type, brand, fuel_type, max_price, is_available)
    return {"filtered_cars": result, "count": len(result)}


# ═════════════════════════════════════════════
#  DAY 6 — Q16  Search Cars  (above /{car_id})
# ═════════════════════════════════════════════

@app.get("/cars/search")
def search_cars(keyword: str = Query(..., description="Search keyword")):
    results = [
        c for c in cars
        if keyword.lower() in c["model"].lower()
        or keyword.lower() in c["brand"].lower()
        or keyword.lower() in c["type"].lower()
    ]
    if not results:
        return {"message": f"No cars found for '{keyword}'", "total_found": 0}
    return {"results": results, "total_found": len(results)}


# ═════════════════════════════════════════════
#  DAY 6 — Q17  Sort Cars  (above /{car_id})
# ═════════════════════════════════════════════

@app.get("/cars/sort")
def sort_cars(
    sort_by: str = Query("price_per_day", description="price_per_day / brand / type"),
    order:   str = Query("asc",           description="asc / desc"),
):
    valid_sort  = ["price_per_day", "brand", "type"]
    valid_order = ["asc", "desc"]
    if sort_by not in valid_sort:
        return {"error": f"sort_by must be one of {valid_sort}"}
    if order not in valid_order:
        return {"error": f"order must be one of {valid_order}"}
    sorted_cars = sorted(cars, key=lambda c: c[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "cars": sorted_cars}


# ═════════════════════════════════════════════
#  DAY 6 — Q18  Paginate Cars  (above /{car_id})
# ═════════════════════════════════════════════

@app.get("/cars/page")
def paginate_cars(
    page:  int = Query(1, ge=1,  description="Page number"),
    limit: int = Query(3, ge=1, le=10, description="Items per page"),
):
    total       = len(cars)
    total_pages = math.ceil(total / limit)
    start       = (page - 1) * limit
    items       = cars[start: start + limit]
    return {
        "page": page, "limit": limit,
        "total": total, "total_pages": total_pages,
        "cars": items,
    }


# ═════════════════════════════════════════════
#  DAY 6 — Q20  Browse Cars (combined)  (above /{car_id})
# ═════════════════════════════════════════════

@app.get("/cars/browse")
def browse_cars(
    keyword:      str  = Query(None, description="Search keyword"),
    type:         str  = Query(None, description="Filter by type"),
    fuel_type:    str  = Query(None, description="Filter by fuel type"),
    max_price:    int  = Query(None, description="Max price per day"),
    is_available: bool = Query(None, description="Available only"),
    sort_by:      str  = Query("price_per_day", description="price_per_day / brand / type"),
    order:        str  = Query("asc",           description="asc / desc"),
    page:         int  = Query(1, ge=1),
    limit:        int  = Query(3, ge=1, le=10),
):
    result = cars[:]
    if keyword:
        result = [
            c for c in result
            if keyword.lower() in c["model"].lower()
            or keyword.lower() in c["brand"].lower()
            or keyword.lower() in c["type"].lower()
        ]
    result = filter_cars_logic(type, None, fuel_type, max_price, is_available)
    if sort_by in ["price_per_day", "brand", "type"]:
        result = sorted(result, key=lambda c: c[sort_by], reverse=(order == "desc"))
    total       = len(result)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start       = (page - 1) * limit
    items       = result[start: start + limit]
    return {
        "keyword": keyword, "sort_by": sort_by, "order": order,
        "page": page, "limit": limit,
        "total": total, "total_pages": total_pages,
        "cars": items,
    }


# ═════════════════════════════════════════════
#  DAY 4 — Q11  Add New Car (POST)  (above /{car_id})
# ═════════════════════════════════════════════

@app.post("/cars", status_code=201)
def add_car(new_car: NewCar, response: Response):
    for c in cars:
        if c["model"].lower() == new_car.model.lower() and c["brand"].lower() == new_car.brand.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": f"{new_car.brand} {new_car.model} already exists"}
    new_id = max(c["id"] for c in cars) + 1
    car = {
        "id":           new_id,
        "model":        new_car.model,
        "brand":        new_car.brand,
        "type":         new_car.type,
        "price_per_day": new_car.price_per_day,
        "fuel_type":    new_car.fuel_type,
        "is_available": new_car.is_available,
    }
    cars.append(car)
    return {"message": "Car added successfully", "car": car}


# ═════════════════════════════════════════════
#  DAY 6 — Q19  Rental Search / Sort / Page
# ═════════════════════════════════════════════

@app.get("/rentals/search")
def search_rentals(customer_name: str = Query(..., description="Customer name")):
    results = [r for r in rentals if customer_name.lower() in r["customer_name"].lower()]
    if not results:
        return {"message": "No rentals found for this customer"}
    return {"results": results, "total_found": len(results)}


@app.get("/rentals/sort")
def sort_rentals(
    sort_by: str = Query("total_cost", description="total_cost / days"),
    order:   str = Query("asc",        description="asc / desc"),
):
    valid = ["total_cost", "days"]
    if sort_by not in valid:
        return {"error": f"sort_by must be one of {valid}"}
    sorted_rentals = sorted(rentals, key=lambda r: r[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "rentals": sorted_rentals}


@app.get("/rentals/page")
def paginate_rentals(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10),
):
    total       = len(rentals)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start       = (page - 1) * limit
    items       = rentals[start: start + limit]
    return {"page": page, "limit": limit, "total": total, "total_pages": total_pages, "rentals": items}


# ═════════════════════════════════════════════
#  DAY 5 — Q15  Active Rentals / Unavailable Cars  (fixed routes)
# ═════════════════════════════════════════════

@app.get("/rentals/active")
def active_rentals():
    active = [r for r in rentals if r["status"] == "active"]
    return {"active_rentals": active, "total": len(active)}


@app.get("/cars/unavailable")
def unavailable_cars():
    unavailable = [c for c in cars if not c["is_available"]]
    return {"unavailable_cars": unavailable, "total": len(unavailable)}


# ═════════════════════════════════════════════
#  DAY 1 — Q3   Get Car by ID  (variable — after all fixed routes)
# ═════════════════════════════════════════════

@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}
    return {"car": car}


# ═════════════════════════════════════════════
#  DAY 4 — Q12  Update Car (PUT)
# ═════════════════════════════════════════════

@app.put("/cars/{car_id}")
def update_car(
    car_id:       int,
    response:     Response,
    price_per_day: int  = Query(None, description="New price per day"),
    is_available:  bool = Query(None, description="Update availability"),
):
    car = find_car(car_id)
    if not car:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Car not found"}
    if price_per_day is not None:
        car["price_per_day"] = price_per_day
    if is_available is not None:
        car["is_available"] = is_available
    return {"message": "Car updated", "car": car}


# ═════════════════════════════════════════════
#  DAY 4 — Q13  Delete Car (DELETE)
# ═════════════════════════════════════════════

@app.delete("/cars/{car_id}")
def delete_car(car_id: int, response: Response):
    car = find_car(car_id)
    if not car:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Car not found"}
    active = [r for r in rentals if r["car_id"] == car_id and r["status"] == "active"]
    if active:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Cannot delete — {car['brand']} {car['model']} has an active rental"}
    cars.remove(car)
    return {"message": f"{car['brand']} {car['model']} deleted successfully"}


# ═════════════════════════════════════════════
#  DAY 2 + 3 — Q8 / Q9   Place Rental (POST)
# ═════════════════════════════════════════════

@app.post("/rentals", status_code=201)
def place_rental(data: RentalRequest, response: Response):
    global rental_counter
    car = find_car(data.car_id)
    if not car:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Car not found"}
    if not car["is_available"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"{car['brand']} {car['model']} is not available"}
    cost = calculate_rental_cost(car["price_per_day"], data.days, data.insurance, data.driver_required)
    car["is_available"] = False
    rental = {
        "rental_id":      rental_counter,
        "customer_name":  data.customer_name,
        "car_id":         data.car_id,
        "car_model":      car["model"],
        "car_brand":      car["brand"],
        "days":           data.days,
        "insurance":      data.insurance,
        "driver_required": data.driver_required,
        "base_cost":      cost["base_cost"],
        "discount_pct":   cost["discount_pct"],
        "discount_amount": cost["discount_amount"],
        "insurance_cost": cost["insurance_cost"],
        "driver_cost":    cost["driver_cost"],
        "total_cost":     cost["total_cost"],
        "status":         "active",
    }
    rentals.append(rental)
    rental_counter += 1
    return {"message": "Rental confirmed", "rental": rental}


# ═════════════════════════════════════════════
#  DAY 5 — Q14  Return Car
# ═════════════════════════════════════════════

@app.get("/rentals/{rental_id}")
def get_rental(rental_id: int, response: Response):
    rental = find_rental(rental_id)
    if not rental:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Rental not found"}
    return {"rental": rental}


@app.post("/return/{rental_id}")
def return_car(rental_id: int, response: Response):
    rental = find_rental(rental_id)
    if not rental:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Rental not found"}
    if rental["status"] == "returned":
        return {"message": "This rental is already returned"}
    rental["status"] = "returned"
    car = find_car(rental["car_id"])
    if car:
        car["is_available"] = True
    return {"message": f"{rental['car_brand']} {rental['car_model']} returned successfully", "rental": rental}


# ═════════════════════════════════════════════
#  DAY 5 — Q15  Rental History by Car
# ═════════════════════════════════════════════

@app.get("/rentals/by-car/{car_id}")
def rentals_by_car(car_id: int):
    car = find_car(car_id)
    if not car:
        return {"error": "Car not found"}
    history = [r for r in rentals if r["car_id"] == car_id]
    return {"car": f"{car['brand']} {car['model']}", "rental_history": history, "total": len(history)}
