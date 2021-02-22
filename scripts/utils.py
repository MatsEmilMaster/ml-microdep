import queue
import emil_types
from typing import Any, Optional
import bisect


class CrudeStreamAnalyzer():
    """Analyzes crude records for single stream-id"""

    def __init__(self, stream_id, h_limit, t_limit, start_gap_threshold, end_gap_threshold, window_size=0, *args, **kwargs):
        self.stream_id: int = int(stream_id)
        self.h_limit: int = int(h_limit)
        self.t_limit: int = int(t_limit)
        self.start_gap_threshold: int = int(start_gap_threshold)
        self.end_gap_threshold: int = int(end_gap_threshold)
        self.window: list[emil_types.CrudeRecord] = []
        self.buffer: list[emil_types.CrudeRecord] = []
        self.gap_counter: int = 0
        self.record_counter: int = 0
        self.highest_seq: int = 0
        self.in_order_counter: int = 1 # resets when packet out of order # NOTE: # could be used, but isn't atm
        self.window_size: int = int(window_size) or (2 * max(self.h_limit, self.end_gap_threshold))

        # keep track of occuring gaps
        # eg. save to file or db when gaps are finalized
        # pop gap from this list to keep memory low
        self.occuring_gap: emil_types.Gap = None
        self.unfinished_gaps: list[emil_types.Gap] = []

    def __str__(self, show_records:int=0) -> str:
        s: str = f"[CrudeStreamAnalyzer #{self.stream_id}] window_size={self.window_size}, window={len(self.window)}, highest_seq={self.highest_seq}, gaps={self.gap_counter}"
        if show_records > 0:
            s += "".join([ f"\n\t{record.__dict__}" for record in self.window[-show_records:]])
        return s

    # def _add_record_to_tail_of_unfinished_gaps(self, record: emil_types.CrudeRecord) -> None:
    def _add_record_to_tail_of_unfinished_gaps(self) -> None:
        for i, gap in enumerate(self.unfinished_gaps):
            if len(gap.tail) >= self.t_limit: # Gap() is complete
                # finalize gap (write to file/db) and pop from list
                # print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][_update_unfinished_gaps] Gap found: {gap} ") # print gap that was detected
                print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][_update_unfinished_gaps] Gap found: {[r.seq for r in gap.head]} - {[r.seq for r in gap.tail]} ") # print gap that was detected
                print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][_update_unfinished_gaps] Gap found: {gap.to_json(indent=4)} ") # print gap that was detected
                del self.unfinished_gaps[i]
            else:
                gap.tail.append(self.window[-1]) # add last record to tail of occuring gaps


    def _gap_handler(self) -> None:

        # print(f"{not self.occuring_gap} and {self._diff()} >= {self.start_gap_threshold}  =>  {not self.occuring_gap and self._diff() >= self.start_gap_threshold}")
        # NOTE: maybe check if last packet wasn't an old one (check with highest_seq seen)
        # detect start of gap
        # if not self.occuring_gap and self.is_order: # currently not occuring a gap
        if not self.occuring_gap and self._diff() >= self.start_gap_threshold: # currently not occuring a gap
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_handler] last {self.start_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.start_gap_threshold*2:]]}") # print records that identifies end of gap
            t = emil_types.Gap.get_type(self._diff())
            self.occuring_gap = emil_types.Gap(type=t, from_adr="", from_ip="", to_adr="", to_ip="", datetime="", timestamp=1)
            h_start_index: int = -self.h_limit-1 # index of head start (#h_limit records before #start_gap_threshold records detected gap)
            self.occuring_gap.head = self.window[h_start_index:-1] # #h_limit records before gap start
            self.gap_counter += 1

        # detect end of gap
        if self.occuring_gap and self.is_order(self.window[-self.end_gap_threshold:]):
            t_start_index: int = -self.end_gap_threshold
            t_end_index: int = t_start_index + min(self.t_limit, self.end_gap_threshold)
            if t_end_index == 0:
                self.occuring_gap.add_records_to_tail(self.window[t_start_index:]) # add last #end_gap_threshold records because they are in order
            else:
                self.occuring_gap.add_records_to_tail(self.window[t_start_index:t_end_index]) # add last #end_gap_threshold records because they are in order
            self.unfinished_gaps.append(self.occuring_gap)
            self.occuring_gap = None

        self._add_record_to_tail_of_unfinished_gaps()


    def cleanup(self):
        """Do something with incomplete gaps"""
        while len(self.buffer) > 0:
            self.window.append(self.buffer.pop(0))
            # window is full, pop oldest record
            if len(self.window) > self.window_size:
                self.window.pop(0)
            self._gap_handler()

        if self.occuring_gap:
            self.gap_counter += 1
            print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][cleanup] Gap found: {[r.seq for r in self.occuring_gap.head]} - {[r.seq for r in self.occuring_gap.tail]} ") # print gap that was detected
            print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][cleanup] Gap found: {self.occuring_gap.to_json(indent=4)} ") # print gap that was detected
        for gap in self.unfinished_gaps:
            self.gap_counter += 1
            print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][cleanup] Gap found: {[r.seq for r in gap.head]} - {[r.seq for r in gap.tail]} ") # print gap that was detected
            print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][cleanup] Gap found: {gap.to_json(indent=4)} ") # print gap that was detected

    @staticmethod
    def is_order(records: list[emil_types.CrudeRecord]) -> bool:
        """Returns True if all of last n records are in order. Used to detect start/end of gap"""
        prev = records[0] if len(records) > 0 else None # first packet if any
        for record in records[1:]:
            if record.seq != prev.seq+1:
                return False
            prev = record
        return True

    def _diff(self) -> int:
        """Returns the sequence difference of the two latest records in window. Used to detect start/end of gap"""
        if len(self.window) >= 2:
            return self.window[-1].seq - self.window[-2].seq
        return -1

    def _update_in_order_counter(self) -> None:
        """
        Increments or resets in_order_counter.
        NB! assumes record has already been added to window (meaning: call this method after adding record to window)
        """
        # NOTE: could be used, but isn't atm
        # TODO: check if this faster than using is_order
        if len(self.window) < 2: # at least 2 records are needed for comparison
            return
        if int(self.window[-1].seq) != int(self.window[-2].seq)+1: # if the two latest packets are not in order
            self.in_order_counter = 1 # reset (a single record is always in order)
        else:
            self.in_order_counter += 1

    def _add_record(self, record: emil_types.CrudeRecord) -> None:

        bisect.insort(self.buffer, record) # faster way of appending element to list while maintaining order

        # buffer is full, move records to window
        if len(self.buffer) > self.window_size:
            self.window.append(self.buffer.pop(0)) # finally add record

        # window is full, pop oldest record
        if len(self.window) > self.window_size:
            self.window.pop(0)

        self._update_in_order_counter()
        self.record_counter += 1
        if record.seq > self.highest_seq:
            self.highest_seq = record.seq

    def add_record(self, record: emil_types.CrudeRecord) -> None:
        if record.id != self.stream_id:
            raise Exception(f"Record doesn't belong to this stream (#{self.stream_id})")
        # NOTE: order is important
        self._add_record(record)
        self._gap_handler()


class CrudeAnalyzer():
    """CrudeStreamAnalyzer wrapper. Handles multiple streams."""

    def __init__(self, analyzer_cls=CrudeStreamAnalyzer, analyzers={}, *args, **kwargs):
        self.kwargs: dict = kwargs
        self.analyzer_cls = analyzer_cls
        self.analyzers: dict = analyzers

    def __str__(self, *args, **kwargs) -> str:
        s: str = f"[CrudeAnalyzer] record_counter={self.record_count()}"
        s += "".join( [f"\n\t{analyzer.__str__(**kwargs)}" for analyzer in self.analyzers.values()] )
        return s

    def record_count(self) -> int:
        return sum([analyzer.record_counter for analyzer in self.analyzers.values()])

    def add_record(self, record: emil_types.CrudeRecord) -> None:
        id: int = record.id
        if id not in self.analyzers:
            self.analyzers[id] = self.analyzer_cls(stream_id=id, **self.kwargs)
        self.analyzers[id].add_record(record)

    def cleanup(self, *args, **kwargs):
        for analyzer in self.analyzers.values():
            analyzer.cleanup()
