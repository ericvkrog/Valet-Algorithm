import time
import tracemalloc
import random
from main import run_simulation, park_car_smart, park_car_random

random.seed(42)
normal_cars  = [(f"car_{i}", random.randint(0, 390),   random.randint(10, 200))  for i in range(265)]
long_stayers = [(f"car_{i}", random.randint(391, 480), random.randint(300, 600)) for i in range(265, 300)]
shift_cars = [
    (arrive, car_id, stay, arrive + int(stay * random.uniform(0.5, 1.5)))
    for car_id, arrive, stay in (normal_cars + long_stayers)
]

def measure(label, fn):
    tracemalloc.start()
    t0 = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{label}")
    print(f"  reshuffles : {result}")
    print(f"  time       : {elapsed * 1000:.2f} ms")
    print(f"  peak memory: {peak / 1024:.1f} KB")

print("=== valet parking benchmark (300 cars, 70-lane lot) ===\n")
measure("smart algorithm", lambda: run_simulation(shift_cars, park_car_smart))

random.seed(77)
measure("random baseline", lambda: run_simulation(shift_cars, park_car_random))
