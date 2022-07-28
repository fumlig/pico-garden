import time


def lerp(y0, y1, x, x0=0.0, x1=1.0):
    return (y0*(x1-x) + y1*(x-x0)) / (x1-x0)


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
