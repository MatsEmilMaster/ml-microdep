# from typing import List, Any
import json
import inspect

class BaseInterface:

    def __init__(self, *args, **kwargs):
        """Enables kwargs"""
        pass

    def get_all_annotations(self) -> dict[str, object]:
        """Find all annotated attrs from inherited classes (including self)"""
        annotations: dict[str, object] = {}
        for cls in inspect.getmro(self.__class__): # for each parent class
            try:
                annotations.update(cls.__annotations__) # not all objects has __annotations__
                # annotations.update({attr:None for attr in cls.__annotations__}) # not all objects has __annotations__
            except:
                pass
        return annotations

    def get_all_attr_names(self) -> list[str]:
        return list(self.get_all_annotations().keys())



class AnnotatedI(BaseInterface):
    """
    This interface will only allow to set attrs that has been annotated. Also support required fields.
    To solve The Diamond Problem on multiple inheritance, redefine 'required_fields' on the child class.

    extended classes must define
    def __init__(self, *args, **kwargs):
        self._required_fields.extend(__class__.required_fields) # must be called before super().__init__()
        super().__init__(*args, **kwargs)
    """

    _required_fields: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self._set_allowed_attrs(**kwargs)
        self._check_required_fields(**kwargs)

    def _set_allowed_attrs(self, **kwargs):
        attr_names = self.get_all_attr_names()
        for attr, value in kwargs.items():
            if attr in attr_names:
                setattr(self, attr, value)
            else:
                print(f"[warning][{self.__class__.__name__}]: Attr '{attr}' not allowed")

    def _check_required_fields(self, **kwargs):
        """Checks if required fields exists after '_set_allowed_attrs'"""

        for field in self._required_fields:
            if not hasattr(self, field):
                raise NotImplementedError(f"[{self.__class__.__name__}] requires attr '{field}'")



class EventI(AnnotatedI):
    """
    Interface for events
    event_type [snmp_trap, trace_route, correlation_match, gap, unique_correlation_match, jitter]
    """
    event_type: str # if not set, raise exception. [snmp_trap, trace_route, correlation_match, gap, unique_correlation_match, jitter]
    required_fields = ['event_type']

    def __init__(self, *args, **kwargs):
        self._required_fields.extend(EventI.required_fields)
        super().__init__(*args, **kwargs)


class CorrelationEventI(EventI):
    """
    match_type [before, before_and_after, after, trace_route_stats, raw_trace_route, trace_route, route_changed]
    """
    event_type: str = "correlation_match"
    match_type: str # [before, before_and_after, after, trace_route_stats, raw_trace_route, trace_route, route_changed]
    required_fields = ['match_type']

    def __init__(self, *args, **kwargs):
        self._required_fields.extend(CorrelationEventI.required_fields)
        super().__init__(*args, **kwargs)


# ------------------------------------------------------------------------------

class LinkTrap(EventI):
    timestamp: float # When the link change occurred.
    trap_source: str # The ip of the link.
    name: str # The domain of the link.
    trap_type: str # Which change? (linkUp or linkDown)
    ifIndex: int # Port Index - the SNMP index for the port/interface
    ifDescr: str # The Interface Description field from SNMP
    ifAlias: str # Unique Port name generated by router
    logical_name: str # The UNINETT name of the port from the UNINETT formatted ifDescr
    event_type: str # which record this is (snmp_trap)


class TrapDowntime(EventI):
    # QUESTION: is this related to LinkTrap?
    name: str
    timestamp_down: float
    timestamp_up: float
    t_down: float
    ifAlias: str
    logical_name: str
    event_type: str = "trap_downtime"


class Jitter(EventI):
    from_: str
    from_adr: str
    to: str
    to_adr: str
    date: str
    datetime: str
    timestamp: float
    timestamp_zone: str = "GMT"
    h_ddelay: float
    h_delay: float
    h_jit: float
    h_min_d: float
    h_n: int
    h_slope_10: float
    rdelay: list[float]
    report_type: str = "interval"
    rtx: list[float]
    slopes: list[str]
    event_type: str = "jitter"


