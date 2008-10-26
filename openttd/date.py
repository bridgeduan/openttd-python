"""openttd.date -- date conversion between python and openttd"""
# reading openttd dates with python
# made by yorickvanpelt {AT} gmail {DOT} com
import datetime

class OpenTTDDate(object):
    """
    Class that allows conversion between openttd dates and python dates
    @ivar _date: date
    @type _date: datetime.date instance
    """
    def __init__(self, ottddate=None, pydate=None, year=None, month=None, day=None):
        """
        constructor for OpenTTDDate
        
        example:
            - OpenTTDDate(ottddate=302974).toYMD()
            - OpenTTDDate(year=2008, month=10, day=12).toOpenTTDDate()
        @param ottddate: openttd date to convert from
        @type  ottddate: int
        @param   pydate: datetime.date to convert from
        @type    pydate: datetime.date instance
        @param     year: year to convert from
        @type      year: int
        @param    month: month to convert from
        @type     month: int
        @param      day: day to convert from
        @type       day: int
        """
        if not ottddate is None:
            self.fromOpenTTDDate(ottddate)
        elif not pydate is None:
            self.fromDate(pydate)
        elif not year is None and not month is None and not day is None:
            self.fromYMD(year, month, day)
        else:
            self._date = datetime.date()
    def fromYMD(self, year, month, day):
        """
        convert from YMD
        @param     year: year to convert from
        @type      year: int
        @param    month: month to convert from
        @type     month: int
        @param      day: day to convert from
        @type       day: int
        """
        self._date = datetime.date(year, month, day)
    def fromDate(self, date):
        """
        convert from datetime.date
        @param date: date to convert from
        @type  date: datetime.date instance
        """
        self._date = date
    def fromOpenTTDDate(self, date):
        """
        convert from openttd date
        @param date: date to convert from
        @type  date: int
        """
        self._date = datetime.date.fromordinal(date - 365)
    def toYMD(self):
        """
        convert to YMD
        @rtype  : tuple
        @returns: (year, month, day)
        """
        return (self._date.year, self._date.month, self._date.day)
    def toDate(self):
        """
        convert to datetime.date
        @rtype  : datetime.date instance
        @returns: converted date
        """
        return self._date
    def toOpenTTDDate(self):
        """
        convert to openttd date
        @rtype  : int
        @returns: openttd date
        """
        return self._date.toordinal() + 365