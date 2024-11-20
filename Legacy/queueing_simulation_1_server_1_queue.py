import numpy as np

CUSTOMERS_SIZE = 15

ARRIVAL_EVENT = 0
DEPARTURE_EVENT = 1

debug = True


class Event:
    def __init__(self, event_type, event_time):
        self.event_type = event_type
        self.event_time = event_time


future_event_list = []
simulation_time = 0.0
length_of_server = 0
length_of_queue = 0
arrived_customer_count = 0

arrival_times = []
start_service_time = []
depart_times = []


def initialization():
    global arrived_customer_count
    event = Event(ARRIVAL_EVENT, 0.0)
    future_event_list.append(event)
    arrived_customer_count += 1


def generate_service_time():
    return np.random.normal(24, 4, 1)[0]


def generate_inter_arrival_time():
    return np.random.normal(30, 5, 1)[0]


def remove_imminent_event_from_future_event_list():
    minimum_event_time = float('inf')
    imminent_event = None
    for event in future_event_list:
        if event.event_time < minimum_event_time:
            minimum_event_time = event.event_time
            imminent_event = event
    future_event_list.remove(imminent_event)
    return imminent_event


def process_arrival(arrival_event: Event):
    global simulation_time
    global arrived_customer_count
    global length_of_server
    global length_of_queue
    simulation_time = arrival_event.event_time
    arrival_times.append(simulation_time)
    if length_of_server == 0:
        length_of_server = 1
        service_time = generate_service_time()
        start_service_time.append(simulation_time)
        new_departure_event = Event(DEPARTURE_EVENT, simulation_time + service_time)
        future_event_list.append(new_departure_event)
    else:
        length_of_queue += 1

    if arrived_customer_count < CUSTOMERS_SIZE:
        inter_arrival_time = generate_inter_arrival_time()
        new_arrival_event = Event(ARRIVAL_EVENT, simulation_time + inter_arrival_time)
        future_event_list.append(new_arrival_event)
        arrived_customer_count += 1


def process_departure(departure_event: Event):
    global length_of_queue
    global length_of_server
    simulation_time = departure_event.event_time
    depart_times.append(simulation_time)
    if length_of_queue > 0:
        length_of_queue -= 1
        service_time = generate_service_time()
        start_service_time.append(simulation_time)
        new_departure_event = Event(DEPARTURE_EVENT, simulation_time + service_time)
        future_event_list.append(new_departure_event)
    else:
        length_of_server = 0


def report_generation():
    if debug:
        for i in range(CUSTOMERS_SIZE):
            print(f'arrival time of customer {i+1}: {arrival_times[i]}')
            print(f'start service time of customer {i + 1}: {start_service_time[i]}')
            print(f'depart time of customer {i + 1}: {depart_times[i]}')
        print()
    for i in range(CUSTOMERS_SIZE):
        waiting_time = start_service_time[i] - arrival_times[i]
        total_system_time = depart_times[i] - arrival_times[i]
        print(f'Waiting time for customer {i + 1}: {waiting_time} sec')
        print(f'Total system time for customer {i + 1}: {total_system_time} sec')


def main():
    initialization()
    while len(future_event_list) != 0:
        imminent_event = remove_imminent_event_from_future_event_list()
        if imminent_event.event_type == ARRIVAL_EVENT:
            process_arrival(imminent_event)
        else:
            process_departure(imminent_event)
    report_generation()


if __name__ == '__main__':
    main()