class GapSum(EventI):
    from_: str # "ytelse-osl.uninett.no",
    from_adr: str # "158.39.1.126",
    to: str # "teknobyen-mp.uninett.no",
    to_adr: str # "158.38.2.4",
    date: str # "2021-01-25T22:59:31.431",
    datetime: str # "2021-01-25T22:59:31.431",
    timestamp: float # 1611615571.43106,
    timestamp_zone: str = "GMT"
    big_gaps: int # 0,
    big_time: float # 0,
    dTTL: float # 0,
    down_ppm: float # 0,
    duplicates: int # 0,
    h_ddelay: float # 0.048,
    h_ddelay_sdv: float # 0.0329894167778323,
    h_delay: float # 3.981,
    h_delay_sdv: float # 0.0384022571702068,
    h_jit: float # 0.021,
    h_jit_sdv: float # 0.0608529272927811,
    h_min_d: float # 3.93,
    h_min_d_sdv: float # 0.0211482621124494,
    h_slope_10: float # 0,
    h_slope_10_sdv: float # 0,
    lasted: str # "23:59:18",
    lasted_sec: float # 86358.989,
    late: int # 0,
    late_sec: int # 0,
    least_delay: float # "3.867",
    reordered: int # 0,
    resets: int # 0,
    small_gaps: int # 0,
    small_time: float # 0,
    event_type: str = "gapsum"


# ------------------------------------------------------------------------------

class IcmpGap(EventI):
    # QUESTION: where is this used?
    ts_start: float
    ts_end: float
    uncreachable: str # host/ip eg. "uninett/127.0.0.1"
    source: str # host/ip
    dst: str # host/ip
    duration: float # ts_end - ts_start
    packet_count: int
    # event_type: str


class LinkGapMatch(CorrelationEventI):
    """
    These records are created using all_correlation.py
    All of the different kinds of matching is just different attempts at trying
    to explain why the gap happened. So for instance the first match_type before
    is just when i try to find a gap record that happened at about the same time
    as an snmp_trap record. 5 different kinds of matching. (match_type).

    before: Checks that the timestamp for gap is +- the same as the trap and check
    if the start of a gap.from (or gap.to) (example: tromso-gw3.uninett.no) so tromso in this case,
    is the same as the first part of the trap.name example tromso-gw.uninett.no.
    Or if the trap.name is in one of the routers used for the trace_route (trace_route index).

    before_and_after: Check if there is also a trap for the same link going up
    at the time: timestamp_gap + tloss.

    after: Checks that the timestamp for the gap+tloss is +- the same as a trap with the trap_type: linkUp.
    And also the same check as before to make sure the trap was very near a router that was actually used by the gap.
    The reason why there sometimes are more before_and_after correlations than just after correlations is because a before_and_after's first
    trap can be n different and for each one of these there can be m number of last traps.
    """
    routers_used: list[str] # [ a list of routers used from "from" to "to" from the trace_route_stats records.  ],
    timestamp: int # gap's
    from_: str # from (gap.from) is also the same as trace_route_stats from
    to: str # to (gap.to) is also the same as trace_route stats to.
    tloss: float # gap's
    timestamp_zone: str # timezone for all the timestamps
    name: str # trap's
    timestamp_trap: int # trap's
    logical_name: str # trap's
    ifAlias: str # trap's
    trap_type: str # trap's [LinkUp]
    trap_source: str # trap's
    event_type = "correlation_match" # is always "correlation_match"


# ------------------------------------------------------------------------------

# class BeforeRoutingTrap(CorrelationEventI):
#     """Like before but also correlating with a routing change that happened at the same time. once I get bgp set up."""
#     pass
#     # QUESTION: spør om denne
#
# class BeforeAndAfterRoutingTrap(CorrelationEventI):
#     """Like before_and_after but also correlating with a routing change that happened at the same time."""
#     pass
#     # QUESTION: spør om denne


