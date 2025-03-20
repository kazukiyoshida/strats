from time import sleep, time

from prometheus_client import Gauge

from strats.core import DataWithMetrics, singletondataclass
from strats.model import PricesData, PricesMetrics, prices_mapper


@singletondataclass
class State:
    usdjpy: DataWithMetrics[PricesData, PricesMetrics]
    btcusd: DataWithMetrics[PricesData, PricesMetrics]
    time: DataWithMetrics[str, str]


print("==== start ====")

usdjpy_prices = DataWithMetrics(
    data=PricesData(bid=0, ask=0),
    metrics=PricesMetrics(prefix="usdjpy"),
    mapper=prices_mapper,
)

btcusd_prices = DataWithMetrics(
    data=PricesData(bid=0, ask=0),
    metrics=PricesMetrics(prefix="btcusd"),
    mapper=prices_mapper,
)

t = DataWithMetrics(
    data=int(time()),
    metrics=Gauge("time", ""),
    mapper=lambda d, m: m.set(d),
)

s = State(
    usdjpy=usdjpy_prices,
    btcusd=btcusd_prices,
    time=t,
)

print("s: ", s)

print("======= time ==============")

print("------- before")
print("s.time:             ", s.time)
print("s.time.data:        ", s.time.data)
print("s.time.metrics:     ", s.time.metrics)

sleep(2)
s.time.data = int(time())

print("------- after")
print("s.time:             ", s.time)
print("s.time.data:        ", s.time.data)
print("s.time.metrics:     ", s.time.metrics)

print("======= usdjpy ==============")

print("------- before")
print("s.usdjpy:             ", s.usdjpy)
print("s.usdjpy.data:        ", s.usdjpy.data)
print("s.usdjpy.metrics:     ", s.usdjpy.metrics)
print("s.usdjpy.metrics.bid: ", s.usdjpy.metrics.bid._value.get())

s.usdjpy.data = PricesData(bid=100, ask=102)

print("------- after")
print("s.usdjpy:             ", s.usdjpy)
print("s.usdjpy.data:        ", s.usdjpy.data)
print("s.usdjpy.metrics:     ", s.usdjpy.metrics)
print("s.usdjpy.metrics.bid: ", s.usdjpy.metrics.bid._value.get())

print("======= btcusd ==============")

print("------- before")
print("s.btcusd:             ", s.btcusd)
print("s.btcusd.data:        ", s.btcusd.data)
print("s.btcusd.metrics:     ", s.btcusd.metrics)
print("s.btcusd.metrics.bid: ", s.btcusd.metrics.bid._value.get())

s.btcusd.data = PricesData(bid=900, ask=902)

print("------- after")
print("s.btcusd:             ", s.btcusd)
print("s.btcusd.data:        ", s.btcusd.data)
print("s.btcusd.metrics:     ", s.btcusd.metrics)
print("s.btcusd.metrics.bid: ", s.btcusd.metrics.bid)
print("s.btcusd.metrics.bid: ", s.btcusd.metrics.bid._value.get())

print("==== end ====")
