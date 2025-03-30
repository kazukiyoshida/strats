from dataclasses import dataclass
from unittest.mock import Mock, call

from strats.core import Data, State


@dataclass
class DummySource:
    s: int = 0


@dataclass
class DummyData:
    d: str = "0"


@dataclass
class DummyMetrics:
    m: float = 0.0


def test_data_update():
    def dummy_source_to_data(source: DummySource) -> DummyData:
        return DummyData(d=str(source.s))

    def dummy_data_to_metrics(data: DummyData) -> DummyMetrics:
        return DummyMetrics(m=float(data.d))

    class DummyState(State):
        num = Data(
            source_class=DummySource,
            data_class=DummyData,
            metrics_class=DummyMetrics,
            source_to_data=dummy_source_to_data,
            data_to_metrics=dummy_data_to_metrics,
        )

    state = DummyState()

    assert state.num.d == "0"
    assert DummyState.num._metrics.m == 0.0

    state.num = DummySource(s=1)
    assert state.num.d == "1"
    assert DummyState.num._metrics.m == 1.0

    del state.num
    assert state.num.d == "0"
    assert DummyState.num._metrics.m == 0.0


def test_data_lifecycle_hook():
    # Mock Parent
    lifecycle = Mock()

    # Mock children
    pre_init = lifecycle.pre_init
    post_init = lifecycle.post_init
    pre_data_set = lifecycle.pre_data_set
    post_data_set = lifecycle.post_data_set
    pre_metrics_set = lifecycle.pre_metrics_set
    post_metrics_set = lifecycle.post_metrics_set
    pre_del = lifecycle.pre_del
    post_del = lifecycle.post_del

    source_to_data = lifecycle.source_to_data
    source_to_data.side_effect = lambda s: DummyData(d=str(s.s))

    data_to_metrics = lifecycle.data_to_metrics
    data_to_metrics.side_effect = lambda d: DummyMetrics(m=float(d.d))

    class DummyState(State):
        num = Data(
            source_class=DummySource,
            data_class=DummyData,
            metrics_class=DummyMetrics,
            source_to_data=source_to_data,
            data_to_metrics=data_to_metrics,
            pre_init=pre_init,
            post_init=post_init,
            pre_data_set=pre_data_set,
            post_data_set=post_data_set,
            pre_metrics_set=pre_metrics_set,
            post_metrics_set=post_metrics_set,
            pre_del=pre_del,
            post_del=post_del,
        )

    state = DummyState()

    # Update state data
    source = DummySource(s=123)
    state.num = source

    # Delete state data
    del state.num

    # Test the calls order
    assert lifecycle.mock_calls == [
        call.pre_init(),
        call.post_init(),
        call.pre_data_set(state, source),
        call.source_to_data(source),
        call.post_data_set(state, DummyData(d="123")),
        call.pre_metrics_set(state, DummyData(d="123")),
        call.data_to_metrics(DummyData(d="123")),
        call.post_metrics_set(state, DummyMetrics(m=123.0)),
        call.pre_del(state),
        call.post_del(state),
    ]
