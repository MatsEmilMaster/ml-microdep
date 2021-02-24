import json
import inspect
from typing import Any, Union
import datetime as dt_module


class CrudeRecord():

    def __init__(self, id, seq, src, dst, tx, rx, size, hoplimit, *args, **kwargs):
        """All attrs are str"""
        self.id: int = int(id) # TODO: change to int, currently some analyzers is assuming str
        self.seq: int = int(seq) # TODO: change to int, currently some analyzers is assuming str
        self.src: str = src
        self.dst: str = dst
        self.tx: float = float(tx)
        self.rx: float = float(rx)
        self.size: int = int(size)
        self.hoplimit: int = int(hoplimit)

    def __str__(self):
        return f"[{self.__class__.__name__}] (id={self.id}, seq={self.seq}, src={self.src}, dst={self.dst}, tx={self.tx}, rx={self.rx}, size={self.size}, hoplimit={self.hoplimit})"

    def __lt__(self, other):
        """Used when sorting"""
        return self.seq < other.seq

    def transmit_time(self) -> float:
        return self.rx - self.tx


class Gap:
    """Gap a la Emil"""
    XS: str = 'tiny'
    SM: str = 'small'
    MD: str = 'medium'
    LG: str = 'big'
    XL: str = 'huge'
    GAP_LIMITS: dict = {
        # from <= n < to
        XS: {'from': None, 'to': 2},
        SM: {'from': 2, 'to': 5},
        MD: {'from': 5, 'to': 10},
        LG: {'from': 10, 'to': 50},
        XL: {'from': 50, 'to': None},
    }

    def __init__(self, from_adr, from_ip, to_adr, to_ip, datetime, timestamp, tz=dt_module.timezone.utc, fastest_record=None, *args, **kwargs):
        self.from_adr: str = from_adr
        self.from_ip: str = from_ip
        self.to_adr: str = to_adr
        self.to_ip: str = to_ip
        # self.datetime: str = datetime
        self.timestamp: float = timestamp
        self.tz: dt_module.timezone = tz
        self.fastest_record: CrudeRecord = fastest_record
        self.head: list[CrudeRecord] = []
        self.tail: list[CrudeRecord] = []
        self.event_type: str = 'gap'

    def __str__(self):
        # return f"Gap: \nhead: {[record.seq for record in self.head]} \ntail: {[record.seq for record in self.tail]}"
        try:
            return f"Gap: {self.head[-1].seq} -> {self.tail[0].seq}"
        except:
            return "Gap..."

    def get_datetime(self):
        return dt_module.datetime.fromtimestamp(self.timestamp, self.tz)

    @staticmethod
    def get_type(gap_size: int) -> Union[str, None]:
        if not gap_size: return None
        for type, limits in Gap.GAP_LIMITS.items():
            if (limits['from'] or gap_size-1) <= gap_size < (limits['to'] or gap_size+1):
                return type
        return None

    def gap_size(self):
        if len(self.head)==0 or len(self.tail)==0:
            return None
        return self.tail[0].seq - self.head[-1].seq



    def to_json(self, **kwargs):
        obj = {
            'from_adr': self.from_adr,
            'from_ip': self.from_ip,
            'to_adr': self.to_adr,
            'to_ip': self.to_ip,
            'gap_size': self.gap_size(),
            'gap_type': self.get_type(self.gap_size()),
            # 'datetime': self.get_datetime(),
            'timestamp': self.timestamp,
            # 'timestamp_zone': dt_module.timezone.tzname(dt=self.tz),

            'h_n': len(self.head),
            'h_ddelay': self.avg_delay(records=self.head) - self.fastest_record.transmit_time() if self.fastest_record else 0,
            'h_delay': self.avg_delay(records=self.head),
            'h_jit': self.jitter(records=self.head),
            'h_min_d': self.min_delay(records=self.head),
            'h_slope_10': self.slope(n=-10, records=self.head),
            'h_slope_20': self.slope(n=-20, records=self.head),
            'h_slope_30': self.slope(n=-30, records=self.head),
            'h_slope_40': self.slope(n=-40, records=self.head),
            'h_slope_50': self.slope(n=-50, records=self.head),

            'tloss': self.tloss(),
            't_n': len(self.tail),

            't_n': len(self.tail),
            't_ddelay': Gap.avg_delay(records=self.tail) - self.fastest_record.transmit_time() if self.fastest_record else 0,
            't_delay': Gap.avg_delay(records=self.tail),
            't_jit': Gap.jitter(records=self.tail),
            't_min_d': Gap.min_delay(records=self.tail),
            't_slope_10': Gap.slope(n=10, records=self.tail),
            't_slope_20': Gap.slope(n=20, records=self.tail),
            't_slope_30': Gap.slope(n=30, records=self.tail),
            't_slope_40': Gap.slope(n=40, records=self.tail),
            't_slope_50': Gap.slope(n=50, records=self.tail),
            'event_type': self.event_type,
        }
        return json.dumps(obj, **kwargs)

    def add_record_to_head(self, record: CrudeRecord) -> None:
        self.head.append(record)

    def add_records_to_head(self, records: list[CrudeRecord]) -> None:
        self.head.extend(records)

    def add_record_to_tail(self, record: CrudeRecord) -> None:
        self.tail.append(record)

    def add_records_to_tail(self, records: list[CrudeRecord]) -> None:
        self.tail.extend(records)

    @staticmethod
    def avg_delay(records: list[CrudeRecord]) -> Union[float, None]:
        if len(records) == 0:
            return None
        return sum([record.transmit_time() for record in records]) / len(records) # can't divide by 0

    @staticmethod
    def jitter(records: list[CrudeRecord]) -> Union[float, None]:
        """https://www.pingman.com/kb/article/what-is-jitter-57.html"""
        if len(records) < 2:
            return None
        return sum([ abs(records[i].rx - records[i+1].rx) for i in range(len(records)-1) ]) / (len(records)-1)

    @staticmethod
    def min_delay(records: list[CrudeRecord]) -> Union[float, None]:
        if len(records) == 0:
            return None
        return min([record.transmit_time() for record in records])

    @staticmethod
    def slope(n: int, records: list[CrudeRecord]) -> Union[float, None]:
        """
        Returns slope (a in y=ax+b)
            n (positive): first n records
            n (negative): last n records
        """
        # TODO: implement
        pass

    def tloss(self) -> Union[float, None]:
        """Return time lost in the gap. Difference between last packet before gap and first packet after gap"""
        if len(self.head)==0 or len(self.tail)==0:
            return None
        return self.tail[0].rx - self.head[-1].rx
