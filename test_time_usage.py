import time

start_time = time.time_ns()
print(start_time, "nanoseconds")

time.sleep(1)

end_time = time.time_ns()
print(end_time, "nanoseconds")
print(end_time - start_time, "nanoseconds")
print((end_time - start_time) / 1e6, "milliseconds")
print((end_time - start_time) / 1e9, "seconds")