# ------------------------------------------------------------------------------

class HopStats:
    first_seen: float # the first time this router was seen
    last_seen: float # the last time this router was seen
    seen: int # how many times it was seen
    sdv: float # standard deviation ping (ms)
    avg: float # average ping
    min: float # minimum ping
    max: float # maximum
    hop: int # which hop number this is
    loss: float # loss %
    router: str # which router # QUESTION: spør om denne
    address: str # the ip of this router.

class TraceRoute(EventI):
    from_: str # where the trace_route started (should always be the same as gap.from)
    to: str # end location of trace_route (should always be the same as gap.to)
    timestamp_to: float # end of the day (midnight)
    timestamp_from: float # start of the day (midnight)
    timestamp_zone: str = "GMT"
    tags: list[str] = ["beats_input_codec_plain_applied"]
    stats: list[HopStats] # [ A list containing every router that was used for this day in the path from (gap.from) to (gap.to). and their corresponding stats. ],
    routers_used: list[str] # [ a list containing just the routers used and not their stats.]
    event_type: str = "trace_route"

class TraceRouteStats(CorrelationEventI):
    """This one checks if the route recently was changed in the trace_route_stats records. Not using traps."""

    from_: str # gap's
    to: str # gap's
    timestamp: float # gap's
    timestamp_zone: str # all timestamps
    trace_route: TraceRoute
    tloss: float # gap's
    match_type: str = "trace_route_stats"
    event_type: str = "correlation_match"



class Probe:
    name: str # domain if it was found, if not then the ip.
    rtt: float # round trip time in ms
    ip: str # ip address.

class Hop:
    probes: list[Probe] # Only 6 probes

class RawTraceRoute(EventI):
    from_: str # domain where the trace_route started should be the same as gap's from
    to: str # domain where the trace_route stopped, should be the same as gap's to.
    to_ip: str # which ip the trace_route was to.
    timestamp: str # raw_trace_route's
    trace_route: list[Hop] # [a list containing multiple lists (hops) with 6 probes in them. at least one of hops has 6 probes with all null values. (that's when I log the original raw_trace_routes)
    event_type: str = "raw_trace_route"


class RawTraceRouteStats(CorrelationEventI):
    """
    Check if there is a raw_trace_route record with the same 'to' and 'from' as the gap and at the same time+-.
    If there is a record then that means that the raw_trace_route contains atleast one * * * * * *.
    """
    from_: str # gap's
    to: str # gap's
    tloss: float # gap's
    timestamp: float # gap's
    timestamp_zone: str # gap's
    raw_trace_route: RawTraceRoute
    match_type: str = "raw_trace_route"
    event_type: str = "correlation_match"


# ------------------------------------------------------------------------------

class RouteChange(EventI):
    timestamp: float # route_change's
    router_id: str # Ip of the router that changed a prefix.
    exabgp_router: str #  which exabgp-router sent this log
    ls_nlri_type: str # 3 for ipv4, 4 for ipv6
    ip_reach_prefix: str # ip and prefix that changed.
    change_type: str # either "announce" or "withdraw" if you announce a new prefix or remove one.
    event_type: str = "route_changed"

class RoutingTrap(CorrelationEventI):
    """Check if there is a trap with an ip that is the same ip as route_change.router_id at the same time+-."""
    name: str # trap's
    timestamp: float # trap's
    timestamp_trap: float # trap's (same as the attribute timestamp) # QUESTION: ???
    timestamp_zone: str # trap's
    logical_name: str # trap's
    ifAlias: str # trap's
    trap_type: str # trap's
    trap_source: str # trap's (this ip is the same as route_change.router-id)
    route_change: RouteChange
    match_type: str = "routing_trap"
    event_type: str = "correlation_match"


