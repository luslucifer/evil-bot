import time
from threading import Thread
fruits = ['apple', 'banana', 'orange', 'grape', 'kiwi']

def process_fruit(fruit):
    time.sleep(1)  # Simulate processing time
    return fruit

def process_fruits(fruits):
    threads = []
    results = []
    for fruit in fruits : 
        t = Thread(target=lambda:results.append(process_fruit(fruit)))
        threads.append(t)
        t.start()  
    for thread in threads:
        thread.join()
    
    return results

if __name__ == "__main__":
    start_time = time.time()
    processed_fruits = process_fruits(fruits)
    end_time = time.time()
    
    print("Processed fruits:", processed_fruits)
    print("Total time taken:", end_time - start_time, "seconds")
