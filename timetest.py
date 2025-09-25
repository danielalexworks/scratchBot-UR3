
import time

def test_sleep_precision(sleep_time, iterations=1000):
    deltas = []
    for _ in range(iterations):
        start = time.perf_counter()  # High-precision timer
        time.sleep(sleep_time)
        end = time.perf_counter()
        print(f"perfs: {end - start}")
        deltas.append(end - start)
    
    average_sleep = sum(deltas) / len(deltas)
    print(f"Requested sleep time: {sleep_time} seconds")
    print(f"Average actual sleep time: {average_sleep:.9f} seconds")
    print(f"System deviation: {average_sleep - sleep_time:.9f} seconds")
    print(f"perfs: {end - start}")



def HQDelay(amt):
    t = 0
    start = time.perf_counter()
    while time.perf_counter() - start < amt:
        pass

    print(f"HQDElay: {time.perf_counter() - start}")

# Test with a very small sleep time
test_sleep_precision(0.0001, 1)  # 0.1 milliseconds
HQDelay(.0001)


