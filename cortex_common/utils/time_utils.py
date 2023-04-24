"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from functools import wraps
import sys
import time
from typing import Any, Mapping, Iterable, Tuple, Dict

import arrow
import pandas as pd

from cortex_common.utils.object_utils import negate_dict_of_numbers

# pylint: disable=chained-comparison
# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name


__all__ = [
    "determine_weekly_ranges",
    "utc_timestamp",
    "timeit",
    "timeit_safely",
    "derive_hour_from_date",
    "derive_day_from_date",
    "remap_date_formats",
    "seconds_between_times",
    "fold_start_and_stop_time_tuples_into_dict",
    "oldest",
    "newest",
    "time_is_within",
]


def utc_timestamp() -> str:
    """
    Gets an ISO-8601 complient timestamp of the current UTC time.
    :return:
    """
    return str(arrow.utcnow())


def timeit(method):
    """
    A decorator that times the invocation of a method and returns it along with the response from the method as a tuple.
    :param method:
    :return:
    """  # pylint: disable=line-too-long

    @wraps(method)
    def timed(*args, **kw):
        t_s = time.time()
        result = method(*args, **kw)
        t_e = time.time()
        return "%2.2f" % (t_e - t_s), result

    return timed


def timeit_safely(precision=2):
    """
    Wrapper to time a method, even if it throws an exception.
    :param precision:
    :return:
    """

    def _timeit_safely(method):
        """
        A decorator that times the invocation of a method and returns it along with the response from the method as a tuple.
        :param method:
        :return:
        """  # pylint: disable=line-too-long

        @wraps(method)
        def timed(*args, **kw):
            t_s = time.time()
            result = None
            exception = None
            try:
                result = method(*args, **kw)
            except Exception:
                exception = sys.exc_info()
            t_e = time.time()
            return (f"%2.{precision}f" % (t_e - t_s), result, exception)

        return timed

    return _timeit_safely


def derive_hour_from_date(iso_timestamp: str) -> dict:
    """
    Enriches an ISO UTC Timestamp ...
    :param iso_timestamp:
    :return:
    """
    d = arrow.get(iso_timestamp)
    return {
        "hour_number": int(d.format("H")),
        "hour": d.format("hhA"),
        "timezone": d.format("ZZ"),
    }


def derive_day_from_date(iso_timestamp) -> str:
    """
    Derives the day from a ISO UTC Timestamp ...
    >>> derive_day_from_date('2019-03-27T21:18:21.760245+00:00') == '2019-03-27'
    :param iso_timestamp:
    :return:
    """
    return str(arrow.get(iso_timestamp).date())


def remap_date_formats(
    date_dict: Mapping[Any, arrow.Arrow], date_formats, original_format
) -> Mapping[Any, arrow.Arrow]:
    """
    Maps a date from on format to another ...

    :param date_dict:
    :param date_formats:
    :param original_format:
    :return:
    """
    return {
        k: arrow.get(v, original_format).format(date_formats.get(k, original_format))
        for (k, v) in date_dict.items()
    }


def seconds_between_times(
    arrow_time_a: arrow.Arrow, arrow_time_b: arrow.Arrow
) -> float:
    """
    Finds the amount of seconds between two arrow times ...
    :param arrow_time_a:
    :param arrow_time_b:
    :return:
    """
    return abs(arrow_time_a.float_timestamp - arrow_time_b.float_timestamp)


def fold_start_and_stop_time_tuples_into_dict(
    startTime_stopTime_tuples: Iterable[Tuple],
) -> Dict:
    """
    Helper to figure out max overlapping start and stop times ...
    >>> [
    >>>     ("2019-01-01T00:00:00Z", "2019-01-01T01:00:00Z"), ("2019-01-01T00:00:00Z", "2019-01-02T02:00:00Z")
    >>> ]
    >>> # into ...
    >>> { "2019-01-01T00:00:00Z": "2019-01-02T02:00:00Z"}

    :param startTime_stopTime_tuples:
    :return:
    """  # pylint: disable=line-too-long
    d: Dict = {}
    for start_time, stop_time in startTime_stopTime_tuples:
        if start_time in d:
            # Take the newer stop time ...
            if stop_time > d[start_time]:
                d[start_time] = stop_time
        else:
            d[start_time] = stop_time
    return d


def oldest(list_of_times: Iterable) -> object:
    """
    Find oldest time ...
    :param list_of_times:
    :return:
    """
    if not list_of_times:
        return None
    return sorted(list_of_times, key=lambda x: x)[0]


def newest(list_of_times: Iterable) -> object:
    """
    Find newest time ..
    :param list_of_times:
    :return:
    """
    if not list_of_times:
        return None
    return sorted(list_of_times, key=lambda x: x)[-1]


def time_is_within(time_to_check, time_to_shift, time_shifter):
    """
    Before and after ...
    :param time_to_check:
    :param time_to_shift:
    :param time_shifter:
    :return:
    """
    return (
        time_to_check >= time_to_shift.shift(**negate_dict_of_numbers(time_shifter))
        and time_to_check < time_to_shift
    ) or (
        time_to_check < time_to_shift.shift(**time_shifter)
        and time_to_check >= time_to_shift
    )


def determine_weekly_ranges(dates):
    """
    For the dates ... determine week ranges that capture all dates ...
    Assumption ... first item in range is included, but last is not ...
    :param dates:
    :return:
    """
    first_date = min(dates)
    last_date = max(dates)
    # Make sure beginning is sunday ... or move it back to last sunday ...
    # Move beginning to sunday ... if still same date ... use it ... (already sunday)
    #     If different date ... go back a week
    first_date_already_sunday = (
        first_date + pd.offsets.Week(n=0, weekday=6)
    ) == first_date
    sunday_of_range_start = (
        first_date
        if first_date_already_sunday
        else first_date + pd.offsets.Week(n=-1, weekday=6)
    )
    last_date_already_sunday = (
        last_date + pd.offsets.Week(n=0, weekday=6)
    ) == last_date
    sunday_of_range_end = (
        last_date + pd.offsets.Week(n=1, weekday=6)
        if last_date_already_sunday
        else last_date + pd.offsets.Week(n=0, weekday=6)
    )
    result_list = list(
        zip(
            pd.date_range(
                start=sunday_of_range_start,
                end=sunday_of_range_end,
                freq="W-SUN",
                closed=None,
            ),
            pd.date_range(
                start=sunday_of_range_start + pd.offsets.Week(n=1, weekday=6),
                end=sunday_of_range_end + pd.offsets.Week(n=1, weekday=6),
                freq="W-SUN",
                closed=None,
            ),
        )
    )
    # Drop last item from list
    return result_list[0:-1]
