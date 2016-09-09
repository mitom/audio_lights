import config

def calculate_colour(ys):
    # Limits for which areas influence which colours
    g_area=config.config['g_area']
    r_area=config.config['r_area']
    b_area=config.config['b_area']
    g_boost=config.config['g_boost']
    r_boost=config.config['r_boost']
    b_boost=config.config['b_boost']
    scale = config.config['saturation']

    r,g,b,max=0,0,0,0
    rc,gc,bc=0,0,0

    for n in range(0,ys.size):
        pos = n/float(ys.size)
        if (pos >= r_area[0] and pos <= r_area[1]):
            val = ys[n]
            if (val > max): max = val
            if (pos >= r_boost[0] and pos <= r_boost[1]): val=val*r_boost[2]
            r+=val
            rc+=1
        if (pos >= g_area[0] and pos <= g_area[1]):
            val = ys[n]
            if (val > max): max = val
            if (pos >= g_boost[0] and pos <= g_boost[1]): val=val*g_boost[2]
            g+=val
            gc+=1

        if (pos >= b_area[0] and pos <= b_area[1]):
            val = ys[n]
            if (val > max): max = val
            if (pos >= b_boost[0] and pos <= b_boost[1]): val=val*b_boost[2]
            b+=val
            bc+=1

    if r: r=255*r/gc/max
    if g: g=255*g/gc/max
    if b: b=255*b/gc/max

    if r>255: r=255
    if g>255: g=255
    if b>255: b=255

    if r<0: r=0
    if g<0: g=0
    if b<0: b=0


    alpha = max/scale*255
    if (alpha > 255): alpha = 255
    if (alpha < 0): alpha = 0

    return {
        'r': r,
        'g': g,
        'b': b,
        'alpha': alpha
    }
