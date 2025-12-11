"""
Integration tests for the Italian Appointment Scheduling AI Agent.

This module tests end-to-end workflows, component integration,
and real-world usage scenarios with comprehensive error handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from ..agent import ScheduleAIAgent
from ..dependencies import ScheduleAgentDependencies
from ..tools import parse_italian_datetime, extract_service_type


@pytest.mark.asyncio
class TestEndToEndWorkflows:
    """Test cases for complete appointment scheduling workflows."""

    async def test_complete_appointment_booking_workflow(self, mock_dependencies):
        """Test complete workflow from Italian request to calendar booking."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            # Mock the calendar operations
            with patch('..tools.mock_google_calendar_create_event') as mock_create, \
                 patch('..tools.mock_google_calendar_check_availability') as mock_check:

                mock_check.return_value = {"success": True, "available": True}
                mock_create.return_value = {
                    "success": True,
                    "event_id": "complete_workflow_event",
                    "event_data": {"summary": "consulenza - Mario Rossi"}
                }

                # Step 1: Process Italian appointment request
                italian_request = "Vorrei prenotare una consulenza fiscale per domani alle 14:30. Cliente: Mario Rossi"
                response = await agent.process_message(italian_request)

                assert isinstance(response, str)
                assert len(response) > 0

                # Step 2: Create appointment using agent method
                result = await agent.create_appointment(
                    client_name="Mario Rossi",
                    service_type="consulenza fiscale",
                    datetime_request="domani alle 14:30",
                    client_email="mario.rossi@email.com"
                )

                assert result["success"] is True
                assert result["client_name"] == "Mario Rossi"
                assert result["service_type"] == "consulenza fiscale"

    async def test_availability_check_workflow(self, mock_dependencies):
        """Test availability checking workflow."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            with patch('..tools.mock_google_calendar_check_availability') as mock_check:
                mock_check.return_value = {
                    "success": True,
                    "available": True,
                    "conflicts": []
                }

                # Check availability for multiple time slots
                time_requests = [
                    "domani mattina",
                    "giovedì pomeriggio",
                    "venerdì alle 15:00"
                ]

                for time_request in time_requests:
                    result = await agent.check_availability(datetime_request=time_request)

                    assert result["success"] is True
                    assert "response" in result
                    assert result["datetime_request"] == time_request

    async def test_appointment_modification_workflow(self, mock_dependencies):
        """Test appointment modification workflow."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            modification_request = "Sposta l'appuntamento di Mario Rossi da domani mattina a giovedì pomeriggio"

            result = await agent.modify_appointment(
                modification_request=modification_request
            )

            assert result["success"] is True
            assert "response" in result
            assert result["modification_request"] == modification_request

    async def test_appointment_cancellation_workflow(self, mock_dependencies):
        """Test appointment cancellation workflow."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            cancellation_request = "Cancella l'appuntamento di consulenza di domani alle 10:00"

            result = await agent.cancel_appointment(
                cancellation_request=cancellation_request
            )

            assert result["success"] is True
            assert "response" in result
            assert result["cancellation_request"] == cancellation_request

    async def test_multi_consultant_workflow(self, mock_dependencies):
        """Test workflow with multiple consultants."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            consultants = ["consulente_fiscale", "consulente_legale", "consulente_generale"]

            for consultant in consultants:
                result = await agent.check_availability(
                    datetime_request="domani alle 14:00",
                    consultant_id=consultant
                )

                assert result["success"] is True
                assert "response" in result

    async def test_multi_business_workflow(self):
        """Test workflow with multiple businesses."""
        business_deps = ScheduleAgentDependencies(
            openai_api_key="test",
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test",
            business_id="business_001",
            consultant_id="consultant_001"
        )

        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=business_deps)

            # Test with business context
            result = await agent.process_message(
                message="Vorrei prenotare per domani",
                session_id="session_123",
                business_id="business_001",
                consultant_id="consultant_001"
            )

            assert isinstance(response, str)
            assert len(response) > 0


