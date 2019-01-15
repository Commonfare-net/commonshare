# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import datetime
import pickle
import unittest
import aniso8601
import dateutil.relativedelta

from aniso8601 import compat
from aniso8601.builder import (BaseTimeBuilder, PythonTimeBuilder,
                               RelativeTimeBuilder, TupleBuilder, UTCOffset)
from aniso8601.exceptions import (DayOutOfBoundsError, HoursOutOfBoundsError,
                                  ISOFormatError, LeapSecondError,
                                  MidnightBoundsError, MinutesOutOfBoundsError,
                                  RelativeValueError, SecondsOutOfBoundsError,
                                  WeekOutOfBoundsError, YearOutOfBoundsError)
from aniso8601.tests.compat import mock

class TestBaseTimeBuilder(unittest.TestCase):
    def test_build_date(self):
        with self.assertRaises(NotImplementedError):
            BaseTimeBuilder.build_date()

    def test_build_time(self):
        with self.assertRaises(NotImplementedError):
            BaseTimeBuilder.build_time()

    def test_build_datetime(self):
        with self.assertRaises(NotImplementedError):
            BaseTimeBuilder.build_datetime(None, None)

    def test_build_duration(self):
        with self.assertRaises(NotImplementedError):
            BaseTimeBuilder.build_duration()

    def test_build_interval(self):
        with self.assertRaises(NotImplementedError):
            BaseTimeBuilder.build_interval()

    def test_build_repeating_interval(self):
        with self.assertRaises(NotImplementedError):
            BaseTimeBuilder.build_repeating_interval()

    def test_build_timezone(self):
        with self.assertRaises(NotImplementedError):
            BaseTimeBuilder.build_timezone()

    def test_cast(self):
        self.assertEqual(BaseTimeBuilder.cast('1', int), 1)
        self.assertEqual(BaseTimeBuilder.cast('-2', int), -2)
        self.assertEqual(BaseTimeBuilder.cast('3', float), float(3))
        self.assertEqual(BaseTimeBuilder.cast('-4', float), float(-4))
        self.assertEqual(BaseTimeBuilder.cast('5.6', float), 5.6)
        self.assertEqual(BaseTimeBuilder.cast('-7.8', float), -7.8)

    def test_cast_exception(self):
        with self.assertRaises(ISOFormatError):
            BaseTimeBuilder.cast('asdf', int)

        with self.assertRaises(ISOFormatError):
            BaseTimeBuilder.cast('asdf', float)

    def test_cast_caughtexception(self):
        def tester(value):
            raise RuntimeError

        with self.assertRaises(ISOFormatError):
            BaseTimeBuilder.cast('asdf', tester,
                                 caughtexceptions=(RuntimeError,))

    def test_cast_thrownexception(self):
        with self.assertRaises(RuntimeError):
            BaseTimeBuilder.cast('asdf', int,
                                 thrownexception=RuntimeError)

    def test_build_object(self):
        datetest = (('1', '2', '3', '4', '5', '6', 'date'),
                    {'YYYY': '1', 'MM': '2', 'DD': '3',
                     'Www': '4', 'D': '5', 'DDD': '6'})

        timetest = (('1', '2', '3',
                     (False, False, '4', '5', 'tz name', 'timezone'),
                     'time'),
                    {'hh': '1', 'mm': '2', 'ss': '3',
                     'tz': (False, False, '4', '5', 'tz name', 'timezone')})

        datetimetest = ((('1', '2', '3', '4', '5', '6', 'date'),
                         ('7', '8', '9',
                          (True, False, '10', '11', 'tz name', 'timezone'),
                          'time'),
                         'datetime'),
                        (('1', '2', '3', '4', '5', '6', 'date'),
                         ('7', '8', '9',
                          (True, False, '10', '11', 'tz name', 'timezone'),
                          'time')))

        durationtest = (('1', '2', '3', '4', '5', '6', '7', 'duration'),
                        {'PnY': '1', 'PnM': '2', 'PnW': '3', 'PnD': '4',
                         'TnH': '5', 'TnM': '6', 'TnS': '7'})

        intervaltests = (((('1', '2', '3', '4', '5', '6', 'date'),
                           ('7', '8', '9', '10', '11', '12', 'date'),
                           None, 'interval'),
                          {'start': ('1', '2', '3', '4', '5', '6', 'date'),
                           'end': ('7', '8', '9', '10', '11', '12', 'date'),
                           'duration': None}),
                         ((('1', '2', '3', '4', '5', '6', 'date'),
                           None,
                           ('7', '8', '9', '10', '11', '12', '13', 'duration'),
                           'interval'),
                          {'start': ('1', '2', '3', '4', '5', '6', 'date'),
                           'end': None,
                           'duration': ('7', '8', '9', '10', '11', '12', '13',
                                        'duration')}),
                         ((None,
                           ('1', '2', '3',
                            (True, False, '4', '5', 'tz name', 'timezone'),
                            'time'),
                           ('6', '7', '8', '9', '10', '11', '12', 'duration'),
                           'interval'),
                          {'start': None,
                           'end': ('1', '2', '3',
                                   (True, False, '4', '5', 'tz name',
                                    'timezone'),
                                   'time'),
                           'duration': ('6', '7', '8', '9', '10', '11', '12',
                                        'duration')}))

        repeatingintervaltests = (((True,
                                    None,
                                    (('1', '2', '3', '4', '5', '6', 'date'),
                                     ('7', '8', '9', '10', '11', '12', 'date'),
                                     None, 'interval'), 'repeatinginterval'),
                                   {'R': True,
                                    'Rnn': None,
                                    'interval': (('1', '2', '3',
                                                  '4', '5', '6', 'date'),
                                                 ('7', '8', '9',
                                                  '10', '11', '12', 'date'),
                                                 None, 'interval')}),
                                  ((False,
                                    '1',
                                    ((('2', '3', '4', '5', '6', '7', 'date'),
                                      ('8', '9', '10', None, 'time'),
                                      'datetime'),
                                     (('11', '12', '13', '14', '15', '16',
                                       'date'),
                                      ('17', '18', '19', None, 'time'),
                                      'datetime'),
                                     None, 'interval'), 'repeatinginterval'),
                                   {'R':False,
                                    'Rnn': '1',
                                    'interval': ((('2', '3', '4',
                                                   '5', '6', '7', 'date'),
                                                  ('8', '9', '10', None,
                                                   'time'), 'datetime'),
                                                 (('11', '12', '13',
                                                   '14', '15', '16', 'date'),
                                                  ('17', '18', '19', None,
                                                   'time'), 'datetime'),
                                                 None, 'interval')}))

        timezonetest = ((False, False, '1', '2', '+01:02', 'timezone'),
                        {'negative': False, 'Z': False,
                         'hh': '1', 'mm': '2', 'name': '+01:02'})

        with mock.patch.object(aniso8601.builder.BaseTimeBuilder,
                               'build_date') as mock_build:
            mock_build.return_value = datetest[0]

            result = BaseTimeBuilder._build_object(datetest[0])

            self.assertEqual(result, datetest[0])
            mock_build.assert_called_once_with(**datetest[1])

        with mock.patch.object(aniso8601.builder.BaseTimeBuilder,
                               'build_time') as mock_build:
            mock_build.return_value = timetest[0]

            result = BaseTimeBuilder._build_object(timetest[0])

            self.assertEqual(result, timetest[0])
            mock_build.assert_called_once_with(**timetest[1])

        with mock.patch.object(aniso8601.builder.BaseTimeBuilder,
                               'build_datetime') as mock_build:
            mock_build.return_value = datetimetest[0]

            result = BaseTimeBuilder._build_object(datetimetest[0])

            self.assertEqual(result, datetimetest[0])
            mock_build.assert_called_once_with(*datetimetest[1])

        with mock.patch.object(aniso8601.builder.BaseTimeBuilder,
                               'build_duration') as mock_build:
            mock_build.return_value = durationtest[0]

            result = BaseTimeBuilder._build_object(durationtest[0])

            self.assertEqual(result, durationtest[0])
            mock_build.assert_called_once_with(**durationtest[1])

        for intervaltest in intervaltests:
            with mock.patch.object(aniso8601.builder.BaseTimeBuilder,
                                   'build_interval') as mock_build:
                mock_build.return_value = intervaltest[0]

                result = BaseTimeBuilder._build_object(intervaltest[0])

                self.assertEqual(result, intervaltest[0])
                mock_build.assert_called_once_with(**intervaltest[1])

        for repeatingintervaltest in repeatingintervaltests:
            with mock.patch.object(aniso8601.builder.BaseTimeBuilder,
                                   'build_repeating_interval') as mock_build:
                mock_build.return_value = repeatingintervaltest[0]

                result = BaseTimeBuilder._build_object(repeatingintervaltest[0])

                self.assertEqual(result, repeatingintervaltest[0])
                mock_build.assert_called_once_with(**repeatingintervaltest[1])

        with mock.patch.object(aniso8601.builder.BaseTimeBuilder,
                               'build_timezone') as mock_build:
            mock_build.return_value = timezonetest[0]

            result = BaseTimeBuilder._build_object(timezonetest[0])

            self.assertEqual(result, timezonetest[0])
            mock_build.assert_called_once_with(**timezonetest[1])

