from pytest import mark as pytest_mark
from pytest import raises as pytest_raises
from datetime import datetime

from apscheduler.triggers.crontab import CronTabTrigger, CronParserError


def calculate_next(expression, n, start_date, serializer):
    
    trigger = CronTabTrigger(
        expression=expression,
        start_date=start_date
    )
    
    if serializer:
        trigger = serializer.deserialize(serializer.serialize(trigger))

    now = start_date
    fire_times = []
    last = None
    for _ in range(n):
        last = now = trigger.get_next_fire_time(last, now)
        fire_times.append(now.isoformat())
    
    return fire_times
    

def run_expression(expression, expected, start_time, serializer):

    if not isinstance(expression, (list, tuple)):
        expression = [expression, ]
    
    for expr in expression:
        
        test = calculate_next(
            expression=expr,
            n=10,
            start_date=start_time,
            serializer=serializer
        )
        
        if sorted(test) != sorted(expected):
            test = 1
        
        assert sorted(test) == sorted(expected)  # , f'expression "{expression}" returned wrong next schedule times'


@pytest_mark.parametrize(
    'expression, expected, start_time',
    [
        (
            '0 0 0 L * ? *',
            [
                '2021-09-30T00:00:00+02:00',
                '2021-10-31T00:00:00+02:00',
                '2021-11-30T00:00:00+01:00',
                '2021-12-31T00:00:00+01:00',
                '2022-01-31T00:00:00+01:00',
                '2022-02-28T00:00:00+01:00',
                '2022-03-31T00:00:00+02:00',
                '2022-04-30T00:00:00+02:00',
                '2022-05-31T00:00:00+02:00',
                '2022-06-30T00:00:00+02:00'
            ],
            'default'
        ),
        (
            '0 0 0 1-4,12 * ? *',
            [
                '2021-10-01T00:00:00+02:00',
                '2021-10-02T00:00:00+02:00',
                '2021-10-03T00:00:00+02:00',
                '2021-10-04T00:00:00+02:00',
                '2021-10-12T00:00:00+02:00',
                '2021-11-01T00:00:00+01:00',
                '2021-11-02T00:00:00+01:00',
                '2021-11-03T00:00:00+01:00',
                '2021-11-04T00:00:00+01:00',
                '2021-11-12T00:00:00+01:00'
            ],
            'default'
        ),
        (
            '0 0 0 LW * ? *',
            [
                '2021-09-30T00:00:00+02:00',
                '2021-10-29T00:00:00+02:00',
                '2021-11-30T00:00:00+01:00',
                '2021-12-31T00:00:00+01:00',
                '2022-01-31T00:00:00+01:00',
                '2022-02-28T00:00:00+01:00',
                '2022-03-31T00:00:00+02:00',
                '2022-04-29T00:00:00+02:00',
                '2022-05-31T00:00:00+02:00',
                '2022-06-30T00:00:00+02:00'
            ],
            'default'
        ),
        (
            '0 0 0 2W * ? *',
            [
                '2021-10-01T00:00:00+02:00',
                '2021-11-02T00:00:00+01:00',
                '2021-12-02T00:00:00+01:00',
                '2022-01-03T00:00:00+01:00',
                '2022-02-02T00:00:00+01:00',
                '2022-03-02T00:00:00+01:00',
                '2022-04-01T00:00:00+02:00',
                '2022-05-02T00:00:00+02:00',
                '2022-06-02T00:00:00+02:00',
                '2022-07-01T00:00:00+02:00'
            ],
            'default'
        ),
        (
            '0 0 0 15W * ? *',
            [
                '2021-10-15T00:00:00+02:00',
                '2021-11-15T00:00:00+01:00',
                '2021-12-15T00:00:00+01:00',
                '2022-01-14T00:00:00+01:00',
                '2022-02-15T00:00:00+01:00',
                '2022-03-15T00:00:00+01:00',
                '2022-04-15T00:00:00+02:00',
                '2022-05-16T00:00:00+02:00',
                '2022-06-15T00:00:00+02:00',
                '2022-07-15T00:00:00+02:00',
            ],
            'default'
        ),
        (
            '0 0 0 15W,2W * ? *',
            [
                '2021-10-01T00:00:00+02:00',
                '2021-10-15T00:00:00+02:00',
                '2021-11-02T00:00:00+01:00',
                '2021-11-15T00:00:00+01:00',
                '2021-12-02T00:00:00+01:00',
                '2021-12-15T00:00:00+01:00',
                '2022-01-03T00:00:00+01:00',
                '2022-01-14T00:00:00+01:00',
                '2022-02-02T00:00:00+01:00',
                '2022-02-15T00:00:00+01:00'
            ],
            'default'
        ),
        (
            '0 0 0 L-5 * ? *',
            [
                '2021-09-25T00:00:00+02:00',
                '2021-10-26T00:00:00+02:00',
                '2021-11-25T00:00:00+01:00',
                '2021-12-26T00:00:00+01:00',
                '2022-01-26T00:00:00+01:00',
                '2022-02-23T00:00:00+01:00',
                '2022-03-26T00:00:00+01:00',
                '2022-04-25T00:00:00+02:00',
                '2022-05-26T00:00:00+02:00',
                '2022-06-25T00:00:00+02:00'
            ],
            'default'
        ),
        (
            '0 0 0/1 ? * * *',
            [
                '2021-03-28T01:00:00+01:00',
                '2021-03-28T02:00:00+01:00',
                '2021-03-28T03:00:00+02:00',
                '2021-03-28T04:00:00+02:00',
                '2021-03-28T05:00:00+02:00',
                '2021-03-28T06:00:00+02:00',
                '2021-03-28T07:00:00+02:00',
                '2021-03-28T08:00:00+02:00',
                '2021-03-28T09:00:00+02:00',
                '2021-03-28T10:00:00+02:00'
            ],
            datetime(2021, 3, 28)
        ),
        (
            '0 0 0/1 ? * * *',
            [
                '2021-10-31T01:00:00+02:00',
                '2021-10-31T02:00:00+02:00',
                '2021-10-31T03:00:00+01:00',
                '2021-10-31T04:00:00+01:00',
                '2021-10-31T05:00:00+01:00',
                '2021-10-31T06:00:00+01:00',
                '2021-10-31T07:00:00+01:00',
                '2021-10-31T08:00:00+01:00',
                '2021-10-31T09:00:00+01:00',
                '2021-10-31T10:00:00+01:00'
            ],
            datetime(2021, 10, 31)
        ),
        (
            [
                '0 0 0 ? * sun/1 *',
                '0 0 0 ? * 1/1 *',
                '0 0 0 ? * * *',
                '0 0 0 * * * *',
                '0 0 0 * * ? *',
                '0 0 0 ? * ? *',
                '0 0 0 ? * */1 *',
            ],
            [
                '2021-09-19T00:00:00+02:00',
                '2021-09-20T00:00:00+02:00',
                '2021-09-21T00:00:00+02:00',
                '2021-09-22T00:00:00+02:00',
                '2021-09-23T00:00:00+02:00',
                '2021-09-24T00:00:00+02:00',
                '2021-09-25T00:00:00+02:00',
                '2021-09-26T00:00:00+02:00',
                '2021-09-27T00:00:00+02:00',
                '2021-09-28T00:00:00+02:00'
            ],
            datetime(2021, 9, 18)
        ),
        (
            '0 0 0 ? * 3/1 *',
            [
                '2021-09-21T00:00:00+02:00',
                '2021-09-22T00:00:00+02:00',
                '2021-09-23T00:00:00+02:00',
                '2021-09-24T00:00:00+02:00',
                '2021-09-25T00:00:00+02:00',
                '2021-09-28T00:00:00+02:00',
                '2021-09-29T00:00:00+02:00',
                '2021-09-30T00:00:00+02:00',
                '2021-10-01T00:00:00+02:00',
                '2021-10-02T00:00:00+02:00'
            ],
            datetime(2021, 9, 18)
        ),
        (
            '0 0 0 ? * 1/7 *',
            [
                '2021-09-19T00:00:00+02:00',
                '2021-09-26T00:00:00+02:00',
                '2021-10-03T00:00:00+02:00',
                '2021-10-10T00:00:00+02:00',
                '2021-10-17T00:00:00+02:00',
                '2021-10-24T00:00:00+02:00',
                '2021-10-31T00:00:00+02:00',
                '2021-11-07T00:00:00+01:00',
                '2021-11-14T00:00:00+01:00',
                '2021-11-21T00:00:00+01:00'
            ],
            datetime(2021, 9, 18)
        ),
        (
            [
                '0 0 0 ? * mon-tue *',
                '0 0 0 ? * mon-tue/1 *',
                '0 0 0 ? * mon,tue *',
                '0 0 0 ? * 2-3 *',
                '0 0 0 ? * 2-3/1 *'
            ],
            [
                '2021-09-20T00:00:00+02:00',
                '2021-09-21T00:00:00+02:00',
                '2021-09-27T00:00:00+02:00',
                '2021-09-28T00:00:00+02:00',
                '2021-10-04T00:00:00+02:00',
                '2021-10-05T00:00:00+02:00',
                '2021-10-11T00:00:00+02:00',
                '2021-10-12T00:00:00+02:00',
                '2021-10-18T00:00:00+02:00',
                '2021-10-19T00:00:00+02:00'
            ],
            datetime(2021, 9, 18)
        ),
        (
            [
                '0 0 0 ? * mon-thu/2 *',
                '0 0 0 ? * 2-4/2 *',
                '0 0 0 ? * mon,wed *'
            ],
            [
                '2021-09-20T00:00:00+02:00',
                '2021-09-22T00:00:00+02:00',
                '2021-09-27T00:00:00+02:00',
                '2021-09-29T00:00:00+02:00',
                '2021-10-04T00:00:00+02:00',
                '2021-10-06T00:00:00+02:00',
                '2021-10-11T00:00:00+02:00',
                '2021-10-13T00:00:00+02:00',
                '2021-10-18T00:00:00+02:00',
                '2021-10-20T00:00:00+02:00'
            ],
            datetime(2021, 9, 18)
        ),
        (
            [
                '0 0 0 ? * 1/2 *',
                '0 0 0 ? * sun/2 *'
            ],
            [
                '2021-09-19T00:00:00+02:00',
                '2021-09-21T00:00:00+02:00',
                '2021-09-23T00:00:00+02:00',
                '2021-09-25T00:00:00+02:00',
                '2021-09-26T00:00:00+02:00',
                '2021-09-28T00:00:00+02:00',
                '2021-09-30T00:00:00+02:00',
                '2021-10-02T00:00:00+02:00',
                '2021-10-03T00:00:00+02:00',
                '2021-10-05T00:00:00+02:00'
            ],
            datetime(2021, 9, 18)
        ),
        (
                [
                    '0 0 0 ? * 2/2 *',
                    '0 0 0 ? * mon/2 *'
                ],
                [
                    '2021-09-20T00:00:00+02:00',
                    '2021-09-22T00:00:00+02:00',
                    '2021-09-24T00:00:00+02:00',
                    '2021-09-27T00:00:00+02:00',
                    '2021-09-29T00:00:00+02:00',
                    '2021-10-01T00:00:00+02:00',
                    '2021-10-04T00:00:00+02:00',
                    '2021-10-06T00:00:00+02:00',
                    '2021-10-08T00:00:00+02:00',
                    '2021-10-11T00:00:00+02:00'
                ],
                datetime(2021, 9, 18)
        ),
        (
                [
                    '0 0 0 ? * 1st-mon *',
                    '0 0 0 ? * 1st-2 *',
                    '0 0 0 ? * mon#1 *',
                    '0 0 0 ? * 2#1 *'
                ],
                [
                    '2021-10-04T00:00:00+02:00',
                    '2021-11-01T00:00:00+01:00',
                    '2021-12-06T00:00:00+01:00',
                    '2022-01-03T00:00:00+01:00',
                    '2022-02-07T00:00:00+01:00',
                    '2022-03-07T00:00:00+01:00',
                    '2022-04-04T00:00:00+02:00',
                    '2022-05-02T00:00:00+02:00',
                    '2022-06-06T00:00:00+02:00',
                    '2022-07-04T00:00:00+02:00'
                ],
                datetime(2021, 9, 18)
        ),
        (
                [
                    '0 0 0 ? * 5L *',
                    '0 0 0 ? * thuL *',
                    '0 0 0 ? * last-thu *',
                    '0 0 0 ? * last-5 *'
                ],
                [
                    '2021-09-30T00:00:00+02:00',
                    '2021-10-28T00:00:00+02:00',
                    '2021-11-25T00:00:00+01:00',
                    '2021-12-30T00:00:00+01:00',
                    '2022-01-27T00:00:00+01:00',
                    '2022-02-24T00:00:00+01:00',
                    '2022-03-31T00:00:00+02:00',
                    '2022-04-28T00:00:00+02:00',
                    '2022-05-26T00:00:00+02:00',
                    '2022-06-30T00:00:00+02:00'
                ],
                datetime(2021, 9, 18)
        ),
        (
            [
                '0 0 0 ? * 4#2 *',
                '0 0 0 ? * wed#2 *',
                '0 0 0 ? * 2nd-wed *',
                '0 0 0 ? * 2nd-4 *'
            ],
            [
                '2021-10-13T00:00:00+02:00',
                '2021-11-10T00:00:00+01:00',
                '2021-12-08T00:00:00+01:00',
                '2022-01-12T00:00:00+01:00',
                '2022-02-09T00:00:00+01:00',
                '2022-03-09T00:00:00+01:00',
                '2022-04-13T00:00:00+02:00',
                '2022-05-11T00:00:00+02:00',
                '2022-06-08T00:00:00+02:00',
                '2022-07-13T00:00:00+02:00'
            ],
            datetime(2021, 9, 18)
        ),
        (
                [
                    '0 0 0 ? * mon,wed *',
                    '0 0 0 ? * 2,4 *',
                    '0 0 0 ? * 2,wed *',
                    '0 0 0 ? * mon,4 *'
                ],
                [
                    '2021-09-20T00:00:00+02:00',
                    '2021-09-22T00:00:00+02:00',
                    '2021-09-27T00:00:00+02:00',
                    '2021-09-29T00:00:00+02:00',
                    '2021-10-04T00:00:00+02:00',
                    '2021-10-06T00:00:00+02:00',
                    '2021-10-11T00:00:00+02:00',
                    '2021-10-13T00:00:00+02:00',
                    '2021-10-18T00:00:00+02:00',
                    '2021-10-20T00:00:00+02:00'
                ],
                datetime(2021, 9, 18)
        )
    ],
    ids=[
        'day_of_month_last',
        'day_of_month_specific_days',
        'day_of_month_last_business_day',
        'day_of_month_nearest_business_day_2',
        'day_of_month_nearest_business_day_15',
        'day_of_month_nearest_business_day_15_2',
        'day_of_month_5_days_before_end_of_month',
        'hour_day_light_saving_march_test',
        'hour_day_light_saving_october_test',
        'day_of_week_every_day',
        'day_of_week_every_day_start_not_sun',
        'day_of_week_every_7th_day',
        'day_of_week_range_mon_tue_one',
        'day_of_week_range_mon_tue_two',
        'day_of_week_every_second_day_sun',
        'day_of_week_every_second_day_mon',
        'day_of_week_first_mon_of_month',
        'day_of_week_last_thu_of_month',
        'day_of_week_second_wed_of_month',
        'day_of_week_comma_mon_wed'
        
    ]
)
def test_crontab_trigger_1(expression, expected, start_time, serializer, timezone):
    
    if start_time == 'default':
        start_time = datetime(2021, 9, 19)
    start_time = start_time.astimezone(timezone)
    
    run_expression(
        expression=expression,
        expected=expected,
        serializer=serializer,
        start_time=start_time
    )


