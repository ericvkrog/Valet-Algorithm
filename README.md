# Valet Parking Algorithm

A simulation of a valet parking lot that compares a smart car-placement algorithm against a random baseline. The smart algorithm minimizes reshuffles — the number of times a car must be temporarily moved to retrieve another car — by tracking each customer's expected stay time and arranging cars so short-stayers are never blocked by long-stayers.

The lot has 70 lanes: 20 single-deep, 30 double-deep, and 20 triple-deep. A full 8-hour shift of 300 cars is simulated with randomized return times (customers come back anywhere between 50% and 150% of their stated stay), and the smart algorithm consistently produces significantly fewer reshuffles than the random baseline.

## How to run the simulation

```
python main.py
```

## How to run the tests

```
pytest test_valet.py
```

Requires pytest (`pip install pytest`).

## How to run the benchmark

```
python benchmark.py
```

Prints total reshuffles, runtime, and peak memory usage for both algorithms.