class TestTupleBuilder(unittest.TestCase):
    def test_build_date(self):
        datetuple = TupleBuilder.build_date()

        self.assertEqual(datetuple, (None, None, None,
                                     None, None, None,
                                     'date'))

        datetuple = TupleBuilder.build_date(YYYY='1', MM='2', DD='3',
                                            Www='4', D='5', DDD='6')

        self.assertEqual(datetuple, ('1', '2', '3',
                                     '4', '5', '6',
                                     'date'))

    def test_build_time(self):
        testtuples = (({}, (None, None, None, None, 'time')),
                      ({'hh': '1', 'mm': '2', 'ss': '3', 'tz': None},
                       ('1', '2', '3', None, 'time')),
                      ({'hh': '1', 'mm': '2', 'ss': '3', 'tz': (False, False,
                                                                '4', '5',
                                                                'tz name',
                                                                'timezone')},
                       ('1', '2', '3', (False, False, '4', '5',
                                        'tz name', 'timezone'),
                        'time')))

        for testtuple in testtuples:
            self.assertEqual(TupleBuilder.build_time(**testtuple[0]),
                             testtuple[1])

    def test_build_datetime(self):
        testtuples = (({'date': ('1', '2', '3', '4', '5', '6', 'date'),
                        'time': ('7', '8', '9', None, 'time')},
                       (('1', '2', '3', '4', '5', '6', 'date'),
                        ('7', '8', '9', None, 'time'),
                        'datetime')),
                      ({'date': ('1', '2', '3', '4', '5', '6', 'date'),
                        'time': ('7', '8', '9',
                                 (True, False, '10', '11', 'tz name',
                                  'timezone'),
                                 'time')},
                       (('1', '2', '3', '4', '5', '6', 'date'),
                        ('7', '8', '9',
                         (True, False, '10', '11', 'tz name',
                          'timezone'),
                         'time'), 'datetime')))

        for testtuple in testtuples:
            self.assertEqual(TupleBuilder.build_datetime(**testtuple[0]),
                             testtuple[1])

    def test_build_duration(self):
        testtuples = (({}, (None, None, None, None, None, None, None,
                            'duration')),
                      ({'PnY': '1', 'PnM': '2', 'PnW': '3', 'PnD': '4',
                        'TnH': '5', 'TnM': '6', 'TnS': '7'},
                       ('1', '2', '3', '4',
                        '5', '6', '7',
                        'duration')))

        for testtuple in testtuples:
            self.assertEqual(TupleBuilder.build_duration(**testtuple[0]),
                             testtuple[1])

    def test_build_interval(self):
        testtuples = (({}, (None, None, None, 'interval')),
                      ({'start': ('1', '2', '3', '4', '5', '6', 'date'),
                        'end': ('7', '8', '9', '10', '11', '12', 'date')},
                       (('1', '2', '3', '4', '5', '6', 'date'),
                        ('7', '8', '9', '10', '11', '12', 'date'),
                        None, 'interval')),
                      ({'start': ('1', '2', '3',
                                  (True, False, '7', '8', 'tz name',
                                   'timezone'),
                                  'time'),
                        'end': ('4', '5', '6',
                                (False, False, '9', '10', 'tz name',
                                 'timezone'),
                                'time')},
                       (('1', '2', '3',
                         (True, False, '7', '8', 'tz name',
                          'timezone'),
                         'time'),
                        ('4', '5', '6',
                         (False, False, '9', '10', 'tz name',
                          'timezone'),
                         'time'),
                        None, 'interval')),
                      ({'start': (('1', '2', '3', '4', '5', '6', 'date'),
                                  ('7', '8', '9',
                                   (True, False, '10', '11', 'tz name',
                                    'timezone'),
                                   'time'),
                                  'datetime'),
                        'end': (('12', '13', '14', '15', '16', '17', 'date'),
                                ('18', '19', '20',
                                 (False, False, '21', '22', 'tz name',
                                  'timezone'),
                                 'time'),
                                'datetime')},
                       ((('1', '2', '3', '4', '5', '6', 'date'),
                         ('7', '8', '9',
                          (True, False, '10', '11', 'tz name',
                           'timezone'),
                          'time'),
                         'datetime'),
                        (('12', '13', '14', '15', '16', '17', 'date'),
                         ('18', '19', '20',
                          (False, False, '21', '22', 'tz name',
                           'timezone'),
                          'time'),
                         'datetime'),
                        None, 'interval')),
                      ({'start': ('1', '2', '3', '4', '5', '6', 'date'),
                        'end': None,
                        'duration': ('7', '8', '9', '10', '11', '12', '13',
                                     'duration')},
                       (('1', '2', '3', '4', '5', '6', 'date'),
                        None,
                        ('7', '8', '9', '10', '11', '12', '13',
                         'duration'),
                        'interval')),
                      ({'start': None,
                        'end': ('1', '2', '3',
                                (True, False, '4', '5', 'tz name',
                                 'timezone'),
                                'time'),
                        'duration': ('6', '7', '8', '9', '10', '11', '12',
                                     'duration')},
                       (None,
                        ('1', '2', '3',
                         (True, False, '4', '5', 'tz name',
                          'timezone'),
                         'time'),
                        ('6', '7', '8', '9', '10', '11', '12',
                         'duration'),
                        'interval')))

        for testtuple in testtuples:
            self.assertEqual(TupleBuilder.build_interval(**testtuple[0]),
                             testtuple[1])

    def test_build_repeating_interval(self):
        testtuples = (({}, (None, None, None, 'repeatinginterval')),
                      ({'R': True,
                        'interval':(('1', '2', '3', '4', '5', '6', 'date'),
                                    ('7', '8', '9', '10', '11', '12', 'date'),
                                    None, 'interval')},
                       (True, None, (('1', '2', '3', '4', '5', '6', 'date'),
                                     ('7', '8', '9', '10', '11', '12', 'date'),
                                     None, 'interval'),
                        'repeatinginterval')),
                      ({'R':False, 'Rnn': '1',
                        'interval': ((('2', '3', '4', '5', '6', '7',
                                       'date'),
                                      ('8', '9', '10', None, 'time'),
                                      'datetime'),
                                     (('11', '12', '13', '14', '15', '16',
                                       'date'),
                                      ('17', '18', '19', None, 'time'),
                                      'datetime'),
                                     None, 'interval')},
                       (False, '1',
                        ((('2', '3', '4', '5', '6', '7',
                           'date'),
                          ('8', '9', '10', None, 'time'),
                          'datetime'),
                         (('11', '12', '13', '14', '15', '16',
                           'date'),
                          ('17', '18', '19', None, 'time'),
                          'datetime'),
                         None, 'interval'),
                        'repeatinginterval')))

        for testtuple in testtuples:
            result = TupleBuilder.build_repeating_interval(**testtuple[0])
            self.assertEqual(result, testtuple[1])

    def test_build_timezone(self):
        testtuples = (({}, (None, None, None, None, '', 'timezone')),
                      ({'negative': False, 'Z': True, 'name': 'UTC'},
                       (False, True, None, None, 'UTC', 'timezone')),
                      ({'negative': False, 'Z': False, 'hh': '1', 'mm': '2',
                        'name': '+01:02'},
                       (False, False, '1', '2', '+01:02', 'timezone')),
                      ({'negative': True, 'Z': False, 'hh': '1', 'mm': '2',
                        'name': '-01:02'},
                       (True, False, '1', '2', '-01:02', 'timezone')))

        for testtuple in testtuples:
            result = TupleBuilder.build_timezone(**testtuple[0])
            self.assertEqual(result, testtuple[1])