@pytest_mark.parametrize(
    'expression, expected',
    [
        (
            '0 0 0 ? * mon-tue/7 *',
            (
                ('expression', '0 0 0 ? * mon-tue/7 *'),
                ('field_index', 6),
                ('field_name', 'day_of_week'),
                ('reasons', ['the step value 7 is higher than the range of days mon-tue']),
                ('sequence', 'mon-tue/7')
            )
        ),
        (
            '0 0 0 ? * mon-tue/55 *',
            (
                ('expression', '0 0 0 ? * mon-tue/55 *'),
                ('field_index', 6),
                ('field_name', 'day_of_week'),
                ('reasons', ['the step value 55 is higher than the range of days mon-tue']),
                ('sequence', 'mon-tue/55')
            )
        ),
        (
            '0 0 0 ? * 4-sat/55 *',
            (
                ('expression', '0 0 0 ? * 4-sat/55 *'),
                ('field_index', 6),
                ('field_name', 'day_of_week'),
                ('reasons', ['the step value 55 is higher than the range of days 4-sat']),
                ('sequence', '4-sat/55')
            )
        ),
        (
            '0 0 0 ? * bla-blu/55 *',
            (
                ('expression', '0 0 0 ? * bla-blu/55 *'),
                ('field_index', 6),
                ('field_name', 'day_of_week'),
                ('reasons', ['Invalid weekday name "bla"']),
                ('sequence', 'bla-blu/55')
            )
        ),
        (
            '0 0 0 ? * 7-1/55 *',
            (
                ('expression', '0 0 0 ? * 7-1/55 *'),
                ('field_index', 6),
                ('field_name', 'day_of_week'),
                ('reasons', ['The first value 7 is higher than the last value 1']),
                ('sequence', '7-1/55')
            )
        )
    ],
    ids=[
        'exception_range_7_higher',
        'exception_range_55_higher',
        'exception_range_55_higher_2',
        'exception_wrong_day_names',
        'exception_first_higher_than_last',
    ]
)
def test_trigger_exception(expression, expected):
    
    exc = pytest_raises(
        CronParserError,
        CronTabTrigger,
        expression=expression
    ).value

    for key, val in expected:
        
        assert getattr(exc, key) == val