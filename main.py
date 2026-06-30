import random

def make_slots():
    # 20 single-deep, 30 double-deep, 20 triple-deep = 70 lanes
    return (
        {f"A{i:02d}": {"stack": [], "max": 1} for i in range(1, 21)} |
        {f"B{i:02d}": {"stack": [], "max": 2} for i in range(1, 31)} |
        {f"C{i:02d}": {"stack": [], "max": 3} for i in range(1, 21)}
    )

# scores every available lane for the incoming car and picks the one with the
# lowest penalty. priority order: avoid blocking other cars, then prefer the
# lane where a blocked car would be stuck the longest (so we can reshuffle it
# sooner rather than holding it forever), then avoid wasting deep lane space.
def park_car_smart(car_id, minutes, lot):
    best_slot, best_score = None, (999, 999, 999)
    for name, slot in lot.items():
        if len(slot["stack"]) >= slot["max"]:
            continue
        # count how many cars already in this lane would be trapped behind the
        # incoming car — a car is "blocked" if it has a shorter stay than ours,
        # meaning it needs to leave first but we'd be sitting on top of it
        blocking = sum(1 for p in slot["stack"] if minutes > p["minutes"])
        if blocking > 0:
            # find the shortest stay among the cars we'd block. we want to
            # minimize the "worst victim" — ideally pick the lane where the
            # car we block was going to leave the latest anyway (less urgency).
            # but lower score wins, so we negate min_blocked: a larger
            # min_blocked (car leaves later, less urgent) becomes a more
            # negative number, which python sorts before a smaller negative —
            # that makes "least urgent victim" the preferred lane.
            min_blocked = min(p["minutes"] for p in slot["stack"] if minutes > p["minutes"])
            secondary = -min_blocked
            # dont bother tracking empty depth when we're already causing a
            # conflict — blocking is the dominant concern
            empty_depth = 0
        else:
            secondary = 0
            # no conflict here, so this car can safely go in any open lane.
            # but single-deep (A) lanes can NEVER cause a reshuffle since they only
            # ever hold 1 car, so theyre a zero-risk use of space. deep lanes (B/C)
            # are more valuable because they can stack multiple compatible cars
            # later (long-stay on bottom, short-stay on top). dont waste that
            # flexibility on a car that didnt need it, save deep lanes for when
            # we actually need to stack
            empty_depth = slot["max"] if slot["max"] > 1 else 0
        # python compares tuples left to right, so blocking wins over everything:
        # a lane with 0 blocks beats one with 1 no matter what secondary or
        # empty_depth say. only when blocking is tied does secondary matter,
        # and only when both are tied does empty_depth break it.
        score = (blocking, secondary, empty_depth)
        if score < best_score:
            best_score, best_slot = score, name
    if best_slot is None:
        return
    lot[best_slot]["stack"].append({"id": car_id, "minutes": minutes})

def park_car_random(car_id, minutes, lot):
    available = [slot for slot in lot.values() if len(slot["stack"]) < slot["max"]]
    if not available:
        return
    random.choice(available)["stack"].append({"id": car_id, "minutes": minutes})

def retrieve_car_from(car_id, lot):
    reshuffles = 0
    for _, slot in lot.items():
        stack = slot["stack"]
        if car_id not in [c["id"] for c in stack]:
            continue
        while stack[-1]["id"] != car_id:
            stack.pop()
            reshuffles += 1
        stack.pop()
        return reshuffles
    return 0

def run_simulation(cars, park_fn, lot_factory=make_slots):
    # cars is list of (arrive_min, car_id, stay_min, actual_return_min)
    # return times are pre-generated so both algos face the exact same scenario
    lot = lot_factory()
    total_reshuffles = 0
    pending_retrievals = []

    for arrive_time, car_id, stay, return_time in sorted(cars):
        due = [r for r in pending_retrievals if r[0] <= arrive_time]
        pending_retrievals = [r for r in pending_retrievals if r[0] > arrive_time]
        for _, cid in due:
            total_reshuffles += retrieve_car_from(cid, lot)

        park_fn(car_id, stay, lot)
        pending_retrievals.append((return_time, car_id))

    for _, cid in pending_retrievals:
        total_reshuffles += retrieve_car_from(cid, lot)

    return total_reshuffles


if __name__ == "__main__":
    # 35 long-stayers arrive in the last 90 min while the lot is still packed with short-stayers
    # return times are randomized 50-150% of stated stay — baked in before either sim run
    random.seed(42)
    normal_cars  = [(f"car_{i}", random.randint(0, 390),   random.randint(10, 200))  for i in range(265)]
    long_stayers = [(f"car_{i}", random.randint(391, 480), random.randint(300, 600)) for i in range(265, 300)]
    shift_cars = [
        (arrive, car_id, stay, arrive + int(stay * random.uniform(0.5, 1.5)))
        for car_id, arrive, stay in (normal_cars + long_stayers)
    ]

    smart_reshuffles  = run_simulation(shift_cars, park_car_smart)
    random_reshuffles = run_simulation(shift_cars, park_car_random)

    print("\n--- full shift simulation (300 cars, 70-lane lot) ---")
    print(f"smart algorithm total reshuffles:  {smart_reshuffles}")
    print(f"random baseline total reshuffles:  {random_reshuffles}")

    # directly set up the two lot states to show the core conflict:
    #   smart outcome: long and short car in separate lanes
    #   random worst-case: long_car stacked on top of short_car in the same lane
    print("\n--- test: long_car on top of short_car (random worst-case) vs separate lanes (smart) ---")

    def mini_lot():
        return {"A": {"stack": [], "max": 1}, "B": {"stack": [], "max": 2}, "C": {"stack": [], "max": 3}}

    lot_smart = mini_lot()
    lot_rand  = mini_lot()

    lot_smart["B"]["stack"] = [{"id": "short_car"}]
    lot_smart["C"]["stack"] = [{"id": "long_car"}]
    lot_rand["B"]["stack"]  = [{"id": "short_car"}, {"id": "long_car"}]

    smart_r = retrieve_car_from("short_car", lot_smart)
    rand_r  = retrieve_car_from("short_car", lot_rand)

    print(f"smart: {smart_r} reshuffle(s) to retrieve short_car")
    print(f"random worst-case: {rand_r} reshuffle(s) to retrieve short_car")
