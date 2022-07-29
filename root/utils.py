import time


def lerp(x, y_min, y_max, x_min=0.0, x_max=1.0):
    return (y_min*(x_max-x) + y_max*(x-x_min)) / (x_max-x_min)


def clamp(x, y_min, y_max):
    if y_min is not None:
        x = max(x, y_min)
    if y_max is not None:
        x = min(x, y_max)
    return x


async def connect(wlan, ssid, key, max_wait=10):
    print("connecting to wlan...")
    wlan.active(True)
    wlan.config(pm=0xa11140) # disable power-save mode
    wlan.connect(ssid, key)

    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("waiting for connection...")
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError("network connection failed")
    else:
        status = wlan.ifconfig()
        print(f"network connected:", status)
