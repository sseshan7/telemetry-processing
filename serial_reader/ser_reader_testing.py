import math
import time
import asyncio
import json

async def generate_data(data_storage):
    """
    Generates dummy data for testing
    """
    while True:
        await asyncio.sleep(1)
        t = int(time.time() * 1000)
        var = {'timestamp': t, 'value': math.sin(t)}
        data_storage['pwr.temp'].append(var)


def package_data(raw_data):
    """
    Parses, packages, and organizes serial data
    :param raw_data: raw string read from serial
    :return a dict (str -> triple[str]) of json payloads keyed by sensor (should
     probably be keyed by id so its cleaner to store)
    """
    readings = [float(i) for i in raw_data.split()]
    jsons = []
    for reading in readings:
        timestamp = int(time.time())
        payload = {'timestamp': timestamp, 'value': reading}
        jsons.append(json.dumps(payload, separators=(',', ':')))
    return {
        'accel': (jsons[0], jsons[1], jsons[2]),  # ax, ay, az
        'gyro': (jsons[3], jsons[4], jsons[5]),  # gx, gy, gz
        'mag': (jsons[6], jsons[7], jsons[8])  # mx, my, mz
    }

