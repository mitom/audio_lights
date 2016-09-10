import collections
import time
import config
import math

queue_length = 20
queue = collections.deque(maxlen=queue_length)
lastclap = None

def add(val):
    global lastclap
    result = 0
    if is_measureable():
        min = 25*(10-math.log10(config.config['scale']))
        if val*0.3 > get_avg() and val > min:
            now = time.time()
            if lastclap == None or lastclap+0.15 < now:
                if lastclap != None and lastclap+0.5 > now:
                    lastclap = None
                    result = 2
                else:
                    result = 1
                    val = val*0.7

                lastclap = now


    queue.append(val)
    return result

def get_avg():
    sum = 0
    for n in queue:
        sum += n

    return sum/len(queue)

def is_measureable():
    if len(queue) < queue_length: return False

    return True