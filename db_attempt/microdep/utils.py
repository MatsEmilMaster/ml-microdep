import inspect
from typing import Any
from microdep import models as microdep_models

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
    required_fields: list[str] = []

    def __init__(self, *args, **kwargs):
        self._required_fields.extend(AnnotatedI.required_fields) # must be called before super().__init__()
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



class CrudeAnalyzer2(AnnotatedI):
    """Analyzes crude records per stream-id"""

    window_size: int
    records: dict[str, list[microdep_models.CrudeRecord]] = {} # Queue for each stream-id in CrudeRecord
    stats: dict[str, dict[str, Any]] = {}
    _stats_init: dict[str, Any] = {
        'counter': 0,
        'counter': 0,
    }

    required_fields: list[str] = ['window_size']

    def __init__(self, *args, **kwargs):
        self._required_fields.extend(CrudeAnalyzer2.required_fields) # must be called before super().__init__()
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}, window_size={self.window_size}\n{self.__str_queues__()}"

    def __str_queues__(self) -> str:
        """Returns str representation of existing records"""
        return "\n".join( [f"queue #{id}: {len(q)} records" for id, q in self.records.items()] )

    def add_record(self, record: microdep_models.CrudeRecord) -> None:
        """Add record and move window when full"""
        i = record.stream_id
        if not i in self.records:
            self.records[i] = []
        elif len(self.records[i]) == self.window_size:
            self.records[i].pop(0) # pop record
        self.records[i].append(record) # finally add record
        self._after_add_record_hook(id=i)

    def _after_add_record_hook(self, id: str) -> None:
        if not id in self.stats:
            # init dict if stats for this stream-id doesn't exist
            self.stats[id] = self._stats_init
        self.stats[id]['counter'] += 1
