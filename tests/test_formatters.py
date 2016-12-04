from datetime import datetime, date
from strainer import formatters


def test_datetime():
    formatter = formatters.format_datetime()
    assert formatter(None) == None
    assert formatter('1') == '1'
    assert formatter(1) == 1

    dt = datetime(1984, 6, 11, 12, 1)
    assert formatter(dt) == '1984-06-11T12:01:00'

    dt = date(1984, 6, 11)
    assert formatter(dt) == '1984-06-11'
