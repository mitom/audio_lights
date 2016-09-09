from multiprocessing import Manager
import json

manager = Manager()
config = manager.dict()

def set_default():
    config['sample_size'] = 64
    config['r_area'] = [0.2,0.3]
    config['g_area'] = [0,0.3]
    config['b_area'] = [0.6,1]
    config['r_boost'] = [0.2,0.3,3]
    config['g_boost'] = [0,0.15,1.4]
    config['b_boost'] = [0.6,0.7,4]
    config['saturation'] = 3000
    config['trim'] = 5
    config['scale'] = 100
    config['active'] = True
    config['clapper'] = True

def load():
    set_default()
    try:
        with open('config.json', 'r') as file:
            try:
                data = json.load(file)
                for key in data:
                    config[key] = data[key]
            except ValueError:
                print "No config to load."
    except IOError:
        return

def dump():
    print config.copy()
    with open('config.json', 'w') as outfile:
        json.dump(config.copy(), outfile)
