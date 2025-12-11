"""
Tests for Italian NLP parsing and date/time handling.

This module tests the Italian language processing capabilities including
date/time parsing, service type extraction, and natural language understanding.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from ..tools import (
    parse_italian_datetime,
    extract_service_type,
    italian_appointment_parser
)


class TestItalianDatetimeParsing:
    """Test cases for Italian date/time parsing functionality."""

    def test_parse_relative_days(self, italian_datetime_test_cases):
        """Test parsing of relative day expressions."""
        reference_date = "2025-01-20T10:00:00"  # Monday

        for test_case in italian_datetime_test_cases:
            input_text, expected_date, expected_time, expected_confidence = test_case

            result = parse_italian_datetime(
                text=input_text,
                reference_date=reference_date,
                timezone="Europe/Rome"
            )

            assert result["success"] is True
            assert result["date"] == expected_date
            assert result["time"] == expected_time
            assert result["timezone"] == "Europe/Rome"
            assert isinstance(result["confidence"], float)
            assert result["confidence"] >= 0.5

    def test_parse_today_expressions(self):
        """Test parsing of 'oggi' (today) expressions."""
        today = datetime.now()
        test_cases = [
            "oggi alle 14:30",
            "oggi pomeriggio",
            "oggi mattina",
            "oggi ore 10:00"
        ]

        for text in test_cases:
            result = parse_italian_datetime(text=text)

            assert result["success"] is True
            parsed_date = datetime.fromisoformat(result["datetime"]).date()
            assert parsed_date == today.date()

    def test_parse_tomorrow_expressions(self):
        """Test parsing of 'domani' (tomorrow) expressions."""
        tomorrow = datetime.now() + timedelta(days=1)
        test_cases = [
            "domani alle 14:30",
            "domani mattina",
            "domani pomeriggio",
            "domani ore 16:00"
        ]

        for text in test_cases:
            result = parse_italian_datetime(text=text)

            assert result["success"] is True
            parsed_date = datetime.fromisoformat(result["datetime"]).date()
            assert parsed_date == tomorrow.date()

    def test_parse_day_of_week(self):
        """Test parsing of specific day of week expressions."""
        today = datetime.now()

        # Test each day of the week
        day_tests = [
            ("lunedì", 0),      # Monday
            ("martedì", 1),     # Tuesday
            ("mercoledì", 2),   # Wednesday
            ("giovedì", 3),     # Thursday
            ("venerdì", 4),     # Friday
            ("sabato", 5),      # Saturday
            ("domenica", 6),    # Sunday
        ]

        for day_name, target_weekday in day_tests:
            result = parse_italian_datetime(text=f"{day_name} alle 10:00")

            assert result["success"] is True
            parsed_date = datetime.fromisoformat(result["datetime"])
            # Should find the next occurrence of that day
            assert parsed_date.weekday() == target_weekday

    def test_parse_next_week_expressions(self):
        """Test parsing of 'next week' expressions."""
        reference_date = "2025-01-20T10:00:00"  # Monday

        next_week_tests = [
            ("lunedì prossimo", "2025-01-27"),
            ("martedì prossimo", "2025-01-28"),
            ("giovedì prossimo", "2025-01-30"),
            ("venerdì prossimo", "2025-01-31"),
        ]

        for text, expected_date in next_week_tests:
            result = parse_italian_datetime(
                text=text,
                reference_date=reference_date
            )

            assert result["success"] is True
            assert result["date"] == expected_date

    def test_parse_time_patterns(self):
        """Test various time pattern parsing."""
        time_tests = [
            ("alle 14:30", "14:30"),
            ("alle 9:00", "09:00"),
            ("ore 15:00", "15:00"),
            ("16:45", "16:45"),
            ("alle 8:05", "08:05"),
        ]

        for text, expected_time in time_tests:
            # Add a day reference to make parsing easier
            full_text = f"domani {text}"
            result = parse_italian_datetime(text=full_text)

            assert result["success"] is True
            assert result["time"] == expected_time

    def test_parse_time_period_expressions(self):
        """Test parsing of time period expressions (morning, afternoon, evening)."""
        period_tests = [
            ("domani mattina", "09:00"),
            ("domani pomeriggio", "15:00"),
            ("domani sera", "18:00"),
            ("oggi mattina", "09:00"),
            ("oggi pomeriggio", "15:00"),
        ]

        for text, expected_time in period_tests:
            result = parse_italian_datetime(text=text)

            assert result["success"] is True
            assert result["time"] == expected_time

    def test_parse_datetime_failure_cases(self):
        """Test parsing failure cases."""
        failure_cases = [
            "xyz123 invalid date",
            "il trentadue febbraio",
            "alle venticinque e settanta",
            "",
            "                       ",  # Only whitespace
        ]

        for text in failure_cases:
            result = parse_italian_datetime(text=text)

            # Should handle gracefully, either with default values or marked as failed
            assert isinstance(result, dict)
            assert "success" in result

    def test_parse_datetime_edge_cases(self):
        """Test edge cases in datetime parsing."""
        # Test with reference date in the past
        past_date = "2024-01-01T10:00:00"
        result = parse_italian_datetime(
            text="domani alle 14:00",
            reference_date=past_date
        )
        assert result["success"] is True

        # Test with different timezone
        result = parse_italian_datetime(
            text="oggi alle 10:00",
            timezone="Europe/Milan"
        )
        assert result["success"] is True
        assert result["timezone"] == "Europe/Milan"


class TestServiceTypeExtraction:
    """Test cases for service type extraction from Italian text."""

    def test_extract_service_types(self, italian_service_test_cases):
        """Test extraction of various service types."""
        for text, expected_service, expected_duration in italian_service_test_cases:
            service_type, duration = extract_service_type(text)

            assert service_type == expected_service
            assert duration == expected_duration

    def test_extract_consultation_types(self):
        """Test extraction of consultation-related services."""
        consultation_tests = [
            ("consulenza", "consulenza", 60),
            ("consulenza fiscale", "consulenza_fiscale", 90),
            ("consulenza legale", "consulenza_legale", 90),
            ("una consulenza approfondita", "consulenza", 60),  # Should match base pattern
        ]

        for text, expected_service, expected_duration in consultation_tests:
            service_type, duration = extract_service_type(text)
            assert service_type == expected_service
            assert duration == expected_duration

    def test_extract_meeting_types(self):
        """Test extraction of meeting-related services."""
        meeting_tests = [
            ("riunione", "riunione", 60),
            ("incontro", "incontro", 45),
            ("colloquio", "colloquio", 30),
            ("intervista", "intervista", 45),
        ]

        for text, expected_service, expected_duration in meeting_tests:
            service_type, duration = extract_service_type(text)
            assert service_type == expected_service
            assert duration == expected_duration

    def test_extract_duration_override(self):
        """Test duration extraction overrides default service duration."""
        duration_tests = [
            ("riunione di 90 minuti", "riunione", 90),
            ("colloquio di un'ora", "colloquio", 60),
            ("appunto di mezz'ora", "appunto", 30),
            ("incontro di due ore", "incontro", 120),
            ("consulenza di un'ora e mezza", "consulenza", 90),
            ("seduta di 15 minuti", "seduta", 15),
        ]

        for text, expected_service, expected_duration in duration_tests:
            service_type, duration = extract_service_type(text)
            assert service_type == expected_service
            assert duration == expected_duration

    def test_extract_unknown_service(self):
        """Test handling of unknown service types."""
        unknown_tests = [
            "servizio non conosciuto",
            "xyz123",
            "",
            "qualsiasi cosa",
        ]

        for text in unknown_tests:
            service_type, duration = extract_service_type(text)
            assert service_type == "generale"  # Should default to 'generale'
            assert duration == 30  # Should default to 30 minutes

    def test_extract_case_insensitive(self):
        """Test case-insensitive service extraction."""
        mixed_case_tests = [
            ("Consulenza Fiscale", "consulenza_fiscale", 90),
            ("RIUNIONE", "riunione", 60),
            ("Colloquio", "colloquio", 30),
            ("APPUNTO", "appunto", 30),
        ]

        for text, expected_service, expected_duration in mixed_case_tests:
            service_type, duration = extract_service_type(text)
            assert service_type == expected_service
            assert duration == expected_duration


@pytest.mark.asyncio
class TestItalianAppointmentParser:
    """Test cases for the integrated Italian appointment parser tool."""

    async def test_appointment_parser_basic(self):
        """Test basic appointment parsing functionality."""
        text = "Vorrei prenotare una consulenza per domani alle 14:30"

        result = italian_appointment_parser(text=text)

        assert result["success"] is True
        assert "datetime" in result
        assert "date" in result
        assert "time" in result
        assert "service_type" in result
        assert "duration_minutes" in result
        assert result["service_type"] == "consulenza"
        assert result["duration_minutes"] == 60

    async def test_appointment_parser_with_context(self):
        """Test appointment parsing with reference date context."""
        text = "Vorrei un appuntamento domani mattina"
        context_date = "2025-01-20T10:00:00"  # Monday

        result = italian_appointment_parser(
            text=text,
            context_date=context_date
        )

        assert result["success"] is True
        assert result["date"] == "2025-01-21"  # Tuesday
        assert result["time"] == "09:00"  # Morning default

    async def test_appointment_parser_complex_request(self):
        """Test parsing of complex appointment requests."""
        text = "Vorrei prenotare una consulenza fiscale di 90 minuti per giovedì prossimo alle 15:00"

        result = italian_appointment_parser(text=text)

        assert result["success"] is True
        assert result["service_type"] == "consulenza_fiscale"
        assert result["duration_minutes"] == 90
        assert result["time"] == "15:00"

    async def test_appointment_parser_failure(self):
        """Test appointment parser failure handling."""
        text = "xyz123 invalid request"

        result = italian_appointment_parser(text=text)

        # Should handle gracefully
        assert isinstance(result, dict)
        assert "success" in result

    async def test_appointment_parser_with_service_only(self):
        """Test parser with service type but no datetime."""
        text = "Vorrei una consulenza legale"

        result = italian_appointment_parser(text=text)

        assert result["success"] is True
        assert result["service_type"] == "consulenza_legale"
        assert result["duration_minutes"] == 90
        # Should have default datetime values

    async def test_appointment_parser_with_datetime_only(self):
        """Test parser with datetime but no service type."""
        text = "Vorrei prenotare per domani alle 10:00"

        result = italian_appointment_parser(text=text)

        assert result["success"] is True
        assert "datetime" in result
        assert result["service_type"] == "generale"  # Default service
        assert result["duration_minutes"] == 30  # Default duration


class TestItalianLanguagePatterns:
    """Test cases for Italian language patterns and politeness."""

    def test_polite_expressions_recognition(self):
        """Test recognition of polite Italian expressions."""
        polite_tests = [
            "Vorrei prenotare un appuntamento",
            "Mi piacerebbe fissare un incontro",
            "Per favore, controlla la disponibilità",
            "Grazie mille per l'aiuto",
            "Scusi, vorrei chiedere",
        ]

        for text in polite_tests:
            # These should not cause errors in parsing
            try:
                # Try to parse as datetime (may fail, but shouldn't crash)
                result = parse_italian_datetime(text)
                assert isinstance(result, dict)

                # Try to extract service type
                service_type, duration = extract_service_type(text)
                assert isinstance(service_type, str)
                assert isinstance(duration, int)

            except Exception as e:
                pytest.fail(f"Polite expression parsing failed: {text}, error: {e}")

    def test_business_italian_expressions(self):
        """Test business Italian expressions."""
        business_tests = [
            "fissare una consulenza",
            "prenotare un appuntamento",
            "verificare la disponibilità",
            "spostare l'incontro",
            "cancellare la riunione",
        ]

        for text in business_tests:
            try:
                service_type, duration = extract_service_type(text)
                assert isinstance(service_type, str)
                assert isinstance(duration, int)
            except Exception as e:
                pytest.fail(f"Business expression parsing failed: {text}, error: {e}")

    def test_italian_number_words(self):
        """Test handling of Italian number words if implemented."""
        # This test checks if the parser can handle Italian number words
        # Implementation may be basic for MVP
        number_tests = [
            "un'ora",  # one hour
            "mezz'ora",  # half hour
            "due ore",  # two hours
        ]

        for text in number_tests:
            service_type, duration = extract_service_type(f"appunto di {text}")
            assert isinstance(duration, int)
            if "un'ora" in text:
                assert duration == 60
            elif "mezz'ora" in text:
                assert duration == 30
            elif "due ore" in text:
                assert duration == 120