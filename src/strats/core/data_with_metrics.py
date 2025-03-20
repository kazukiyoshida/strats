from typing import Callable, Generic, Optional, TypeVar

D = TypeVar("D")
M = TypeVar("M")
MapperFunction = Callable[[D, M], None]


class DataWithMetrics(Generic[D, M]):
    def __init__(
        self,
        data: D,
        metrics: Optional[M] = None,
        mapper: Optional[MapperFunction] = None,
    ):
        self._data = data
        self._metrics = metrics
        self._mapper = mapper

    @property
    def data(self) -> D:
        return self._data

    @data.setter
    def data(self, value: D):
        self._data = value
        if self._mapper is not None:
            self._mapper(self._data, self._metrics)

    @property
    def metrics(self) -> Optional[M]:
        return self._metrics
