import machine
import network
import utime as time
import uasyncio as asyncio
import uhttp as http
import secret
import utils


led = machine.Pin("LED", machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)
pump = machine.PWM(machine.Pin(15))
moisture = machine.ADC(machine.Pin(26))
srv = http.Server()


@srv.route("/")
async def index(_request):
    return http.Response.html(open("index.html", "rb"))

@srv.route("/pump", method="GET")
async def get_pump(_request):
    data = {"duty": pump.duty_u16(), "freq": pump.freq()}

    return http.Response.json(data)

@srv.route("/pump", method="PUT")
async def set_pump(request):
    data = await request.json()

    if not "duty" in data or not "freq" in data:
        raise http.Error(400)

    print("setting pump:", data)

    pump.duty_u16(data["duty"])
    pump.freq(data["freq"])

    return http.Response(200) 

@srv.route("/moisture", method="GET")
async def get_moisture(_request):
    data = moisture.read_u16()

    return http.Response.json(data)


async def main():
    await utils.connect(wlan, secret.SSID, secret.KEY)
    
    asyncio.create_task(srv.start())

    while True:
        print("heartbeat")
        led.on()
        await asyncio.sleep_ms(100)
        led.off()
        await asyncio.sleep_ms(5000)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
