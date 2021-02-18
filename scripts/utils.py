import queue
import microdep_types
from typing import Any


class CrudeStreamAnalyzer():
    """Analyzes crude records per stream-id. Does not handle multiple streams"""

    def __init__(self, stream_id, window_size, h_n, t_n, start_gap_threshold, end_gap_threshold, gap_mode=0, *args, **kwargs):
        self.stream_id: int = int(stream_id)
        self.window_size: int = int(window_size)
        self.h_n: int = int(h_n)
        self.t_n: int = int(t_n)
        self.start_gap_threshold: int = int(start_gap_threshold)
        self.end_gap_threshold: int = int(end_gap_threshold)
        self.gap_mode: int = int(gap_mode)
        self.head: list[microdep_types.CrudeRecord] = []
        self.tail: list[microdep_types.CrudeRecord] = []
        self.window: list[microdep_types.CrudeRecord] = []
        self.gap_modes: dict = {
            0: {'name': 'before', 'handler': self._gap_before_handler},
            1: {'name': 'during', 'handler': self._gap_during_handler},
            2: {'name': 'after', 'handler': self._gap_after_handler},
        }
        self.gap_counter: int = 0
        self.in_order_counter: int = 1 # resets when packet out of order

    def __str__(self, show_records:int=0) -> str:
        s: str = f"[CrudeStreamAnalyzer #{self.stream_id}] window_size={self.window_size}, window={len(self.window)}, gaps={self.gap_counter}"
        s += "".join([ f"\n\t{record.__dict__}" for record in self.window[-show_records:]])
        return s

    def set_next_gap_mode(self) -> None:
        self.gap_mode = (self.gap_mode+1) % len(self.gap_modes)
        # print(f"[CrudeStreamAnalyzer][set_next_gap_mode] gap_mode: {self.gap_modes[self.gap_mode]['name']}")

    def _gap_before_handler(self) -> None:
        """Detects gap and saves head"""
        # if self.in_order_counter == 0: # NOTE: may be faster, but is less flexible
        if not self.is_order(n=self.start_gap_threshold):
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_before_handler] last {self.start_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.start_gap_threshold*2:]]}") # print records that identifies end of gap
            h_start_i: int = self.h_n + self.start_gap_threshold # index of head start (#h_n records before #start_gap_threshold records detected gap)
            h_end_i: int = self.h_n # index of head end (#start_gap_threshold-records ago)
            self.head.append(self.window[-h_start_i:h_end_i]) # save #t_n records before gap start
            self.set_next_gap_mode()

    def _gap_during_handler(self) -> None:
        """Detects end of gap"""
        # if self.is_order(n=self.end_gap_threshold):
        if self.in_order_counter >= self.end_gap_threshold: # NOTE: may be faster?
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_during_handler] in_order_counter={self.in_order_counter}")
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_during_handler] last {self.end_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.end_gap_threshold*2:]]}") # print records that identifies end of gap
            self.set_next_gap_mode()
            self.gap_counter += 1

    def _gap_after_handler(self) -> None:
        """Saves tail-records until t_n, creates a gap record, empties head & tail"""
        self.tail.append(self.window[-1])
        if len(self.tail) == self.t_n:
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_after_handler] Gap created")
            # print(f"[CrudeStreamAnalyzer][_gap_after_handler] head: {self.head}")
            self.head = []
            self.tail = []
            self.set_next_gap_mode()

    def is_order(self, n: int) -> bool:
        """Returns True if all of last n records are in order. Used to detect start/end of gap"""
        if len(self.window) < n:
            return True
        prev = self.window[-n]
        for record in self.window[-n+1:]:
            if int(record.seq) != int(prev.seq)+1:
                return False
            prev = record
        return True

    def _update_in_order_counter(self) -> None:
        """
        Increments or resets in_order_counter.
        NB! assumes record has already been added to window (meaning: call this method after adding record to window)
        """
        # TODO: check if this faster than using is_order
        if len(self.window) < 2: # at least 2 records are needed for comparison
            return
        if int(self.window[-1].seq) != int(self.window[-2].seq)+1: # if the two latest packets are not in order
            self.in_order_counter = 1 # reset (a single record is always in order)
        else:
            self.in_order_counter += 1

    def add_record_to_window(self, record: microdep_types.CrudeRecord) -> None:
        """Adds record and updates in_order_counter"""
        if len(self.window) == self.window_size:
            self.window.pop(0) # pop oldest record because window is full

        self.window.append(record) # finally add record

    def add_record(self, record: microdep_types.CrudeRecord) -> None:
        if record.id != self.stream_id:
            raise Exception(f"Record doesn't belong to this stream (#{self.stream_id})")
        self.add_record_to_window(record)
        self._update_in_order_counter()
        self.gap_modes[self.gap_mode]['handler']() # process gap
        self._after_add_record_hook()

    def _after_add_record_hook(self) -> None:
        # self.stats['counter'] += 1
        pass


class CrudeAnalyzer():
    """CrudeStreamAnalyzer wrapper. Handles multiple streams."""

    def __init__(self, analyzer=CrudeStreamAnalyzer, analyzers={}, *args, **kwargs):
        self.kwargs: dict = kwargs
        self.analyzer = analyzer
        self.analyzers: dict = analyzers
        self.record_counter = 0

    def __str__(self, *args, **kwargs) -> str:
        s: str = f"[CrudeAnalyzer] record_counter={self.record_counter}"
        s += "".join( [f"\n\t{analyzer.__str__(**kwargs)}" for analyzer in self.analyzers.values()] )
        return s

    def add_record(self, record: microdep_types.CrudeRecord) -> None:
        id: int = record.id
        if id not in self.analyzers:
            self.analyzers[id] = self.analyzer(stream_id=id, **self.kwargs)
        self.analyzers[id].add_record(record)
        self.record_counter += 1
