# Changelog

## 0.1.6

Released 2025-05-04

- Rename util module to internal module
- Re-create util module
- Add Unix Domain Socket Clock server & client for backtest
- Move exchange.StreamClient to monitor.StreamClient

## 0.1.5

Released 2025-05-02

- Add monitor's name, again
- Add `start_delay_seconds` in StreamMonitor
- Add CronMonitor
- Wrap Strategy and Monitors by global error handler
- Define QueueMsg type and dedup them
- Give state to Strategy as its member
- Delete `source_class` from Data descriptor
- Flush queue before Strategy starts
- Add an argument `current_data` for `source_to_data` function

## 0.1.4

Released 2025-04-15

- Fix signal handling
- Update Monitor IF
- Improve log readability
- Use cancel method instead of stop event

## 0.1.3

Released 2025-04-11

- Command Line Tool

## 0.1.2

Released 2025-04-10

- Make Srategy, State and Monitors optional
- Enhance PyPI project details
- E2E Test

## 0.1.1

Released 2025-04-05

- Set up CI using GitHub Actions:
  - Run tests
  - Publish to PyPI

## 0.1.0

Released 2025-04-02

- Core Components (Kernel, Data descriptor, State)
- REST API
- StreamMonitor
- Prices, Clock models
- Backtest Exchange for clock handling
- Example usage code
- Project Settings (tox, mypy, ruff)
