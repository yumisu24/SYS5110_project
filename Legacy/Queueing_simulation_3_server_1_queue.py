import numpy as np

MAX_SIMULATION_TIME = 480  # 服务终止时间，单位为分钟

ARRIVAL_EVENT = 0
DEPARTURE_EVENT = 1

debug = True


class Event:
    def __init__(self, event_type, event_time):
        self.event_type = event_type
        self.event_time = event_time


future_event_list = []
simulation_time = 0.0
servers_free_time = [0] * 3  # 三个服务器的空闲时间
servers_idle_time = [0] * 3  # 三台服务器的空闲时间累计
queue = []  # 客户队列（存储到达时间和索引）
arrived_customer_count = 0
abandoned_count = 0  # 放弃等待的客户数量

arrival_times = []
start_service_time = []
depart_times = []


def initialization():
    event = Event(ARRIVAL_EVENT, 0.0)
    future_event_list.append(event)


def generate_service_time():
    return np.random.exponential(1 / 5)  # 服务时间服从参数为5的指数分布


def generate_inter_arrival_time():
    time = np.random.normal(5, 4)  # 客户到达时间间隔服从N(5, 4)的正态分布
    return max(0, time)  # 确保间隔时间不小于0


def remove_imminent_event_from_future_event_list():
    minimum_event_time = float('inf')
    imminent_event = None
    for event in future_event_list:
        if event.event_time < minimum_event_time:
            minimum_event_time = event.event_time
            imminent_event = event
    future_event_list.remove(imminent_event)
    return imminent_event


def check_and_process_abandonments(current_time):
    global abandoned_count
    abandon_prob = {1: 0.3, 2: 0.5, 3: 0.7}  # 按等待时间超过的分钟数映射放弃概率
    queue[:] = [customer for customer in queue if not (
            (current_time - customer[1] > 1 and np.random.random() < abandon_prob[
                min(int(current_time - customer[1]), 3)]) or
            (abandoned_count := abandoned_count + 1)  # 递增放弃客户计数
    )]


def update_idle_times(index, current_time):
    if current_time > servers_free_time[index]:
        servers_idle_time[index] += (current_time - servers_free_time[index])
        servers_free_time[index] = current_time


def process_arrival(arrival_event: Event):
    global simulation_time
    global arrived_customer_count
    simulation_time = arrival_event.event_time
    arrival_times.append(simulation_time)

    check_and_process_abandonments(simulation_time)  # 处理可能的放弃

    for i in range(len(servers_free_time)):
        update_idle_times(i, simulation_time)  # 更新空闲时间
        if simulation_time >= servers_free_time[i]:  # 如果服务器空闲
            service_time = generate_service_time()
            start_service_time.append(simulation_time)
            servers_free_time[i] = simulation_time + service_time  # 更新服务器空闲时间
            new_departure_event = Event(DEPARTURE_EVENT, servers_free_time[i])
            future_event_list.append(new_departure_event)
            break
    else:
        queue.append((arrived_customer_count, simulation_time))  # 所有服务器都忙，加入队列

    arrived_customer_count += 1
    if simulation_time < MAX_SIMULATION_TIME:
        inter_arrival_time = generate_inter_arrival_time()
        new_arrival_event = Event(ARRIVAL_EVENT, simulation_time + inter_arrival_time)
        future_event_list.append(new_arrival_event)


def process_departure(departure_event: Event):
    global simulation_time
    simulation_time = departure_event.event_time
    depart_times.append(simulation_time)

    for i in range(len(servers_free_time)):
        if servers_free_time[i] == simulation_time:  # 找到空闲的服务器
            if queue:  # 检查队列是否有等待的客户
                queue.sort(key=lambda x: x[1])  # 按到达时间排序，确保公平性
                customer_index, _ = queue.pop(0)
                service_time = generate_service_time()
                start_service_time[customer_index] = simulation_time
                servers_free_time[i] = simulation_time + service_time  # 更新服务器空闲时间
                new_departure_event = Event(DEPARTURE_EVENT, servers_free_time[i])
                future_event_list.append(new_departure_event)
            break


def report_generation():
    total_idle_time = sum(servers_idle_time)
    print(f'Total customers arrived: {arrived_customer_count}')
    print(f'Total customers abandoned: {abandoned_count}')
    print(f'Total servers idle time: {total_idle_time} minutes')
    if debug:
        for i in range(len(arrival_times)):
            if i < len(start_service_time):
                print(
                    f'Customer {i + 1}: Arrival time = {arrival_times[i]}, Start service = {start_service_time[i]}, Departure = {depart_times[i]}')
                print()
    for i in range(len(arrival_times)):
        if i < len(start_service_time):
            waiting_time = start_service_time[i] - arrival_times[i]
            total_system_time = depart_times[i] - arrival_times[i]
            print(f'Waiting time for customer {i + 1}: {waiting_time} sec')
            print(f'Total system time for customer {i + 1}: {total_system_time} sec')


def main():
    initialization()
    while future_event_list and future_event_list[0].event_time <= MAX_SIMULATION_TIME:
        imminent_event = remove_imminent_event_from_future_event_list()
        if imminent_event.event_type == ARRIVAL_EVENT:
            process_arrival(imminent_event)
        else:
            process_departure(imminent_event)
    report_generation()


if __name__ == '__main__':
    main()
