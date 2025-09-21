"""Tests for the logging module."""

from __future__ import annotations


from traffic_sim.core.logging import Event, EventLogger


class TestEvent:
    """Test the Event dataclass."""

    def test_event_creation(self) -> None:
        """Test creating an event with all fields."""
        event = Event(time_s=1.5, type="collision", vehicle_ids=[1, 2], info={"severity": "high"})

        assert event.time_s == 1.5
        assert event.type == "collision"
        assert event.vehicle_ids == [1, 2]
        assert event.info == {"severity": "high"}


class TestEventLogger:
    """Test the EventLogger class."""

    def test_logger_initialization(self) -> None:
        """Test that logger starts with empty events list."""
        logger = EventLogger()
        assert logger.events == []

    def test_log_event(self) -> None:
        """Test logging an event."""
        logger = EventLogger()
        event = Event(time_s=2.0, type="lane_change", vehicle_ids=[3], info={"lane": "left"})

        logger.log(event)

        assert len(logger.events) == 1
        assert logger.events[0] == event

    def test_log_multiple_events(self) -> None:
        """Test logging multiple events."""
        logger = EventLogger()

        event1 = Event(1.0, "start", [1], {})
        event2 = Event(2.0, "end", [1], {})

        logger.log(event1)
        logger.log(event2)

        assert len(logger.events) == 2
        assert logger.events[0] == event1
        assert logger.events[1] == event2
