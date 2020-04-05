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
with open(os.path.join(app_root, 'index.html'), mode='rb') as fp:
    index_html = fp.read()


def serve_file(environ, start_response):
    status = '404 Not Found'
    byte_content = b''
    content_type = 'text/plain'
    content_length = '0'

    req_path = environ.get('PATH_INFO', '/')
    if req_path in ('/', '/index.html'):
        status = '200 OK'
        content_type = 'text/html'
        content_length = str(len(index_html))
        byte_content = index_html

    elif req_path == '/log':
        qdic = dict(parse_qsl(environ.get('QUERY_STRING', '')))
        req_date = qdic.get('date', '').split('/')[-1]
        if req_date:
            log_file = os.path.join(app_root, 'log', req_date + '.csv')
            if os.path.exists(log_file):
                with open(log_file, mode='rb') as fp:
                    byte_content = fp.read()
                status = '200 OK'
                content_length = str(len(byte_content))

    headers = [
        ('Content-Type', content_type),
        ('Content-Length', content_length)
    ]
    start_response(status, headers)
    return [byte_content]


def main():
    server_th = Thread(target=serve, args=(serve_file, ), kwargs={'host': '0.0.0.0', 'port': 8080})
    server_th.start()

    while True:
        s = time()

        values = mh_z19.read_all()
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)

        co2_str = str(values.get('co2', 'failed')) if values else 'failed'
        temperature_str = 'failed' if temperature is None else str(int(temperature))
        humidity_str = 'failed' if humidity is None else str(int(humidity))
        time_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        pioled.set_text_lines((
            time_text,
            'CO2 {}ppm'.format(co2_str),
            'temperature {}C'.format(temperature_str),
            'humidity {}%'.format(humidity_str)
        ))

        log_text = '{},{},{},{}\n'.format(time_text, co2_str, temperature_str, humidity_str)
        logfile = 'log/{}.csv'.format(time_text.split(' ')[0])
        with open(logfile, mode='a') as fp:
            fp.write(log_text)
        sleep(TARGET_INTERVAL - (time() - s))


if __name__ == '__main__':
    main()
