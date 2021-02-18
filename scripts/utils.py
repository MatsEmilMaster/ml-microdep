import queue
import microdep_types
from typing import Any, Optional


class CrudeStreamAnalyzer():
    """Analyzes crude records for single stream-id"""


    GAP_MODE_BEFORE: str = 'before'
    GAP_MODE_DURING: str = 'during'
    GAP_MODE_AFTER: str = 'after'

    GAP_MODE_SEARCHING: str = 'searching'
    GAP_MODE_OCCURING: str = 'occuring'

    def __init__(self, stream_id, window_size, h_limit, t_limit, start_gap_threshold, end_gap_threshold, gap_mode=0, *args, **kwargs):
        self.stream_id: int = int(stream_id)
        self.window_size: int = int(window_size)
        self.h_limit: int = int(h_limit)
        self.t_limit: int = int(t_limit)
        self.start_gap_threshold: int = int(start_gap_threshold)
        self.end_gap_threshold: int = int(end_gap_threshold)
        self.gap_mode: str = gap_mode
        self.head: list[microdep_types.CrudeRecord] = [] # depricated
        self.tail: list[microdep_types.CrudeRecord] = [] # depricated
        self.window: list[microdep_types.CrudeRecord] = []
        self.gap_modes: dict = {
            CrudeStreamAnalyzer.GAP_MODE_BEFORE: {'handler': self._gap_before_handler},
            CrudeStreamAnalyzer.GAP_MODE_DURING: {'handler': self._gap_during_handler},
            CrudeStreamAnalyzer.GAP_MODE_AFTER: {'handler': self._gap_after_handler}, # BUG: new gaps are not detected while in this mode
            CrudeStreamAnalyzer.GAP_MODE_SEARCHING: {'handler': self._gap_searching_handler}, # BUG: new gaps are not detected while in this mode
            CrudeStreamAnalyzer.GAP_MODE_OCCURING: {'handler': self._gap_occuring_handler}, # BUG: new gaps are not detected while in this mode
        }
        self.gap_counter: int = 0
        self.in_order_counter: int = 1 # resets when packet out of order

        # keep track of occuring gaps
        # eg. save to file or db when gaps are finalized
        # pop gap from this list to keep memory low
        self.occuring_gaps: list[microdep_types.Gap2] = []

    def __str__(self, show_records:int=0) -> str:
        s: str = f"[CrudeStreamAnalyzer #{self.stream_id}] window_size={self.window_size}, window={len(self.window)}, gaps={self.gap_counter}"
        s += "".join([ f"\n\t{record.__dict__}" for record in self.window[-show_records:]])
        return s

    def set_next_gap_mode(self, mode:Optional[int]=None) -> None:
        """Set mode or increment""" # depricated
        self.gap_mode = mode or (self.gap_mode+1) % len(self.gap_modes)
        # print(f"[CrudeStreamAnalyzer][set_next_gap_mode] gap_mode: {self.gap_modes[self.gap_mode]['name']}")

    def _gap_before_handler(self) -> None:
        """Detects gap and saves head"""
        # if self.in_order_counter == 0: # NOTE: may be faster, but is less flexible
        if not self.is_order(n=self.start_gap_threshold):
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_before_handler] last {self.start_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.start_gap_threshold*2:]]}") # print records that identifies end of gap
            h_start_i: int = self.h_limit + self.start_gap_threshold # index of head start (#h_limit records before #start_gap_threshold records detected gap)
            h_end_i: int = self.h_limit # index of head end (#start_gap_threshold-records ago)
            self.head.append(self.window[-h_start_i:h_end_i]) # save #t_limit records before gap start
            self.gap_mode = CrudeStreamAnalyzer.GAP_MODE_DURING

    def _gap_during_handler(self) -> None:
        """Detects end of gap"""
        # if self.is_order(n=self.end_gap_threshold):
        if self.in_order_counter >= self.end_gap_threshold: # NOTE: may be faster?
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_during_handler] in_order_counter={self.in_order_counter}")
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_during_handler] last {self.end_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.end_gap_threshold*2:]]}") # print records that identifies end of gap
            self.gap_counter += 1
            self.gap_mode = CrudeStreamAnalyzer.GAP_MODE_AFTER

    def _gap_after_handler(self) -> None:
        """Saves tail-records until t_limit, creates a gap record, empties head & tail"""
        self.tail.append(self.window[-1])
        if len(self.tail) == self.t_limit:
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_after_handler] Gap created")
            # print(f"[CrudeStreamAnalyzer][_gap_after_handler] head: {self.head}")
            self.head = []
            self.tail = []
            self.set_next_gap_mode()

    def _update_occuring_gaps(self) -> None:
        # add packet to tail of occuring gaps
        for i, gap in enumerate(self.occuring_gaps):
            gap.tail.append(self.window[-1]) # add last record to tail of occuring gaps
            if len(gap.tail) >= self.t_limit:
                # finalize gap and pop from list
                del self.occuring_gaps[i]

    def _gap_searching_handler(self) -> None:
        self._update_occuring_gaps()


        # if self.in_order_counter == 0: # NOTE: may be faster, but is less flexible
        if not self.is_order(n=self.start_gap_threshold):
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_before_handler] last {self.start_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.start_gap_threshold*2:]]}") # print records that identifies end of gap
            h_start_i: int = self.h_limit + self.start_gap_threshold # index of head start (#h_limit records before #start_gap_threshold records detected gap)
            h_end_i: int = self.h_limit # index of head end (#start_gap_threshold-records ago)
            self.occuring_gaps.append( microdep_types.Gap2(from_adr=) )
            # self.head.append(self.window[-h_start_i:h_end_i]) # save #t_limit records before gap start
            self.gap_mode = CrudeStreamAnalyzer.GAP_MODE_OCCURING

    def _gap_occuring_handler(self) -> None:
        """Detects gap and saves head"""
        # if self.in_order_counter == 0: # NOTE: may be faster, but is less flexible
        if not self.is_order(n=self.start_gap_threshold):
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_before_handler] last {self.start_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.start_gap_threshold*2:]]}") # print records that identifies end of gap
            h_start_i: int = self.h_limit + self.start_gap_threshold # index of head start (#h_limit records before #start_gap_threshold records detected gap)
            h_end_i: int = self.h_limit # index of head end (#start_gap_threshold-records ago)
            self.head.append(self.window[-h_start_i:h_end_i]) # save #t_limit records before gap start
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
