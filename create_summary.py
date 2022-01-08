from datetime import datetime, timedelta
import json
import os
from web import _list_dates, _summary


def daily_summary():
    """前日分までの日別まとめファイルを更新する"""
    oldest = _list_dates()[0]
    daily_summary = _summary(date_from=oldest, time_unit='day')
    # 当日分の記録は計測中なので除く
    if daily_summary['timestamp'][-1] == datetime.now().strftime('%Y-%m-%d'):
        for key in daily_summary:
            del(daily_summary[key][-1])
    with open(os.path.join(os.path.dirname(__file__), 'log/daily_summary.json'), mode='w') as fp:
        fp.write(json.dumps(daily_summary))


if __name__ == '__main__':
    daily_summary()
