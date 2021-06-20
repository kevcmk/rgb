import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import rgb.timer
import datetime

t_fin = datetime.datetime(2021, 6, 19, 15, 3, 15)
t_now = datetime.datetime(2021, 6, 19, 15, 1, 3)
assert rgb.timer.Timer.render_dt(t_fin - t_now) == "2:12"

t_fin = datetime.datetime(2021, 6, 19, 15, 3, 13)
t_now = datetime.datetime(2021, 6, 19, 15, 1, 3)
assert rgb.timer.Timer.render_dt(t_fin - t_now) == "2:10"

t_fin = datetime.datetime(2021, 6, 19, 15, 3, 3)
t_now = datetime.datetime(2021, 6, 19, 15, 1, 3)
assert rgb.timer.Timer.render_dt(t_fin - t_now) == "2:00"

t_fin = datetime.datetime(2021, 6, 19, 15, 3, 45)
t_now = datetime.datetime(2021, 6, 19, 15, 3, 00)
assert rgb.timer.Timer.render_dt(t_fin - t_now) == "0:45"

t_fin = datetime.datetime(2021, 6, 19, 15, 3, 45)
t_now = datetime.datetime(2021, 6, 19, 15, 3, 40)
assert rgb.timer.Timer.render_dt(t_fin - t_now) == "0:05"

t_fin = datetime.datetime(2021, 6, 19, 15, 3, 45)
t_now = datetime.datetime(2021, 6, 19, 15, 3, 45)
assert rgb.timer.Timer.render_dt(t_fin - t_now) == "0:00"