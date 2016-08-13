import collections

queue = collections.deque(maxlen=5)

def add(val):
    queue.append(val)

def get_avg():
    sum = 0
    for n in queue:
        sum += n

    return sum/queue.count()