# routing ----------------------------------------------------------------------

class BgpUpdate(EventI):
    name: str # Name of which prefix. bgp
    timestamp_zone: str = "GMT" # "GMT"
    prefix: str # bgp_update's
    community: list # [bgp_update's], # QUESTION: what is in this?
    source_id: str # bgp_update's
    as_path: list # [bgp_update's],
    timestamp: float # bgp_update's
    type: str # bgp_update's. A for announcements and W for withdraws.
    event_type: str = "bgp_update"

class Routing(CorrelationEventI):
    """
    Three different ways of matching a route record with a gap record.
    The first one is: get a Prefix from a bgp_update and check if either gap.from_adr or
    gap.to_adr is in the prefix of the bgp_update. (routing_match_type=before)
    The second one is when a withdraw record happens at gap.timestamp and announce
    record for the same prefix at gap.timestamp + gap.tloss.
    And also check is the gap.from_adr or gap.to_adr is in the prefix from the bgp_update (routing_match_type=before_and_after)
    The last one is when a routing change also matches when a new route was seen.
    So it goes through every stat in the trace_route_stats and tries to find a first_seen that is +- the same as the gap.timestamp (routing_match_type=trace_route_stats)
    """
    from_: str # gap's
    to: str # gap's
    from_adr: str # Sometimes found in raw gaps and sometimes I create this myself using a text file mp-names.
    to_adr: str # Sometimes found in raw gaps and sometimes I create this myself using a text file mp-names.
    timestamp: float # gap's
    timestamp_zone: str = "GMT" # Always GMT
    tloss: float # gap's
    ip_list: list[str] # [A list of IPs including: gap.to IP and gap.from IP and all the IPs used in the trace_route from (gap.from) to (gap.to).],
    bgp_update: BgpUpdate
    match_type: str = "bgp_update"
    event_type: str = "correlation_match"

# ------------------------------------------------------------------------------


class Gap(EventI):
    from_: str # "volda-mp.hivolda.no" # Who it was sent from.
    to: str # "ntnu-mp.ntnu.no" # Receiver.
    datetime: str # "2018-05-16 18:06:25" # When the gap occurred. Human readable formatted time in second resolution.
    timestamp: float # Time in seconds since 1970. This timestamp is more accurate then the datetime attribute. In milliseconds.
    timestamp_zone: str # Which timezone the timestamp is in.
    h_ddelay: float # Average of the 50 (h_n) packets in the header minus the fastest of the 1000 packets.
    h_delay: float # rx-tx average for the last 50 packets
    h_jit: float # the jitter in header
    h_min_d: float # Minimum rx-tx for the last 50 packets.
    h_n: int # How many packets in the header. usually 50.
    h_slope_10: float # The ```a``` in ```y=ax+b``` on the 10'th last packet.
    h_slope_20: float # Like above only 20'th last.
    h_slope_30: float # Like above only 30'th last.
    h_slope_40: float # Like above only 40'th last.
    h_slope_50: float # Like above only 50'th last.
    overlap: int # Number of gaps overlapping eachother with head and tail. This is normally 1. Might be unstable if more than 1.
    t_ddelay: float # Like the header, only for the tail
    t_delay: float # Like the header, only for the tail
    t_jit: float # Like the header, only for the tail
    t_min_d: float # Like the header, only for the tail
    t_n: int # Like the header, only for the tail
    t_slope_10: float # 10'th first.
    t_slope_20: float # 20'th first.
    t_slope_30: float # 30'th first.
    t_slope_40: float # 40'th first.
    t_slope_50: float # 50'th first.
    tloss: float # When a gap occurs tloss is the time between when you got packets correctly ordered and when you got 5 packets in a row again.
    event_type: str = "gap" # Should always be "gap" for these records.


if __name__ == "__main__":
    pass
    # gap = Gap()
    # gap.a()

    # print(gap.event_type)
