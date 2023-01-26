import tracemalloc


def app():
    lt = []
    for i in range(0, 100000):
        lt.append(i)


tracemalloc.start()

app()

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current} Bytes")
print(f"Peak: {peak} Bytes")
print(f"Peak: {peak / (1024 * 1024)} MegaBytes")

tracemalloc.stop()
