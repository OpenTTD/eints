"""
Unique ordered identification of things and events
"""
import re, datetime

re_datetime = re.compile('([1-2][0-9]{3})-([01][0-9])-([0-3][0-9])T' +
                         '([0-2][0-9]):([0-5][0-9]):([0-5][0-9])(\\.[0-9]{1,6})?$')

class Stamp:
    """
    A unique identification in time.

    @ivar stamp: The time stamp.
    @type stamp: L{datetime.datetime}

    @ivar name: Optional name of this moment.
    @type name: C{None} or C{str}
    """
    def __init__(self, stamp, text = None):
        if text == "":
            text = None

        self.stamp = stamp
        self.text  = text

    def __eq__(self, other):
        if not isinstance(other, Stamp):
            return False
        return self.stamp == other.stamp

    def __hash__(self):
        return hash(self.stamp)

    def __lt__(self, other):
        if not isinstance(other, Stamp):
            raise NotImplementedError()
        return self.stamp < other.stamp

    def __le__(self, other):
        if not isinstance(other, Stamp):
            raise NotImplementedError()
        return self.stamp == other.stamp or self.stamp < other.stamp

    def to_text(self):
        if self.text is None:
            return self.stamp.isoformat()
        else:
            return self.stamp.isoformat() + " " + self.text


class TimeStamper:
    """
    Class handling construction of unique ordered time stamps.

    @ivar last_stamp: Last time stamp given away.
    @type last_stamp: L{datetime.datetime} or C{None} if no time stamp has been created yet.
    """
    def __init__(self):
        self.last_stamp = None

    def new_stamp(self, text = None):
        """
        Construct a new unique identification stamp.

        @param text: Optional name of the identification.
        @type  text: C{None} or C{str}

        @return: Unique identification stamp.
        @rtype:  C{Stamp}
        """
        now = datetime.datetime.utcnow()
        if self.last_stamp is not None and self.last_stamp == now:
            now = now + datetime.resolution
        self.last_stamp = now
        return Stamp(now, text)

    def read_stamp(self, text):
        """
        Read an identification stamp.

        @param text: Text of the stamp.
        @type  text: C{str}

        @return: The read stamp if it can be read, else C{None}
        @rtype:  C{Stamp} or C{None}
        """
        text = text.strip().split(' ', 1)
        m = re_datetime.match(text[0])
        if not m:
            return None

        # Convert the parsed text to an object
        try:
            year   = int(m.group(1))
            month  = int(m.group(2))
            day    = int(m.group(3))
            hour   = int(m.group(4))
            minute = int(m.group(5))
            second = int(m.group(6))
            if m.group(7) is None:
                microsecond = 0
            else:
                microsecond = int(m.group(7)[1:])

            stamp = datetime.datetime(year, month, day, hour, minute, second, microsecond)
        except ValueError:
            return None

        # Read datetime stamps should not be in the future.
        now = datetime.datetime.utcnow()
        if now < stamp:
            return None

        # Update ourselves as well.
        if self.last_stamp is None or self.last_stamp < stamp:
            self.last_stamp = stamp

        if len(text) == 1:
            return Stamp(stamp)
        else:
            return Stamp(stamp, text[1].lstrip())

stamper = TimeStamper()

