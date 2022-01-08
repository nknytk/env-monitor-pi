from datetime import datetime, timedelta
import json
import re
import os
from urllib.parse import parse_qsl

app_root = os.path.dirname(__file__)


def application(environ, start_response):
    status = '404 Not Found'
    content = b'requested path not found'
    content_type = 'text/plain'

    req_path = environ.get('PATH_INFO', '/')
    if req_path in ('/', '/index.html'):
        status, content, content_type = '200 OK', _read_static('index.html'), 'text/html; charset="UTF-8"'
    elif req_path == '/history':
        status, content, content_type = '200 OK', _read_static('history.html'), 'text/html; charset="UTF-8"'
    elif req_path == '/log':
        status, content, content_type = get_log(environ)
    elif req_path == '/list':
        status, content, content_type = list_dates(environ)
    elif req_path == '/summary':
        status, content, content_type = get_summary(environ)

    headers = [
        ('Content-Type', content_type),
        ('Content-Length', str(len(content)))
    ]
    start_response(status, headers)
    return [content]


def get_log(environ):
    qdic = dict(parse_qsl(environ.get('QUERY_STRING', '')))
    req_date = qdic.get('date', '')
    if not req_date:
        req_date = _list_dates()[-1]
    log_file = os.path.join(app_root, 'log', req_date + '.csv')

    if os.path.exists(log_file):
        with open(log_file, mode='rb') as fp:
            byte_content = fp.read()
        if qdic.get('with_header'):
            byte_content = b'timestamp,co2(ppm),temperature(C),humidity(%),discomfort_index\n' + byte_content
        return '200 OK', byte_content, 'text/csv;charset="UTF-8"'
    else:
        byte_content = b'file not found'
        return '404 Not Found', byte_content, 'text/plain;charset="UTF-8"'


def list_dates(environ):
    valid_dates = _list_dates()
    content = bytes(json.dumps(valid_dates), encoding='UTF-8')
    return '200 OK', content, 'application/json'


def get_summary(environ):
    qdic = dict(parse_qsl(environ.get('QUERY_STRING', '')))
    date_from = qdic.get('from', _list_dates()[-3])
    time_unit = qdic.get('unit', 'hour')
    content = bytes(json.dumps(_summary(date_from, time_unit)), encoding='UTF=8')
    return '200 OK', content, 'application/json'


def _list_dates(date_from=None, date_to=None):
    valid_dates = []
    valid_file_pattern = re.compile('^202[0-9]-[01][0-9]-[0-3][0-9].csv$')
    for f in os.listdir(os.path.join(app_root, 'log')):
        if valid_file_pattern.match(f):
            file_date = f.split('.')[0]
            if date_from is not None and file_date < date_from:
                continue
            if date_to is not None and date_to > file_date:
                continue
            valid_dates.append(file_date)
    valid_dates.sort()
    return valid_dates


def _read_static(file_name):
    with open(os.path.join(app_root, file_name), mode='rb') as fp:
        return fp.read()


def _summary(date_from, time_unit='hour'):
    result = {
        'timestamp': [],
        'max_co2': [],
        'avg_co2': [],
        'min_co2': [],
        'max_temperature': [],
        'avg_temperature': [],
        'min_temperature': [],
        'max_humidity': [],
        'avg_humidity': [],
        'min_humidity': [],
        'max_di': [],
        'avg_di': [],
        'min_di': []
    }

    if time_unit == 'day':
        time_formatter = lambda x: x[:10]
        summary_file = os.path.join(app_root, 'log/daily_summary.json')
        if os.path.exists(summary_file):
            with open(summary_file) as fp:
                result = json.load(fp)
            while result['timestamp'][0] < date_from:
                for key in result:
                    del(result[key][0])
            date_from = (datetime.strptime(result['timestamp'][-1], '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    elif time_unit == 'hour':
        time_formatter = lambda x: x[:14] + '00:00'

    key = ''
    co2s, temperatures, humidities, dis = [], [], [], []
    for valid_date in _list_dates(date_from=date_from):
        file_path = os.path.join(app_root, 'log', valid_date + '.csv')
        with open(file_path) as fp:
            for row in fp:
                timestamp, co2, temperature, humidity, di = row.strip().split(',')
                timestamp = time_formatter(timestamp)

                if timestamp != key:
                    if key and (co2s or temperatures or humidities or di):
                        result['timestamp'].append(key)
                        if co2s:
                            result['max_co2'].append(max(co2s))
                            result['min_co2'].append(min(co2s))
                            result['avg_co2'].append(round(sum(co2s) / len(co2s), 2))
                        else:
                            result['max_co2'].append(None)
                            result['min_co2'].append(None)
                            result['avg_co2'].append(None)
                        if temperatures:
                            result['max_temperature'].append(max(temperatures))
                            result['min_temperature'].append(min(temperatures))
                            result['avg_temperature'].append(round(sum(temperatures) / len(temperatures), 2))
                        else:
                            result['max_temperature'].append(None)
                            result['min_temperature'].append(None)
                            result['avg_temperature'].append(None)
                        if humidities:
                            result['max_humidity'].append(max(humidities))
                            result['min_humidity'].append(min(humidities))
                            result['avg_humidity'].append(round(sum(humidities) / len(humidities), 2))
                        else:
                            result['max_humidity'].append(None)
                            result['min_humidity'].append(None)
                            result['avg_humidity'].append(None)
                        if dis:
                            result['max_di'].append(max(dis))
                            result['min_di'].append(min(dis))
                            result['avg_di'].append(round(sum(dis) / len(dis), 2))
                        else:
                            result['max_di'].append(None)
                            result['min_di'].append(None)
                            result['avg_di'].append(None)

                    key = timestamp
                    co2s, temperatures, humidities, dis = [], [], [], []

                if co2 != 'failed':
                    co2s.append(int(co2))
                if temperature != 'failed':
                    temperatures.append(float(temperature))
                if humidity != 'failed':
                    humidities.append(float(humidity))
                if di != 'failed':
                    dis.append(float(di))
                    
    if co2s or temperatures or humidities:
        result['timestamp'].append(key)
        if co2s:
            result['max_co2'].append(max(co2s))
            result['min_co2'].append(min(co2s))
            result['avg_co2'].append(round(sum(co2s) / len(co2s), 2))
        else:
            result['max_co2'].append(None)
            result['min_co2'].append(None)
            result['avg_co2'].append(None)
        if temperatures:
            result['max_temperature'].append(max(temperatures))
            result['min_temperature'].append(min(temperatures))
            result['avg_temperature'].append(round(sum(temperatures) / len(temperatures), 2))
        else:
            result['max_temperature'].append(None)
            result['min_temperature'].append(None)
            result['avg_temperature'].append(None)
        if humidities:
            result['max_humidity'].append(max(humidities))
            result['min_humidity'].append(min(humidities))
            result['avg_humidity'].append(round(sum(humidities) / len(humidities), 2))
        else:
            result['max_humidity'].append(None)
            result['min_humidity'].append(None)
            result['avg_humidity'].append(None)
        if dis:
            result['max_di'].append(max(dis))
            result['min_di'].append(min(dis))
            result['avg_di'].append(round(sum(dis) / len(dis), 2))
        else:
            result['max_di'].append(None)
            result['min_di'].append(None)
            result['avg_di'].append(None)

    return result
