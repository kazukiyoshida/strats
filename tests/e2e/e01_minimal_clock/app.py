from zoneinfo import ZoneInfo

from strats import Clock, Strats


def main():
    Strats(
        clock=Clock(
            start_at="2025-01-01 12:00:00",
            tz=ZoneInfo("Asia/Tokyo"),
            speed=2,
        ),
    ).serve()


if __name__ == "__main__":
    main()
