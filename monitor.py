from datetime import datetime
from time import time, sleep
import os
import sys
from threading import Thread
from urllib.parse import parse_qsl
from waitress import serve
import mh_z19
import pioled
import Adafruit_DHT

SENSOR = Adafruit_DHT.DHT11
PIN = 23
TARGET_INTERVAL = 60

app_root = os.path.dirname(__file__)
sys.path.append(app_root)
import web


def main():
    server_th = Thread(target=serve, args=(web.application, ), kwargs={'host': '0.0.0.0', 'port': 8080})
    server_th.start()

    while True:
        s = time()

        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' read mh_z19')
        values = mh_z19.read_all()
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' read DHT11')
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)

        co2_str = str(values.get('co2', 'failed')) if isinstance(values, dict) else 'failed'
        print(values)
        temperature_str = 'failed' if temperature is None else str(int(temperature))
        humidity_str = 'failed' if humidity is None else str(int(humidity))
        time_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' set pioled')
        pioled.set_text_lines((
            time_text,
            'CO2 {}ppm'.format(co2_str),
            'temperature {}C'.format(temperature_str),
            'humidity {}%'.format(humidity_str)
        ))

        log_text = '{},{},{},{}\n'.format(time_text, co2_str, temperature_str, humidity_str)
        logfile = 'log/{}.csv'.format(time_text.split(' ')[0])
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' write csv')
        with open(logfile, mode='a') as fp:
            fp.write(log_text)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' sleep')
        sleep(TARGET_INTERVAL - (time() - s))


if __name__ == '__main__':
    main()
