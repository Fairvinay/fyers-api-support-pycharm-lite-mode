#https://medium.com/@surve.aasim/thread-synchronization-in-python-using-queue-1be0df535a66

import threading
import time
import queue

# Queue to hold shared data
data_queue = queue.Queue(maxsize=5)

# Producer function
def producer():
    for i in range(10):
        item = f"Item {i}"
        print(f"Producing {item}")
        data_queue.put(item)
        time.sleep(1)

# Consumer function
def consumer():
    while True:
        item = data_queue.get()
        if item is None:
            break
        print(f"Consuming {item}")
        data_queue.task_done()

# Create producer and consumer threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

# Start the threads
producer_thread.start()
consumer_thread.start()

# Wait for producer to finish, then signal consumer to stop
producer_thread.join()
data_queue.put(None)
consumer_thread.join()

print("All threads have finished.")