import random
import main


def make_15_lanes():
    return (
        {f"A{i}": {"stack": [], "max": 1} for i in range(1, 6)} |
        {f"B{i}": {"stack": [], "max": 2} for i in range(1, 6)} |
        {f"C{i}": {"stack": [], "max": 3} for i in range(1, 6)}
    )


def test_smart_zero_reshuffles_long_before_short():
    # lot has one single-deep and one double-deep lane
    # smart puts long_car in the single-deep (safe), short_car in the double-deep
    # retrieving short_car requires zero reshuffles
    lot = {"A": {"stack": [], "max": 1}, "B": {"stack": [], "max": 2}}
    main.park_car_smart("long_car", 480, lot)
    main.park_car_smart("short_car", 30, lot)
    assert main.retrieve_car_from("short_car", lot) == 0


def test_random_at_least_one_reshuffle_long_before_short():
    # single two-deep lane forces both cars into the same stack
    # long_car parks first (bottom), short_car parks second (top)
    # retrieving long_car requires moving short_car — always 1 reshuffle
    lot = {"X": {"stack": [], "max": 2}}
    main.park_car_random("long_car", 480, lot)
    main.park_car_random("short_car", 30, lot)
    assert main.retrieve_car_from("long_car", lot) >= 1


def test_lot_full_no_crash():
    # two single-deep lanes, fill both, then attempt a third car
    lot = {"A": {"stack": [], "max": 1}, "B": {"stack": [], "max": 1}}
    main.park_car_smart("car1", 30, lot)
    main.park_car_smart("car2", 30, lot)
    main.park_car_smart("overflow", 30, lot)
    total = sum(len(s["stack"]) for s in lot.values())
    assert total == 2  # overflow was silently rejected, not added


def test_retrieve_nonexistent_no_crash():
    lot = main.make_slots()
    assert main.retrieve_car_from("ghost", lot) == 0


def test_smart_beats_random_300_cars():
    random.seed(42)
    raw = [(f"car_{i}", random.randint(0, 480), random.randint(10, 300)) for i in range(300)]
    shift_cars = [
        (arrive, car_id, stay, arrive + int(stay * random.uniform(0.5, 1.5)))
        for car_id, arrive, stay in raw
    ]
    smart_r = main.run_simulation(shift_cars, main.park_car_smart, make_15_lanes)
    random.seed(77)
    random_r = main.run_simulation(shift_cars, main.park_car_random, make_15_lanes)
    assert smart_r < random_r