class TestPythonTimeBuilder(unittest.TestCase):
    def test_build_date(self):
        testtuples = (({'YYYY': '2013', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(2013, 1, 1)),
                      ({'YYYY': '0001', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(1, 1, 1)),
                      ({'YYYY': '1900', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(1900, 1, 1)),
                      ({'YYYY': '1981', 'MM': '04', 'DD': '05', 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(1981, 4, 5)),
                      ({'YYYY': '1981', 'MM': '04', 'DD': None, 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(1981, 4, 1)),
                      ({'YYYY': '1981', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': '095'},
                       datetime.date(1981, 4, 5)),
                      ({'YYYY': '1981', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': '365'},
                       datetime.date(1981, 12, 31)),
                      ({'YYYY': '1980', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': '366'},
                       datetime.date(1980, 12, 31)),
                      #Make sure we shift in zeros
                      ({'YYYY': '1', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(1000, 1, 1)),
                      ({'YYYY': '12', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(1200, 1, 1)),
                      ({'YYYY': '123', 'MM': None, 'DD': None, 'Www': None,
                        'D': None, 'DDD': None},
                       datetime.date(1230, 1, 1)))

        for testtuple in testtuples:
            result = PythonTimeBuilder.build_date(**testtuple[0])
            self.assertEqual(result, testtuple[1])

        #Test weekday
        testtuples = (({'YYYY': '2004', 'MM': None, 'DD': None, 'Www': '53',
                        'D': None, 'DDD': None},
                       datetime.date(2004, 12, 27), 0),
                      ({'YYYY': '2009', 'MM': None, 'DD': None, 'Www': '01',
                        'D': None, 'DDD': None},
                       datetime.date(2008, 12, 29), 0),
                      ({'YYYY': '2010', 'MM': None, 'DD': None, 'Www': '01',
                        'D': None, 'DDD': None},
                       datetime.date(2010, 1, 4), 0),
                      ({'YYYY': '2009', 'MM': None, 'DD': None, 'Www': '53',
                        'D': None, 'DDD': None},
                       datetime.date(2009, 12, 28), 0),
                      ({'YYYY': '2009', 'MM': None, 'DD': None, 'Www': '01',
                        'D': '1', 'DDD': None},
                       datetime.date(2008, 12, 29), 0),
                      ({'YYYY': '2009', 'MM': None, 'DD': None, 'Www': '53',
                        'D': '7', 'DDD': None},
                       datetime.date(2010, 1, 3), 6),
                      ({'YYYY': '2010', 'MM': None, 'DD': None, 'Www': '01',
                        'D': '1', 'DDD': None},
                       datetime.date(2010, 1, 4), 0),
                      ({'YYYY': '2004', 'MM': None, 'DD': None, 'Www': '53',
                        'D': '6', 'DDD': None},
                       datetime.date(2005, 1, 1), 5))

        for testtuple in testtuples:
            result = PythonTimeBuilder.build_date(**testtuple[0])
            self.assertEqual(result, testtuple[1])
            self.assertEqual(result.weekday(), testtuple[2])

    def test_build_date_bounds_checking(self):
        #0 isn't a valid week number
        with self.assertRaises(WeekOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='2003', Www='00')

        #Week must not be larger than 53
        with self.assertRaises(WeekOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='2004', Www='54')

        #0 isn't a valid day number
        with self.assertRaises(DayOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='2001', Www='02', D='0')

        #Day must not be larger than 7
        with self.assertRaises(DayOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='2001', Www='02', D='8')

        #0 isn't a valid year for a Python builder
        with self.assertRaises(YearOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='0000')

        with self.assertRaises(DayOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='1981', DDD='000')

        #Day 366 is only valid on a leap year
        with self.assertRaises(DayOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='1981', DDD='366')

        #Day must me 365, or 366, not larger
        with self.assertRaises(DayOutOfBoundsError):
            PythonTimeBuilder.build_date(YYYY='1981', DDD='367')

    def test_build_time(self):
        testtuples = (({}, datetime.time()),
                      ({'hh': '1', 'mm': '23'},
                       datetime.time(hour=1, minute=23)),
                      ({'hh': '1', 'mm': '23', 'ss': '45'},
                       datetime.time(hour=1, minute=23, second=45)),
                      ({'hh': '1', 'mm': '23.4567'},
                       datetime.time(hour=1, minute=23, second=27,
                                     microsecond=402000)),
                      ({'hh': '23', 'mm': '21', 'ss': '28.512400'},
                       datetime.time(hour=23, minute=21, second=28,
                                     microsecond=512400)),
                      ({'hh': '14', 'mm': '43', 'ss': '59.9999997'},
                       datetime.time(hour=14, minute=43, second=59,
                                     microsecond=999999)),
                      ({'hh': '12.5'},
                       datetime.time(hour=12, minute=30)),
                      ({'hh': '24'}, datetime.time(hour=0)),
                      ({'hh': '24', 'mm': '00'}, datetime.time(hour=0)),
                      ({'hh': '24', 'mm': '00', 'ss': '00'},
                       datetime.time(hour=0)),
                      ({'tz': (False, None, '00', '00', 'UTC', 'timezone')},
                       datetime.time(tzinfo=UTCOffset(name='UTC', minutes=0))),
                      ({'hh': '23', 'mm': '21', 'ss': '28.512400',
                        'tz': (False, None, '00', '00', '+00:00', 'timezone')},
                       datetime.time(hour=23, minute=21, second=28,
                                     microsecond=512400,
                                     tzinfo=UTCOffset(name='+00:00',
                                                      minutes=0))),
                      ({'hh': '1', 'mm': '23',
                        'tz': (False, None, '01', '00', '+1', 'timezone')},
                       datetime.time(hour=1, minute=23,
                                     tzinfo=UTCOffset(name='+1',
                                                      minutes=60))),
                      ({'hh': '1', 'mm': '23.4567',
                        'tz': (True, None, '01', '00', '-1', 'timezone')},
                       datetime.time(hour=1, minute=23, second=27,
                                     microsecond=402000,
                                     tzinfo=UTCOffset(name='-1',
                                                      minutes=-60))),
                      ({'hh': '23', 'mm': '21', 'ss': '28.512400',
                        'tz': (False, None, '01', '30', '+1:30', 'timezone')},
                       datetime.time(hour=23, minute=21, second=28,
                                     microsecond=512400,
                                     tzinfo=UTCOffset(name='+1:30',
                                                      minutes=90))),
                      ({'hh': '23', 'mm': '21', 'ss': '28.512400',
                        'tz': (False, None, '11', '15', '+11:15', 'timezone')},
                       datetime.time(hour=23, minute=21, second=28,
                                     microsecond=512400,
                                     tzinfo=UTCOffset(name='+11:15',
                                                      minutes=675))),
                      ({'hh': '23', 'mm': '21', 'ss': '28.512400',
                        'tz': (False, None, '12', '34', '+12:34', 'timezone')},
                       datetime.time(hour=23, minute=21, second=28,
                                     microsecond=512400,
                                     tzinfo=UTCOffset(name='+12:34',
                                                      minutes=754))),
                      ({'hh': '23', 'mm': '21', 'ss': '28.512400',
                        'tz': (False, None, '00', '00', 'UTC', 'timezone')},
                       datetime.time(hour=23, minute=21, second=28,
                                     microsecond=512400,
                                     tzinfo=UTCOffset(name='UTC',
                                                      minutes=0))))

        for testtuple in testtuples:
            result = PythonTimeBuilder.build_time(**testtuple[0])
            self.assertEqual(result, testtuple[1])

    def test_build_time_bounds_checking(self):
        #Leap seconds not supported
        #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
        #https://bitbucket.org/nielsenb/aniso8601/issues/13/parsing-of-leap-second-gives-wildly
        with self.assertRaises(LeapSecondError):
            PythonTimeBuilder.build_time(hh='23', mm='59', ss='60')

        with self.assertRaises(LeapSecondError):
            PythonTimeBuilder.build_time(hh='23', mm='59', ss='60',
                                         tz=UTCOffset(name='UTC', minutes=0))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='00', ss='60')

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='00', ss='60',
                                         tz=UTCOffset(name='UTC', minutes=0))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='00', ss='61')

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='00', ss='61',
                                         tz=UTCOffset(name='UTC', minutes=0))

        with self.assertRaises(MinutesOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='61')

        with self.assertRaises(MinutesOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='61',
                                         tz=UTCOffset(name='UTC', minutes=0))

        with self.assertRaises(MinutesOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='60')

        with self.assertRaises(MinutesOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='00', mm='60.1')

        with self.assertRaises(HoursOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='25')

        with self.assertRaises(HoursOutOfBoundsError):
            PythonTimeBuilder.build_time(hh='24.1')

        #Hour 24 can only represent midnight
        with self.assertRaises(MidnightBoundsError):
            PythonTimeBuilder.build_time(hh='24', mm='00', ss='01')

        with self.assertRaises(MidnightBoundsError):
            PythonTimeBuilder.build_time(hh='24', mm='00.1')

        with self.assertRaises(MidnightBoundsError):
            PythonTimeBuilder.build_time(hh='24', mm='01')

    def test_build_datetime(self):
        testtuples = (((('1234', '2', '3', None, None, None, 'date'),
                        ('23', '21', '28.512400', None, 'time')),
                       datetime.datetime(1234, 2, 3, hour=23, minute=21,
                                         second=28, microsecond=512400)),
                      ((('1981', '04', '05', None, None, None, 'date'),
                        ('23', '21', '28.512400',
                         (False, None, '11', '15', '+11:15', 'timezone'),
                         'time')),
                       datetime.datetime(1981, 4, 5, hour=23, minute=21,
                                         second=28, microsecond=512400,
                                         tzinfo=UTCOffset(name='+11:15',
                                                          minutes=675))))

        for testtuple in testtuples:
            result = PythonTimeBuilder.build_datetime(*testtuple[0])
            self.assertEqual(result, testtuple[1])

    def test_build_datetime_bounds_checking(self):
        #Leap seconds not supported
        #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
        #https://bitbucket.org/nielsenb/aniso8601/issues/13/parsing-of-leap-second-gives-wildly
        with self.assertRaises(LeapSecondError):
            PythonTimeBuilder.build_datetime(('2016', '12', '31',
                                              None, None, None, 'date'),
                                             ('23', '59', '60', None, 'time'))

        with self.assertRaises(LeapSecondError):
            PythonTimeBuilder.build_datetime(('2016', '12', '31',
                                              None, None, None, 'date'),
                                             ('23', '59', '60',
                                              (False, None, '00', '00',
                                               '+00:00', 'timezone'), 'time'))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '00', '60', None, 'time'))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '00', '60',
                                              (False, None, '00', '00',
                                               '+00:00', 'timezone'), 'time'))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '00', '61', None, 'time'))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '00', '61',
                                              (False, None, '00', '00',
                                               '+00:00', 'timezone'), 'time'))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '59', '61', None, 'time'))

        with self.assertRaises(SecondsOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '59', '61',
                                              (False, None, '00', '00',
                                               '+00:00', 'timezone'), 'time'))

        with self.assertRaises(MinutesOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '61', None, None, 'time'))

        with self.assertRaises(MinutesOutOfBoundsError):
            PythonTimeBuilder.build_datetime(('1981', '04', '05',
                                              None, None, None, 'date'),
                                             ('00', '61', None,
                                              (False, None, '00', '00',
                                               '+00:00', 'timezone'), 'time'))

    def test_build_duration(self):
        testtuples = (({'PnY': '1', 'PnM': '2', 'PnD': '3',
                        'TnH': '4', 'TnM': '54', 'TnS': '6'},
                       datetime.timedelta(days=428, hours=4,
                                          minutes=54, seconds=6)),
                      ({'PnY': '1', 'PnM': '2', 'PnD': '3',
                        'TnH': '4', 'TnM': '54', 'TnS': '6.5'},
                       datetime.timedelta(days=428, hours=4,
                                          minutes=54, seconds=6.5)),
                      ({'PnY': '1', 'PnM': '2', 'PnD': '3'},
                       datetime.timedelta(days=428)),
                      ({'PnY': '1', 'PnM': '2', 'PnD': '3.5'},
                       datetime.timedelta(days=428.5)),
                      ({'TnH': '4', 'TnM': '54', 'TnS': '6.5'},
                       datetime.timedelta(hours=4, minutes=54, seconds=6.5)),
                      #Make sure we truncate, not round
                      #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
                      ({'TnS': '0.0000001'}, datetime.timedelta(0)),
                      ({'TnS': '2.0000048'},
                       datetime.timedelta(seconds=2, microseconds=4)),
                      ({'PnY': '1'}, datetime.timedelta(days=365)),
                      ({'PnY': '1.5'}, datetime.timedelta(days=547.5)),
                      ({'PnM': '1'}, datetime.timedelta(days=30)),
                      ({'PnM': '1.5'}, datetime.timedelta(days=45)),
                      ({'PnW': '1'}, datetime.timedelta(days=7)),
                      ({'PnW': '1.5'}, datetime.timedelta(days=10.5)),
                      ({'PnD': '1'}, datetime.timedelta(days=1)),
                      ({'PnD': '1.5'}, datetime.timedelta(days=1.5)),
                      ({'PnY': '0003', 'PnM': '06', 'PnD': '04',
                        'TnH': '12', 'TnM': '30', 'TnS': '05'},
                       datetime.timedelta(days=1279, hours=12,
                                          minutes=30, seconds=5)),
                      ({'PnY': '0003', 'PnM': '06', 'PnD': '04',
                        'TnH': '12', 'TnM': '30', 'TnS': '05.5'},
                       datetime.timedelta(days=1279, hours=12,
                                          minutes=30, seconds=5.5)),
                      #Make sure we truncate, not round
                      #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
                      ({'PnY': '0001', 'PnM': '02', 'PnD': '03',
                        'TnH': '14', 'TnM': '43', 'TnS': '59.9999997'},
                       datetime.timedelta(days=428, hours=14,
                                          minutes=43, seconds=59,
                                          microseconds=999999)),
                      #Verify overflows
                      ({'TnH': '36'}, datetime.timedelta(days=1, hours=12)))

        for testtuple in testtuples:
            result = PythonTimeBuilder.build_duration(**testtuple[0])
            self.assertEqual(result, testtuple[1])

    def test_build_interval(self):
        testtuples = (({'end': (('1981', '04', '05', None, None, None, 'date'),
                                ('01', '01', '00', None, 'time'), 'datetime'),
                        'duration': (None, '1', None, None, None, None, None,
                                     'duration')},
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=3, day=6,
                                         hour=1, minute=1)),
                      ({'end': ('1981', '04', '05', None, None, None, 'date'),
                        'duration': (None, '1', None, None, None, None, None,
                                     'duration')},
                       datetime.date(year=1981, month=4, day=5),
                       datetime.date(year=1981, month=3, day=6)),
                      ({'end': ('2018', '03', '06', None, None, None, 'date'),
                        'duration': ('1.5', None, None, None, None, None, None,
                                     'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.date(year=2016, month=9, day=5)),
                      ({'end': ('2014', '11', '12', None, None, None, 'date'),
                        'duration': (None, None, None, None, '1', None, None,
                                     'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=11,
                                         hour=23)),
                      ({'end': ('2014', '11', '12', None, None, None, 'date'),
                        'duration': (None, None, None, None, '4', '54', '6.5',
                                     'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=11,
                                         hour=19, minute=5, second=53,
                                         microsecond=500000)),
                      ({'end': (('2050', '03', '01',
                                 None, None, None, 'date'),
                                ('13', '00', '00',
                                 (False, True, None, None,
                                  'Z', 'timezone'), 'time'), 'datetime'),
                        'duration': (None, None, None,
                                     None, '10', None, None, 'duration')},
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=13,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0)),
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=3,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0))),
                      #Make sure we truncate, not round
                      #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
                      ({'end': ('2018', '03', '06', None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '0.0000001', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=6)),
                      ({'end': ('2018', '03', '06', None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '2.0000048', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=5,
                                         hour=23, minute=59, second=57,
                                         microsecond=999996)),
                      ({'start': (('1981', '04', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00', None, 'time'),
                                  'datetime'),
                        'duration': (None, '1', None,
                                     '1', None, '1', None, 'duration')},
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=5, day=6,
                                         hour=1, minute=2)),
                      ({'start': ('1981', '04', '05',
                                  None, None, None, 'date'),
                        'duration': (None, '1', None,
                                     '1', None, None, None, 'duration')},
                       datetime.date(year=1981, month=4, day=5),
                       datetime.date(year=1981, month=5, day=6)),
                      ({'start': ('2018', '03', '06',
                                  None, None, None, 'date'),
                        'duration': (None, '2.5', None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.date(year=2018, month=5, day=20)),
                      ({'start': ('2014', '11', '12',
                                  None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, '1', None, None, 'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=12,
                                         hour=1, minute=0)),
                      ({'start': ('2014', '11', '12',
                                  None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, '4', '54', '6.5', 'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=12,
                                         hour=4, minute=54, second=6,
                                         microsecond=500000)),
                      ({'start': (('2050', '03', '01',
                                   None, None, None, 'date'),
                                  ('13', '00', '00',
                                   (False, True, None, None,
                                    'Z', 'timezone'), 'time'), 'datetime'),
                        'duration': (None, None, None,
                                     None, '10', None, None, 'duration')},
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=13,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0)),
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=23,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0))),
                      #Make sure we truncate, not round
                      #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
                      ({'start': ('2018', '03', '06',
                                  None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '0.0000001', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=6)),
                      ({'start': ('2018', '03', '06',
                                  None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '2.0000048', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=6,
                                         hour=0, minute=0, second=2,
                                         microsecond=4)),
                      ({'start': (('1980', '03', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00',
                                   None, 'time'), 'datetime'),
                        'end': (('1981', '04', '05',
                                 None, None, None, 'date'),
                                ('01', '01', '00',
                                 None, 'time'), 'datetime')},
                       datetime.datetime(year=1980, month=3, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1)),
                      ({'start': (('1980', '03', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00',
                                   None, 'time'), 'datetime'),
                        'end': ('1981', '04', '05',
                                None, None, None, 'date')},
                       datetime.datetime(year=1980, month=3, day=5,
                                         hour=1, minute=1),
                       datetime.date(year=1981, month=4, day=5)),
                      ({'start': ('1980', '03', '05',
                                  None, None, None, 'date'),
                        'end': (('1981', '04', '05',
                                 None, None, None, 'date'),
                                ('01', '01', '00',
                                 None, 'time'), 'datetime')},
                       datetime.date(year=1980, month=3, day=5),
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1)),
                      ({'start': ('1980', '03', '05',
                                  None, None, None, 'date'),
                        'end': ('1981', '04', '05',
                                None, None, None, 'date')},
                       datetime.date(year=1980, month=3, day=5),
                       datetime.date(year=1981, month=4, day=5)),
                      ({'start': ('1981', '04', '05',
                                  None, None, None, 'date'),
                        'end': ('1980', '03', '05',
                                None, None, None, 'date')},
                       datetime.date(year=1981, month=4, day=5),
                       datetime.date(year=1980, month=3, day=5)),
                      ({'start': (('2050', '03', '01',
                                   None, None, None, 'date'),
                                  ('13', '00', '00',
                                   (False, True, None, None,
                                    'Z', 'timezone'), 'time'), 'datetime'),
                        'end': (('2050', '05', '11',
                                 None, None, None, 'date'),
                                ('15', '30', '00',
                                 (False, True, None, None,
                                  'Z', 'timezone'), 'time'), 'datetime')},
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=13,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0)),
                       datetime.datetime(year=2050, month=5, day=11,
                                         hour=15, minute=30,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0))),
                      #Make sure we truncate, not round
                      #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
                      ({'start': (('1980', '03', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00.0000001',
                                   None, 'time'), 'datetime'),
                        'end': (('1981', '04', '05',
                                 None, None, None, 'date'),
                                ('14', '43', '59.9999997', None, 'time'),
                                'datetime')},
                       datetime.datetime(year=1980, month=3, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=14, minute=43, second=59,
                                         microsecond=999999)))

        for testtuple in testtuples:
            result = PythonTimeBuilder.build_interval(**testtuple[0])
            self.assertEqual(result[0], testtuple[1])
            self.assertEqual(result[1], testtuple[2])

    def test_build_repeating_interval(self):
        args = {'Rnn': '3', 'interval': (('1981', '04', '05',
                                          None, None, None, 'date'),
                                         None,
                                         (None, None, None,
                                          '1', None, None,
                                          None, 'duration'),
                                         'interval')}
        results = list(PythonTimeBuilder.build_repeating_interval(**args))

        self.assertEqual(results[0], datetime.date(year=1981, month=4, day=5))
        self.assertEqual(results[1], datetime.date(year=1981, month=4, day=6))
        self.assertEqual(results[2], datetime.date(year=1981, month=4, day=7))

        args = {'Rnn': '11', 'interval': (None,
                                          (('1980', '03', '05',
                                            None, None, None, 'date'),
                                           ('01', '01', '00',
                                            None, 'time'), 'datetime'),
                                          (None, None, None,
                                           None, '1', '2',
                                           None, 'duration'),
                                          'interval')}
        results = list(PythonTimeBuilder.build_repeating_interval(**args))

        for dateindex in compat.range(0, 11):
            self.assertEqual(results[dateindex],
                             datetime.datetime(year=1980, month=3, day=5,
                                               hour=1, minute=1)
                             - dateindex * datetime.timedelta(hours=1,
                                                              minutes=2))

        args = {'Rnn': '2', 'interval': ((('1980', '03', '05',
                                           None, None, None, 'date'),
                                          ('01', '01', '00',
                                           None, 'time'), 'datetime'),
                                         (('1981', '04', '05',
                                           None, None, None, 'date'),
                                          ('01', '01', '00',
                                           None, 'time'), 'datetime'),
                                         None,
                                         'interval')}
        results = list(PythonTimeBuilder.build_repeating_interval(**args))

        self.assertEqual(results[0],
                         datetime.datetime(year=1980, month=3, day=5,
                                           hour=1, minute=1))
        self.assertEqual(results[1],
                         datetime.datetime(year=1981, month=4, day=5,
                                           hour=1, minute=1))

        args = {'Rnn': '2', 'interval': ((('1980', '03', '05',
                                           None, None, None, 'date'),
                                          ('01', '01', '00',
                                           None, 'time'), 'datetime'),
                                         (('1981', '04', '05',
                                           None, None, None, 'date'),
                                          ('01', '01', '00',
                                           None, 'time'), 'datetime'),
                                         None,
                                         'interval')}
        results = list(PythonTimeBuilder.build_repeating_interval(**args))

        self.assertEqual(results[0],
                         datetime.datetime(year=1980, month=3, day=5,
                                           hour=1, minute=1))
        self.assertEqual(results[1],
                         datetime.datetime(year=1981, month=4, day=5,
                                           hour=1, minute=1))

        args = {'R': True, 'interval': (None,
                                        (('1980', '03', '05',
                                          None, None, None, 'date'),
                                         ('01', '01', '00',
                                          None, 'time'), 'datetime'),
                                        (None, None, None,
                                         None, '1', '2', None, 'duration'),
                                        'interval')}
        resultgenerator = PythonTimeBuilder.build_repeating_interval(**args)

        #Test the first 11 generated
        for dateindex in compat.range(0, 11):
            self.assertEqual(next(resultgenerator),
                             datetime.datetime(year=1980, month=3, day=5,
                                               hour=1, minute=1)
                             - dateindex * datetime.timedelta(hours=1,
                                                              minutes=2))

    def test_build_timezone(self):
        testtuples = (({'Z': True, 'name': 'Z'},
                       datetime.timedelta(hours=0), 'UTC'),
                      ({'negative': False, 'hh': '00', 'mm': '00',
                        'name': '+00:00'},
                       datetime.timedelta(hours=0), '+00:00'),
                      ({'negative': False, 'hh': '01', 'mm': '00',
                        'name': '+01:00'},
                       datetime.timedelta(hours=1), '+01:00'),
                      ({'negative': True, 'hh': '01', 'mm': '00',
                        'name': '-01:00'},
                       -datetime.timedelta(hours=1), '-01:00'),
                      ({'negative': False, 'hh': '00', 'mm': '12',
                        'name': '+00:12'},
                       datetime.timedelta(minutes=12), '+00:12'),
                      ({'negative': False, 'hh': '01', 'mm': '23',
                        'name': '+01:23'},
                       datetime.timedelta(hours=1, minutes=23), '+01:23'),
                      ({'negative': True, 'hh': '01', 'mm': '23',
                        'name': '-01:23'},
                       -datetime.timedelta(hours=1, minutes=23), '-01:23'),
                      ({'negative': False, 'hh': '00',
                        'name': '+00'},
                       datetime.timedelta(hours=0), '+00'),
                      ({'negative': False, 'hh': '01',
                        'name': '+01'},
                       datetime.timedelta(hours=1), '+01'),
                      ({'negative': True, 'hh': '01',
                        'name': '-01'},
                       -datetime.timedelta(hours=1), '-01'),
                      ({'negative': False, 'hh': '12',
                        'name': '+12'},
                       datetime.timedelta(hours=12), '+12'),
                      ({'negative': True, 'hh': '12',
                        'name': '-12'},
                       -datetime.timedelta(hours=12), '-12'))

        for testtuple in testtuples:
            result = PythonTimeBuilder.build_timezone(**testtuple[0])
            self.assertEqual(result.utcoffset(None), testtuple[1])
            self.assertEqual(result.tzname(None), testtuple[2])

    def test_build_week_date(self):
        weekdate = PythonTimeBuilder._build_week_date(2009, 1)
        self.assertEqual(weekdate, datetime.date(year=2008, month=12, day=29))

        weekdate = PythonTimeBuilder._build_week_date(2009, 53, isoday=7)
        self.assertEqual(weekdate, datetime.date(year=2010, month=1, day=3))

    def test_build_ordinal_date(self):
        ordinaldate = PythonTimeBuilder._build_ordinal_date(1981, 95)
        self.assertEqual(ordinaldate, datetime.date(year=1981, month=4, day=5))

    def test_build_ordinal_date_bounds_checking(self):
        with self.assertRaises(DayOutOfBoundsError):
            PythonTimeBuilder._build_ordinal_date(1234, 0)

        with self.assertRaises(DayOutOfBoundsError):
            PythonTimeBuilder._build_ordinal_date(1234, 367)

    def test_iso_year_start(self):
        yearstart = PythonTimeBuilder._iso_year_start(2004)
        self.assertEqual(yearstart, datetime.date(year=2003, month=12, day=29))

        yearstart = PythonTimeBuilder._iso_year_start(2010)
        self.assertEqual(yearstart, datetime.date(year=2010, month=1, day=4))

        yearstart = PythonTimeBuilder._iso_year_start(2009)
        self.assertEqual(yearstart, datetime.date(year=2008, month=12, day=29))

    def test_date_generator(self):
        startdate = datetime.date(year=2018, month=8, day=29)
        timedelta = datetime.timedelta(days=1)
        iterations = 10

        generator = PythonTimeBuilder._date_generator(startdate,
                                                      timedelta,
                                                      iterations)

        results = list(generator)

        for dateindex in compat.range(0, 10):
            self.assertEqual(results[dateindex],
                             datetime.date(year=2018, month=8, day=29)
                             + dateindex * datetime.timedelta(days=1))

    def test_date_generator_unbounded(self):
        startdate = datetime.date(year=2018, month=8, day=29)
        timedelta = datetime.timedelta(days=5)

        generator = PythonTimeBuilder._date_generator_unbounded(startdate,
                                                                timedelta)

        #Check the first 10 results
        for dateindex in compat.range(0, 10):
            self.assertEqual(next(generator),
                             datetime.date(year=2018, month=8, day=29)
                             + dateindex * datetime.timedelta(days=5))

