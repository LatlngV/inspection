# -*- coding: utf-8 -*-

import time


def _time_stamp(date, float_time):
    time_list = str(float_time).split(".")
    minutes = time_list[1]
    if minutes != 0:
        if len(minutes) == 1:
            minutes = minutes + "0"
        minutes = str(int(float(minutes) * 3 / 5))
    date = date + " " + time_list[0] + ":" + minutes + ":00"
    time_array = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    time_stamp = int(time.mktime(time_array))
    return time_stamp


if "__main__" == __name__:
    time_array = time.strptime("2017-10-20", "%Y-%m-%d")
    time_stamp = int(time.mktime(time_array)) + 24 * 60 * 60
    time_arrays = time.localtime(time_stamp)
    date = time.strftime("%Y-%m-%d", time_arrays)
    print date

"""
1508464980    2017-10-20 10:3:0
1508464800    2017-10-20 10:0:0
"""