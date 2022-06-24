import datetime


def get_current_datetime() -> str:
    now = datetime.datetime.now()
    return now.strftime(get_date_format())


def get_date_format() -> str:
    return "%Y-%m-%d %H:%M:%S"


def to_string(timestamp) -> datetime:
    return timestamp.strftime(get_date_format())


def to_date(timestamp, format_from=None) -> datetime:
    if format_from is None:
        format_from = get_date_format()
    return datetime.datetime.strptime(timestamp, format_from)


def get_now() -> datetime:
    return to_date(to_string(datetime.datetime.now()))  # Todo: Make more efficient way to truncate seconds


def get_now_as_string() -> str:
    return to_string(get_now())


def compare(time1, time2):
    t1 = time1
    t2 = time2
    if isinstance(time1, str):
        if time1.lower() == "never":
            t1 = to_date("1970-01-01 00:00:00")
        else:
            t1 = to_date(time1)
    if isinstance(time2, str):
        if time2.lower() == "never":
            t2 = to_date("1970-01-01 00:00:00")
        else:
            t2 = to_date(time2)

    return (t2 - t1).total_seconds()
