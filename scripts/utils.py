import queue
import microdep_types
from typing import Any, Optional


class CrudeStreamAnalyzer():
    """Analyzes crude records for single stream-id"""

    def __init__(self, stream_id, window_size, h_limit, t_limit, start_gap_threshold, end_gap_threshold, *args, **kwargs):
        self.stream_id: int = int(stream_id)
        self.window_size: int = int(window_size)
        self.h_limit: int = int(h_limit)
        self.t_limit: int = int(t_limit)
        self.start_gap_threshold: int = int(start_gap_threshold)
        self.end_gap_threshold: int = int(end_gap_threshold)
        self.window: list[microdep_types.CrudeRecord] = []
        self.gap_counter: int = 0
        self.in_order_counter: int = 1 # resets when packet out of order # NOTE: # could be used, but isn't atm


        # keep track of occuring gaps
        # eg. save to file or db when gaps are finalized
        # pop gap from this list to keep memory low
        self.occuring_gap: microdep_types.Gap2 = None
        self.unfinished_gaps: list[microdep_types.Gap2] = []

    def __str__(self, show_records:int=0) -> str:
        s: str = f"[CrudeStreamAnalyzer #{self.stream_id}] window_size={self.window_size}, window={len(self.window)}, gaps={self.gap_counter}"
        if show_records > 0:
            s += "".join([ f"\n\t{record.__dict__}" for record in self.window[-show_records:]])
        return s

    def _add_record_to_tail_of_unfinished_gaps(self, record: microdep_types.CrudeRecord) -> None:
        for i, gap in enumerate(self.unfinished_gaps):
            if len(gap.tail) >= self.t_limit: # Gap() is complete
                # finalize gap (write to file/db) and pop from list
                # print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][_update_unfinished_gaps] Gap found: {gap} ") # print gap that was detected
                # print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][_update_unfinished_gaps] Gap found: {[r.seq for r in gap.head]} - {[r.seq for r in gap.tail]} ") # print gap that was detected
                print(f"\n[CrudeStreamAnalyzer #{self.stream_id}][_update_unfinished_gaps] Gap found: {gap.to_json(indent=4)} ") # print gap that was detected
                del self.unfinished_gaps[i]
            else:
                gap.tail.append(record) # add last record to tail of occuring gaps


    def _gap_handler(self) -> None:

        # detect start of gap
        if not self.occuring_gap and not self.is_order(n=self.start_gap_threshold):
            # print(f"[CrudeStreamAnalyzer #{self.stream_id}][_gap_handler] last {self.start_gap_threshold*2} packets: {[(record.id, record.seq) for record in self.window[-self.start_gap_threshold*2:]]}") # print records that identifies end of gap
            self.occuring_gap = microdep_types.Gap2(from_adr="", from_ip="", to_adr="", to_ip="", datetime="", timestamp=1)
            h_start_i: int = self.h_limit + self.start_gap_threshold - 1 # index of head start (#h_limit records before #start_gap_threshold records detected gap)
            h_end_i: int = self.start_gap_threshold-1 # index of head end (#start_gap_threshold-records ago)
            self.occuring_gap.head = self.window[-h_start_i:-h_end_i] # #h_limit records before gap start
            self.gap_counter += 1

        # detect end of gap
        if self.occuring_gap and self.is_order(n=self.end_gap_threshold):
            t_start_index: int = -self.end_gap_threshold
            t_end_index: int = t_start_index + min(self.t_limit, self.end_gap_threshold)
            if t_end_index == 0:
                self.occuring_gap.tail.extend(self.window[t_start_index:]) # add last #end_gap_threshold records because they are in order
            else:
                self.occuring_gap.tail.extend(self.window[t_start_index:t_end_index]) # add last #end_gap_threshold records because they are in order
            self.unfinished_gaps.append(self.occuring_gap)
            self.occuring_gap = None

    def cleanup(self):
        """Do something with incomplete gaps"""
        pass # TODO: implement

    def is_order(self, n: int) -> bool:
        """Returns True if all of last n records are in order. Used to detect start/end of gap"""
        records_to_inspect = self.window[-n:]
        prev = records_to_inspect[0]
        for record in records_to_inspect[1:]:
            if record.seq != prev.seq+1:
                return False
            prev = record
        return True

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

    def add_record_to_window(self, record: microdep_types.CrudeRecord) -> None:
        """Adds record to window"""
        if len(self.window) == self.window_size:
            self.window.pop(0) # pop oldest record because window is full
        self.window.append(record) # finally add record
        self._update_in_order_counter()


    def add_record(self, record: microdep_types.CrudeRecord) -> None:
        if record.id != self.stream_id:
            raise Exception(f"Record doesn't belong to this stream (#{self.stream_id})")
        # NOTE: order is important
        self.add_record_to_window(record)
        self._add_record_to_tail_of_unfinished_gaps(record)
        self._gap_handler()


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
