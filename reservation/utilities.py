__author__ = 'pavanchitrapu'
import datetime

# These can actually be configurable, hard coding for now.
RESERVATION_START_TIME = (11, 0, 0) #Hours, mins, secs
RESERVATION_END_TIME = (10, 0, 0) #Hours, mins, secs

def normalize_date(__date, type='arrival'):

    """
    Normalize a date based on a given date and type.
    :param date: __date
    :param type: Values should be "arrival" or "departure", default value is "arrival"
    :return:
        A datetime.datetime object where it is normalized based on the RESERVATION_START_TIME, RESERVATION_END_TIME
        constants if __date is an instance of datetime.datetime,
        None otherwise
    """

    if isinstance(__date, datetime.datetime):
        # If type is arrival pass RESERVATION_START_TIME as tup else RESERVATION_END_TIME as tup
        if type == 'arrival':
            tup = RESERVATION_START_TIME
        else:
            tup = RESERVATION_END_TIME

        __date = datetime.datetime(__date.year, __date.month, __date.day,
                                           tup[0], tup[1], tup[2])

        return __date
    return None


def datetime_object(__date):
    """
    Given a naive instance of datetime, convert into datetime.datetime object
    :param date:
    :return:
    """
    if isinstance(__date, datetime.datetime):
        return datetime.datetime(__date.year, __date.month, __date.day, __date.hour, __date.minute, __date.second)
    return None
