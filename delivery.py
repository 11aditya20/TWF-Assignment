from fastapi import FastAPI, HTTPException
from typing import Dict, List, Tuple
from itertools import permutations

app = FastAPI()

# Data- "product name": ("center", "weight")
product_data = {
    "A": ("C1", 3), "B": ("C1", 2), "C": ("C1", 8),
    "D": ("C2", 12), "E": ("C2", 25), "F": ("C2", 15),
    "G": ("C3", 0.5), "H": ("C3", 1), "I": ("C3", 2)
}

# Distances- ("from", "to") : "distance"
distances = {
    ("C1", "L1"): 3, ("C2", "L1"): 2.5, ("C3", "L1"): 2,
    ("C1", "C2"): 4, ("C2", "C3"): 3, ("C1", "C3"): 7
}
# Make distances bidirectional
for (a, b), d in list(distances.items()):
    distances[(b, a)] = d

def cost_per_distance(weight: float) -> float:
    if weight <= 5:
        return 10
    extra = weight - 5
    return 10 + (int((extra + 4.9999) // 5)) * 8

def group_products_by_center(order: Dict[str, int]) -> Dict[str, List[Tuple[str, int, float]]]:
    grouped = {"C1": [], "C2": [], "C3": []}
    for prod, qty in order.items():
        if prod not in product_data:
            raise ValueError(f"Product {prod} not found.")
        center, weight = product_data[prod]
        grouped[center].append((prod, qty, weight))
    return grouped

def generate_sequences(start: str, centers: List[str]) -> List[List[str]]:
    centers = list(set(centers))
    centers.remove(start)
    all_routes = []
    for perm in permutations(centers):
        route = [start]
        for c in perm:
            route += ["L1", c]
        route.append("L1")
        all_routes.append(route)
    return all_routes

def calculate_route_cost(route: List[str], grouped: Dict[str, List[Tuple[str, int, float]]]) -> float:
    total_cost = 0.0
    carried_items = []

    for i in range(1, len(route)):
        from_loc, to_loc = route[i - 1], route[i]
        if from_loc in grouped:
            for _, qty, wt in grouped[from_loc]:
                carried_items += [(wt, from_loc)] * qty

        weight = sum(w for w, _ in carried_items)
        per_unit = cost_per_distance(weight)
        total_cost += distances[(from_loc, to_loc)] * per_unit

        if to_loc == "L1":
            carried_items = []

    return total_cost

def compute_min_cost(order: Dict[str, int]) -> float:
    grouped = group_products_by_center(order)
    centers = [c for c, items in grouped.items() if items]
    min_cost = float("inf")

    for start in centers:
        routes = generate_sequences(start, centers)
        for route in routes:
            cost = calculate_route_cost(route, grouped)
            if cost < min_cost:
                min_cost = cost

    return min_cost

@app.post("/calculate")
async def calculate_cost(order: Dict[str, int]):
    try:
        cost = compute_min_cost(order)
        return {"minimum_cost": cost}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))