class TestRelativeTimeBuilder(unittest.TestCase):
    def test_build_duration(self):
        testtuples = (({'PnY': '1'},
                       dateutil.relativedelta.relativedelta(years=1)),
                      ({'PnM': '1'},
                      #Add the relative ‘days’ argument to the absolute day. Notice that the ‘weeks’ argument is multiplied by 7 and added to ‘days’.
                      #http://dateutil.readthedocs.org/en/latest/relativedelta.html
                       dateutil.relativedelta.relativedelta(months=1)),
                      ({'PnW': '1'},
                       dateutil.relativedelta.relativedelta(days=7)),
                      ({'PnW': '1.5'},
                       dateutil.relativedelta.relativedelta(days=10.5)),
                      ({'PnD': '1'},
                       dateutil.relativedelta.relativedelta(days=1)),
                      ({'PnD': '1.5'},
                       dateutil.relativedelta.relativedelta(days=1.5)),
                      ({'PnY': '1', 'PnM': '2', 'PnD': '3'},
                       dateutil.relativedelta.relativedelta(years=1, months=2,
                                                            days=3)),
                      ({'PnY': '1', 'PnM': '2', 'PnD': '3.5'},
                       dateutil.relativedelta.relativedelta(years=1, months=2,
                                                            days=3.5)),
                      ({'PnY': '1', 'PnM': '2', 'PnD': '3',
                        'TnH': '4', 'TnM': '54', 'TnS': '6.5'},
                       dateutil.relativedelta.relativedelta(years=1, months=2,
                                                            days=3, hours=4,
                                                            minutes=54,
                                                            seconds=6,
                                                            microseconds=
                                                            500000)),
                      ({'PnY': '0003', 'PnM': '06', 'PnD': '04',
                        'TnH': '12', 'TnM': '30', 'TnS': '05'},
                       dateutil.relativedelta.relativedelta(years=3, months=6,
                                                            days=4, hours=12,
                                                            minutes=30,
                                                            seconds=5)),
                      ({'PnY': '0003', 'PnM': '06', 'PnD': '04',
                        'TnH': '12', 'TnM': '30', 'TnS': '05.5'},
                       dateutil.relativedelta.relativedelta(years=3, months=6,
                                                            days=4, hours=12,
                                                            minutes=30,
                                                            seconds=5,
                                                            microseconds=
                                                            500000)),
                      ({'TnH': '4', 'TnM': '54', 'TnS': '6.5'},
                       dateutil.relativedelta.relativedelta(hours=4,
                                                            minutes=54,
                                                            seconds=6,
                                                            microseconds=
                                                            500000)),
                      #Make sure we truncate, not round
                      #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
                      ({'TnS': '0.0000001'},
                       dateutil.relativedelta.relativedelta(0)),
                      ({'TnS': '2.0000048'},
                       dateutil.relativedelta.relativedelta(seconds=2,
                                                            microseconds=4)),
                      ({'PnY': '0001', 'PnM': '02', 'PnD': '03',
                        'TnH': '14', 'TnM': '43', 'TnS': '59.9999997'},
                       dateutil.relativedelta.relativedelta(years=1, months=2,
                                                            days=3, hours=14,
                                                            minutes=43,
                                                            seconds=59,
                                                            microseconds=
                                                            999999)),
                      ({'PnY': '1', 'PnM': '2', 'PnW': '4', 'PnD': '3',
                        'TnH': '5', 'TnM': '6', 'TnS': '7.0000091011'},
                       dateutil.relativedelta.relativedelta(years=1, months=2,
                                                            days=31, hours=5,
                                                            minutes=6,
                                                            seconds=7,
                                                            microseconds=9)))

        for testtuple in testtuples:
            result = RelativeTimeBuilder.build_duration(**testtuple[0])
            self.assertEqual(result, testtuple[1])

    def test_build_duration_fractional_year(self):
        with self.assertRaises(RelativeValueError):
            RelativeTimeBuilder.build_duration(PnY='1.5')

    def test_build_duration_fractional_month(self):
        with self.assertRaises(RelativeValueError):
            RelativeTimeBuilder.build_duration(PnM='1.5')

    def test_build_duration_nodateutil(self):
        import sys
        import dateutil

        dateutil_import = dateutil

        sys.modules['dateutil'] = None

        with self.assertRaises(RuntimeError):
            RelativeTimeBuilder.build_duration()

        #Reinstall dateutil
        sys.modules['dateutil'] = dateutil_import

    def test_build_interval(self):
        #Intervals are contingent on durations, make sure they work
        testtuples = (({'end': (('1981', '04', '05', None, None, None, 'date'),
                                ('01', '01', '00', None, 'time'), 'datetime'),
                        'duration': (None, '1', None, None, None, None, None,
                                     'duration')},
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=3, day=5,
                                         hour=1, minute=1)),
                      ({'end': ('1981', '04', '05', None, None, None, 'date'),
                        'duration': (None, '1', None, None, None, None, None,
                                     'duration')},
                       datetime.date(year=1981, month=4, day=5),
                       datetime.date(year=1981, month=3, day=5)),
                      ({'end': ('2014', '11', '12', None, None, None, 'date'),
                        'duration': (None, None, None, None, '1', None, None,
                                     'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=11,
                                         hour=23)),
                      ({'end': ('2014', '11', '12', None, None, None, 'date'),
                        'duration': (None, None, None, None, '4', '54', '6.5',
                                     'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=11,
                                         hour=19, minute=5, second=53,
                                         microsecond=500000)),
                      ({'end': (('2050', '03', '01',
                                 None, None, None, 'date'),
                                ('13', '00', '00',
                                 (False, True, None, None,
                                  'Z', 'timezone'), 'time'), 'datetime'),
                        'duration': (None, None, None,
                                     None, '10', None, None, 'duration')},
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=13,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0)),
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=3,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0))),
                      #Make sure we truncate, not round
                      #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
                      ({'end': ('2018', '03', '06', None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '0.0000001', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=6)),
                      ({'end': ('2018', '03', '06', None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '2.0000048', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=5,
                                         hour=23, minute=59, second=57,
                                         microsecond=999996)),
                      ({'start': ('2018', '03', '06', None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '0.0000001', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=6)),
                      ({'start': ('2018', '03', '06', None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, None, None,
                                     '2.0000048', 'duration')},
                       datetime.date(year=2018, month=3, day=6),
                       datetime.datetime(year=2018, month=3, day=6,
                                         hour=0, minute=0, second=2,
                                         microsecond=4)),
                      ({'start': (('1981', '04', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00', None, 'time'),
                                  'datetime'),
                        'duration': (None, '1', None,
                                     '1', None, '1', None, 'duration')},
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=5, day=6,
                                         hour=1, minute=2)),
                      ({'start': ('1981', '04', '05',
                                  None, None, None, 'date'),
                        'duration': (None, '1', None,
                                     '1', None, None, None, 'duration')},
                       datetime.date(year=1981, month=4, day=5),
                       datetime.date(year=1981, month=5, day=6)),
                      ({'start': ('2014', '11', '12',
                                  None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, '1', None, None, 'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=12,
                                         hour=1, minute=0)),
                      ({'start': ('2014', '11', '12',
                                  None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, '4', '54', '6.5', 'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=12,
                                         hour=4, minute=54, second=6,
                                         microsecond=500000)),
                      ({'start': ('2014', '11', '12',
                                  None, None, None, 'date'),
                        'duration': (None, None, None,
                                     None, '4', '54', '6.5', 'duration')},
                       datetime.date(year=2014, month=11, day=12),
                       datetime.datetime(year=2014, month=11, day=12,
                                         hour=4, minute=54, second=6,
                                         microsecond=500000)),
                      ({'start': (('2050', '03', '01',
                                   None, None, None, 'date'),
                                  ('13', '00', '00',
                                   (False, True, None, None,
                                    'Z', 'timezone'), 'time'), 'datetime'),
                        'duration': (None, None, None,
                                     None, '10', None, None, 'duration')},
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=13,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0)),
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=23,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0))),
                      ({'start': (('1980', '03', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00.0000001', None, 'time'),
                                  'datetime'),
                        'end': (('1981', '04', '05',
                                 None, None, None, 'date'),
                                ('14', '43', '59.9999997', None, 'time'),
                                'datetime')},
                       datetime.datetime(year=1980, month=3, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=14, minute=43, second=59,
                                         microsecond=999999)),
                      ({'start': (('2050', '03', '01',
                                   None, None, None, 'date'),
                                  ('13', '00', '00',
                                   (False, True, None, None,
                                    'Z', 'timezone'), 'time'), 'datetime'),
                        'end': (('2050', '05', '11',
                                 None, None, None, 'date'),
                                ('15', '30', '00',
                                 (False, True, None, None,
                                  'Z', 'timezone'), 'time'), 'datetime')},
                       datetime.datetime(year=2050, month=3, day=1,
                                         hour=13,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0)),
                       datetime.datetime(year=2050, month=5, day=11,
                                         hour=15, minute=30,
                                         tzinfo=UTCOffset(name='UTC',
                                                          minutes=0))),
                      #Some relativedelta examples
                      #http://dateutil.readthedocs.org/en/latest/examples.html#relativedelta-examples
                      ({'start': ('2003', '1', '27',
                                  None, None, None, 'date'),
                        'duration': (None, '1', None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=2003, month=1, day=27),
                       datetime.date(year=2003, month=2, day=27)),
                      ({'start': ('2003', '1', '31',
                                  None, None, None, 'date'),
                        'duration': (None, '1', None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=2003, month=1, day=31),
                       datetime.date(year=2003, month=2, day=28)),
                      ({'start': ('2003', '1', '31',
                                  None, None, None, 'date'),
                        'duration': (None, '2', None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=2003, month=1, day=31),
                       datetime.date(year=2003, month=3, day=31)),
                      ({'start': ('2000', '2', '28',
                                  None, None, None, 'date'),
                        'duration': ('1', None, None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=2000, month=2, day=28),
                       datetime.date(year=2001, month=2, day=28)),
                      ({'start': ('1999', '2', '28',
                                  None, None, None, 'date'),
                        'duration': ('1', None, None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=1999, month=2, day=28),
                       datetime.date(year=2000, month=2, day=28)),
                      ({'start': ('1999', '3', '1',
                                  None, None, None, 'date'),
                        'duration': ('1', None, None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=1999, month=3, day=1),
                       datetime.date(year=2000, month=3, day=1)),
                      ({'end': ('2001', '2', '28',
                                None, None, None, 'date'),
                        'duration': ('1', None, None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=2001, month=2, day=28),
                       datetime.date(year=2000, month=2, day=28)),
                      ({'end': ('2001', '3', '1',
                                None, None, None, 'date'),
                        'duration': ('1', None, None,
                                     None, None, None, None, 'duration')},
                       datetime.date(year=2001, month=3, day=1),
                       datetime.date(year=2000, month=3, day=1)),
                      ({'start': (('1980', '03', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00', None, 'time'),
                                  'datetime'),
                        'end': (('1981', '04', '05',
                                 None, None, None, 'date'),
                                ('01', '01', '00', None, 'time'),
                                'datetime')},
                       datetime.datetime(year=1980, month=3, day=5,
                                         hour=1, minute=1),
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1)),
                      ({'start': (('1980', '03', '05',
                                   None, None, None, 'date'),
                                  ('01', '01', '00', None, 'time'),
                                  'datetime'),
                        'end': ('1981', '04', '05', None, None, None, 'date')},
                       datetime.datetime(year=1980, month=3, day=5,
                                         hour=1, minute=1),
                       datetime.date(year=1981, month=4, day=5)),
                      ({'start': ('1980', '03', '05',
                                  None, None, None, 'date'),
                        'end': (('1981', '04', '05',
                                 None, None, None, 'date'),
                                ('01', '01', '00', None, 'time'),
                                'datetime')},
                       datetime.date(year=1980, month=3, day=5),
                       datetime.datetime(year=1981, month=4, day=5,
                                         hour=1, minute=1)),
                      ({'start': ('1980', '03', '05',
                                  None, None, None, 'date'),
                        'end': ('1981', '04', '05',
                                None, None, None, 'date')},
                       datetime.date(year=1980, month=3, day=5),
                       datetime.date(year=1981, month=4, day=5)),
                      ({'start': ('1981', '04', '05',
                                  None, None, None, 'date'),
                        'end': ('1980', '03', '05',
                                None, None, None, 'date')},
                       datetime.date(year=1981, month=4, day=5),
                       datetime.date(year=1980, month=3, day=5)))

        for testtuple in testtuples:
            result = RelativeTimeBuilder.build_interval(**testtuple[0])
            self.assertEqual(result[0], testtuple[1])
            self.assertEqual(result[1], testtuple[2])

    def test_build_repeating_interval(self):
        #Repeating intervals are contingent on durations, make sure they work
        args = {'Rnn': '3', 'interval': (('1981', '04', '05',
                                          None, None, None, 'date'),
                                         None,
                                         (None, None, None,
                                          '1', None, None,
                                          None, 'duration'),
                                         'interval')}
        results = list(RelativeTimeBuilder.build_repeating_interval(**args))

        self.assertEqual(results[0], datetime.date(year=1981, month=4, day=5))
        self.assertEqual(results[1], datetime.date(year=1981, month=4, day=6))
        self.assertEqual(results[2], datetime.date(year=1981, month=4, day=7))

        args = {'Rnn': '11', 'interval': (None,
                                          (('1980', '03', '05',
                                            None, None, None, 'date'),
                                           ('01', '01', '00',
                                            None, 'time'), 'datetime'),
                                          (None, None, None,
                                           None, '1', '2',
                                           None, 'duration'),
                                          'interval')}
        results = list(RelativeTimeBuilder.build_repeating_interval(**args))

        for dateindex in compat.range(0, 11):
            self.assertEqual(results[dateindex],
                             datetime.datetime(year=1980, month=3, day=5,
                                               hour=1, minute=1)
                             - dateindex * datetime.timedelta(hours=1,
                                                              minutes=2))

        #Make sure relative is correctly applied for months
        #https://bitbucket.org/nielsenb/aniso8601/issues/12/month-intervals-calculated-incorrectly-or
        args = {'Rnn': '4', 'interval': ((('2017', '04', '30',
                                           None, None, None, 'date'),
                                          ('00', '00', '00',
                                           None, 'time'), 'datetime'),
                                         None,
                                         (None, '1', None,
                                          None, None, None, None, 'duration'),
                                         'interval')}
        results = list(RelativeTimeBuilder.build_repeating_interval(**args))

        self.assertEqual(results[0],
                         datetime.datetime(year=2017, month=4, day=30))
        self.assertEqual(results[1],
                         datetime.datetime(year=2017, month=5, day=30))
        self.assertEqual(results[2],
                         datetime.datetime(year=2017, month=6, day=30))
        self.assertEqual(results[3],
                         datetime.datetime(year=2017, month=7, day=30))

        args = {'R': True, 'interval': (None,
                                        (('1980', '03', '05',
                                          None, None, None, 'date'),
                                         ('01', '01', '00',
                                          None, 'time'), 'datetime'),
                                        (None, None, None,
                                         None, '1', '2', None, 'duration'),
                                        'interval')}
        resultgenerator = RelativeTimeBuilder.build_repeating_interval(**args)

        for dateindex in compat.range(0, 11):
            self.assertEqual(next(resultgenerator),
                             datetime.datetime(year=1980, month=3, day=5,
                                               hour=1, minute=1)
                             - dateindex * datetime.timedelta(hours=1,
                                                              minutes=2))

class TestUTCOffset(unittest.TestCase):
    def test_pickle(self):
        #Make sure timezone objects are pickleable
        testutcoffset = UTCOffset(name='UTC', minutes=0)

        utcoffsetpickle = pickle.dumps(testutcoffset)

        resultutcoffset = pickle.loads(utcoffsetpickle)

        self.assertEqual(resultutcoffset._name, testutcoffset._name)
        self.assertEqual(resultutcoffset._utcdelta, testutcoffset._utcdelta)

    def test_repr(self):
        self.assertEqual(str(UTCOffset(minutes=0)), '+0:00:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=60)), '+1:00:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=-60)), '-1:00:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=12)), '+0:12:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=-12)), '-0:12:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=83)), '+1:23:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=-83)), '-1:23:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=1440)), '+1 day, 0:00:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=-1440)), '-1 day, 0:00:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=2967)), '+2 days, 1:27:00 UTC')

        self.assertEqual(str(UTCOffset(minutes=-2967)), '-2 days, 1:27:00 UTC')

    def test_dst(self):
        tzinfoobject = UTCOffset(minutes=240)
        #This would raise ISOFormatError or a TypeError if dst info is invalid
        result = datetime.datetime.now(tzinfoobject)
        #Hacky way to make sure the tzinfo is what we'd expect
        self.assertEqual(result.tzinfo.utcoffset(None),
                         datetime.timedelta(hours=4))