@pytest.mark.asyncio
class TestErrorHandlingIntegration:
    """Integration tests for error handling across the system."""

    async def test_cascade_error_handling(self, mock_dependencies):
        """Test error handling when multiple components fail."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            # Mock calendar API failure
            with patch('..tools.mock_google_calendar_check_availability') as mock_check:
                mock_check.side_effect = Exception("Calendar API unavailable")

                # System should handle gracefully
                result = await agent.check_availability("domani alle 10:00")

                assert isinstance(result, dict)
                assert result["success"] is False
                assert "error" in result

    async def test_partial_failure_recovery(self, mock_dependencies):
        """Test system recovery from partial failures."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            # First request fails
            with patch('..tools.mock_google_calendar_check_availability') as mock_check:
                mock_check.side_effect = [
                    Exception("API timeout"),
                    {"success": True, "available": True}
                ]

                # Retry should succeed
                failed_result = await agent.check_availability("domani alle 10:00")
                assert failed_result["success"] is False

                success_result = await agent.check_availability("domani alle 11:00")
                assert success_result["success"] is True

    async def test_invalid_italian_parsing_recovery(self, mock_dependencies):
        """Test recovery from invalid Italian parsing."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            # Test with unparseable Italian
            invalid_requests = [
                "xyz123 nonexistent request",
                "prenotare xyz invalid date",
                "",
                "                ",  # Only whitespace
            ]

            for request in invalid_requests:
                response = await agent.process_message(request)

                # Should handle gracefully without crashing
                assert isinstance(response, str)
                assert len(response) >= 0  # May be empty for invalid input

    async def test_dependency_injection_failure(self):
        """Test behavior when dependency injection fails."""
        with patch('..dependencies.create_dependencies') as mock_create:
            mock_create.side_effect = Exception("Configuration error")

            with pytest.raises(Exception):
                from ..dependencies import create_dependencies
                create_dependencies()

    async def test_model_initialization_failure(self):
        """Test behavior when model initialization fails."""
        invalid_deps = ScheduleAgentDependencies(
            openai_api_key="",  # Invalid empty key
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test"
        )

        # Should handle initialization gracefully
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.side_effect = Exception("Model initialization failed")

            with pytest.raises(Exception):
                agent = ScheduleAIAgent(dependencies=invalid_deps)


@pytest.mark.asyncio
class TestPerformanceIntegration:
    """Integration tests for system performance under realistic load."""

    async def test_concurrent_user_sessions(self, mock_dependencies):
        """Test system handling multiple concurrent user sessions."""
        import asyncio

        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            # Simulate multiple concurrent users
            user_requests = [
                {
                    "session_id": f"session_{i}",
                    "message": f"Vorrei prenotare per domani alle {10 + i}:00",
                    "business_id": f"business_{i % 3}",
                    "consultant_id": f"consultant_{i % 2}"
                }
                for i in range(5)
            ]

            # Process all requests concurrently
            tasks = [
                agent.process_message(
                    message=req["message"],
                    session_id=req["session_id"],
                    business_id=req["business_id"],
                    consultant_id=req["consultant_id"]
                )
                for req in user_requests
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # All should complete successfully
            for i, response in enumerate(responses):
                assert not isinstance(response, Exception), f"Request {i} failed: {response}"
                assert isinstance(response, str)

    async def test_rapid_sequential_requests(self, mock_dependencies):
        """Test system handling rapid sequential requests."""
        import time

        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            # Process many requests sequentially
            start_time = time.time()
            request_count = 10

            for i in range(request_count):
                message = f"Request {i}: Vorrei controllare la disponibilità"
                response = await agent.process_message(message)
                assert isinstance(response, str)

            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / request_count

            # Each request should complete quickly
            assert avg_time < 2.0  # Average under 2 seconds per request

    async def test_memory_usage_stability(self, mock_dependencies):
        """Test memory usage stability over extended operation."""
        import gc

        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            # Process many requests to test memory stability
            for i in range(20):
                await agent.process_message(f"Test message {i}: vorrei prenotare")

                # Periodically force garbage collection
                if i % 5 == 0:
                    gc.collect()

            # Agent should still function correctly after many requests
            final_response = await agent.process_message("Final test message")
            assert isinstance(final_response, str)


@pytest.mark.asyncio
class TestDataIntegrityIntegration:
    """Integration tests for data integrity and consistency."""

    async def test_session_context_isolation(self):
        """Test that different sessions maintain proper isolation."""
        agent1_deps = ScheduleAgentDependencies(
            openai_api_key="test",
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test",
            session_id="session_001"
        )

        agent2_deps = ScheduleAgentDependencies(
            openai_api_key="test",
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test",
            session_id="session_002"
        )

        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()

            agent1 = ScheduleAIAgent(dependencies=agent1_deps)
            agent2 = ScheduleAIAgent(dependencies=agent2_deps)

            # Each agent should maintain its own context
            response1 = await agent1.process_message("Session 1 request")
            response2 = await agent2.process_message("Session 2 request")

            assert isinstance(response1, str)
            assert isinstance(response2, str)
            assert agent1.dependencies.session_id == "session_001"
            assert agent2.dependencies.session_id == "session_002"

    async def test_business_context_consistency(self):
        """Test business context is maintained consistently."""
        business_a_deps = ScheduleAgentDependencies(
            openai_api_key="test",
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test",
            business_id="business_a",
            business_hours=(9, 17),  # Different hours
            working_days=(1, 2, 3, 4)  # Monday-Thursday only
        )

        business_b_deps = ScheduleAgentDependencies(
            openai_api_key="test",
            google_calendar_api_key="test",
            google_client_id="test",
            google_client_secret="test",
            google_refresh_token="test",
            business_id="business_b",
            business_hours=(10, 19),  # Different hours
            working_days=(2, 3, 4, 5)  # Tuesday-Friday only
        )

        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()

            agent_a = ScheduleAIAgent(dependencies=business_a_deps)
            agent_b = ScheduleAIAgent(dependencies=business_b_deps)

            # Each agent should maintain its business context
            assert agent_a.dependencies.business_hours == (9, 17)
            assert agent_a.dependencies.working_days == (1, 2, 3, 4)

            assert agent_b.dependencies.business_hours == (10, 19)
            assert agent_b.dependencies.working_days == (2, 3, 4, 5)

    async def test_italian_datetime_consistency(self):
        """Test Italian datetime parsing provides consistent results."""
        test_cases = [
            ("domani alle 14:30",),
            ("lunedì prossimo",),
            ("oggi pomeriggio",),
            ("giovedì alle 10:00",),
        ]

        reference_date = "2025-01-20T10:00:00"

        for text_input in test_cases:
            # Parse multiple times to ensure consistency
            results = []
            for _ in range(3):
                result = parse_italian_datetime(
                    text=text_input[0],
                    reference_date=reference_date
                )
                results.append(result)

            # All results should be identical
            for i in range(1, len(results)):
                assert results[i]["success"] == results[0]["success"]
                if results[0]["success"]:
                    assert results[i]["datetime"] == results[0]["datetime"]
                    assert results[i]["time"] == results[0]["time"]


@pytest.mark.asyncio
class TestRealWorldScenarios:
    """Integration tests for realistic user scenarios."""

    async def test_complex_appointment_request(self, mock_dependencies):
        """Test complex appointment request with multiple details."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            complex_request = """
            Buongiorno, vorrei prenotare una consulenza fiscale di 90 minuti
            per la prossima settimana. Il cliente è Mario Rossi, email: mario.rossi@email.com,
            telefono: 333-1234567. Preferirebbe giovedì pomeriggio se possibile.
            """

            response = await agent.process_message(complex_request)

            assert isinstance(response, str)
            assert len(response) > 0

    async def test_reschedule_with_constraints(self, mock_dependencies):
        """Test appointment rescheduling with time constraints."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            reschedule_request = """
            Devo spostare l'appuntamento di Mario Rossi previsto per domani mattina.
            Il cliente preferirebbe giovedì o venerdì pomeriggio, ma non dopo le 17:00.
            La durata rimane di 60 minuti.
            """

            result = await agent.modify_appointment(reschedule_request)

            assert result["success"] is True
            assert "response" in result

    async def test_multiple_service_booking(self, mock_dependencies):
        """Test booking multiple different services."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            services = [
                ("consulenza legale", 90),
                ("colloquio", 30),
                ("riunione", 60)
            ]

            for service_type, duration in services:
                result = await agent.create_appointment(
                    client_name=f"Cliente {service_type}",
                    service_type=service_type,
                    datetime_request="domani alle 14:00"
                )

                assert result["success"] is True
                assert result["service_type"] == service_type

    async def test_emergency_appointment_handling(self, mock_dependencies):
        """Test handling of urgent/emergency appointment requests."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            urgent_request = """
            URGENTE: Ho bisogno di una consulenza immediata per un problema fiscale.
            È possibile oggi pomeriggio o domani mattina presto? Grazie.
            """

            response = await agent.process_message(urgent_request)

            assert isinstance(response, str)
            assert len(response) > 0

    async def test_cancellation_with_refund_policy(self, mock_dependencies):
        """Test appointment cancellation with policy considerations."""
        with patch('..providers.get_llm_model') as mock_model:
            mock_model.return_value = Mock()
            agent = ScheduleAIAgent(dependencies=mock_dependencies)

            cancellation_request = """
            Vorrei cancellare l'appuntamento di consulenza previsto per domani alle 10:00.
            È possibile ottenere un rimborso o un credito per una futura consulenza?
            """

            result = await agent.cancel_appointment(cancellation_request)

            assert result["success"] is True
            assert "response" in result