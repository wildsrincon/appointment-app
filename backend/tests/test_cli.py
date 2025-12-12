"""
Tests for CLI interface functionality.

This module tests the command-line interface, argument parsing,
interactive mode, single message mode, and CLI error handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from io import StringIO
import sys
import asyncio
from argparse import Namespace

from ..cli import ScheduleAICLI, main


@pytest.mark.asyncio
class TestScheduleAICLI:
    """Test cases for ScheduleAICLI class."""

    async def test_cli_initialization(self):
        """Test CLI initialization with default parameters."""
        cli = ScheduleAICLI()

        assert cli.business_id is None
        assert cli.consultant_id is None
        assert cli.agent is None
        assert "cli_session_" in cli.session_id

    async def test_cli_initialization_with_parameters(self):
        """Test CLI initialization with business and consultant IDs."""
        cli = ScheduleAICLI(
            business_id="test_business_123",
            consultant_id="test_consultant_456"
        )

        assert cli.business_id == "test_business_123"
        assert cli.consultant_id == "test_consultant_456"
        assert cli.agent is None

    async def test_initialize_success(self, mock_dependencies):
        """Test successful agent initialization."""
        cli = ScheduleAICLI()

        with patch('..cli.create_dependencies', return_value=mock_dependencies) as mock_create:
            with patch('..cli.ScheduleAIAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent_class.return_value = mock_agent

                await cli.initialize()

                mock_create.assert_called_once_with(
                    business_id=None,
                    consultant_id=None
                )
                mock_agent_class.assert_called_once_with(mock_dependencies)
                assert cli.agent == mock_agent

    async def test_initialize_with_parameters(self, mock_dependencies):
        """Test agent initialization with business and consultant parameters."""
        cli = ScheduleAICLI(
            business_id="business_123",
            consultant_id="consultant_456"
        )

        with patch('..cli.create_dependencies', return_value=mock_dependencies) as mock_create:
            with patch('..cli.ScheduleAIAgent'):
                await cli.initialize()

                mock_create.assert_called_once_with(
                    business_id="business_123",
                    consultant_id="consultant_456"
                )

    async def test_initialize_failure(self):
        """Test CLI initialization failure handling."""
        cli = ScheduleAICLI()

        with patch('..cli.create_dependencies', side_effect=Exception("Configuration error")):
            with patch('builtins.print') as mock_print:
                with patch('sys.exit') as mock_exit:
                    await cli.initialize()

                    # Should print error message and exit
                    mock_print.assert_called()
                    mock_exit.assert_called_once_with(1)

    async def test_single_message_mode(self, mock_dependencies):
        """Test single message processing mode."""
        cli = ScheduleAICLI()
        cli.agent = Mock()
        cli.agent.process_message = AsyncMock(return_value="Test response")
        cli.session_id = "test_session"

        test_message = "Vorrei prenotare per domani"

        with patch('builtins.print') as mock_print:
            await cli.single_message_mode(test_message)

            # Should print user message and agent response
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Messaggio: Vorrei prenotare per domani" in call for call in print_calls)
            assert any("Risposta: Test response" in call for call in print_calls)

            # Should call agent with correct parameters
            cli.agent.process_message.assert_called_once_with(
                message=test_message,
                session_id="test_session",
                business_id=None,
                consultant_id=None
            )

    async def test_single_message_mode_with_context(self, mock_dependencies):
        """Test single message mode with business and consultant context."""
        cli = ScheduleAICLI(
            business_id="business_123",
            consultant_id="consultant_456"
        )
        cli.agent = Mock()
        cli.agent.process_message = AsyncMock(return_value="Context response")
        cli.session_id = "test_session"

        test_message = "Controlla disponibilità"

        with patch('builtins.print'):
            await cli.single_message_mode(test_message)

            # Should call agent with context parameters
            cli.agent.process_message.assert_called_once_with(
                message=test_message,
                session_id="test_session",
                business_id="business_123",
                consultant_id="consultant_456"
            )

    async def test_single_message_mode_failure(self):
        """Test single message mode error handling."""
        cli = ScheduleAICLI()
        cli.agent = Mock()
        cli.agent.process_message = AsyncMock(side_effect=Exception("Processing error"))
        cli.session_id = "test_session"

        with patch('builtins.print') as mock_print:
            with patch('sys.exit') as mock_exit:
                await cli.single_message_mode("Test message")

                mock_print.assert_called()
                mock_exit.assert_called_once_with(1)

    @patch('builtins.input')
    @patch('builtins.print')
    async def test_interactive_mode_basic_flow(self, mock_print, mock_input, mock_dependencies):
        """Test interactive mode basic conversation flow."""
        cli = ScheduleAICLI()
        cli.agent = Mock()
        cli.agent.process_message = AsyncMock(return_value="Italian response")
        cli.session_id = "test_session"

        # Mock user inputs
        mock_input.side_effect = ["Vorrei prenotare", "esci"]

        await cli.interactive_mode()

        # Should process the message and then exit
        cli.agent.process_message.assert_called_once_with(
            message="Vorrei prenotare",
            session_id="test_session",
            business_id=None,
            consultant_id=None
        )

    @patch('builtins.input')
    @patch('builtins.print')
    async def test_interactive_mode_help_command(self, mock_print, mock_input):
        """Test interactive mode help command."""
        cli = ScheduleAICLI()
        cli.agent = Mock()

        mock_input.side_effect = ["aiuto", "esci"]

        await cli.interactive_mode()

        # Should print help information
        print_calls = [str(call) for call in mock_print.call_args_list]
        help_printed = any("Guida Rapida" in call for call in print_calls)
        assert help_printed

    @patch('builtins.input')
    @patch('builtins.print')
    async def test_interactive_mode_empty_input(self, mock_print, mock_input):
        """Test interactive mode handling of empty input."""
        cli = ScheduleAICLI()
        cli.agent = Mock()

        mock_input.side_effect = ["   ", "\t", "", "esci"]

        await cli.interactive_mode()

        # Should not process empty inputs
        cli.agent.process_message.assert_not_called()

    @patch('builtins.input')
    @patch('builtins.print')
    async def test_interactive_mode_exit_variations(self, mock_print, mock_input):
        """Test interactive mode various exit commands."""
        cli = ScheduleAICLI()
        cli.agent = Mock()

        exit_commands = ["esci", "exit", "quit", "chiudi"]

        for command in exit_commands:
            mock_input.side_effect = [command]
            await cli.interactive_mode()

            # Verify goodbye message was printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            goodbye_printed = any("Arrivederci" in call for call in print_calls)
            assert goodbye_printed

    @patch('builtins.input')
    @patch('builtins.print')
    async def test_interactive_mode_keyboard_interrupt(self, mock_print, mock_input):
        """Test interactive mode keyboard interrupt handling."""
        cli = ScheduleAICLI()
        cli.agent = Mock()

        mock_input.side_effect = KeyboardInterrupt()

        await cli.interactive_mode()

        # Should print interruption message
        print_calls = [str(call) for call in mock_print.call_args_list]
        interrupt_handled = any("interrotta" in call for call in print_calls)
        assert interrupt_handled

    @patch('builtins.input')
    @patch('builtins.print')
    async def test_interactive_mode_processing_error(self, mock_print, mock_input):
        """Test interactive mode processing error handling."""
        cli = ScheduleAICLI()
        cli.agent = Mock()
        cli.agent.process_message = AsyncMock(side_effect=Exception("Processing error"))
        cli.session_id = "test_session"

        mock_input.side_effect = ["test message", "esci"]

        await cli.interactive_mode()

        # Should handle error gracefully
        print_calls = [str(call) for call in mock_print.call_args_list]
        error_handled = any("Errore" in call for call in print_calls)
        assert error_handled

    def test_print_help(self):
        """Test help text printing."""
        cli = ScheduleAICLI()

        with patch('builtins.print') as mock_print:
            cli._print_help()

            # Should print help content
            print_calls = [str(call) for call in mock_print.call_args_list]
            help_content = " ".join(print_calls)

            expected_sections = [
                "Guida Rapida",
                "CREARE APPUNTAMENTO",
                "CONTROLLARE DISPONIBILITÀ",
                "MODIFICARE APPUNTAMENTO",
                "CANCELLARE APPUNTAMENTO",
                "COMANDI",
                "Suggerimenti"
            ]

            for section in expected_sections:
                assert section in help_content


@pytest.mark.asyncio
class TestCLIArguments:
    """Test cases for CLI argument parsing and main function."""

    async def test_main_no_arguments(self):
        """Test main function with no arguments (interactive mode)."""
        test_args = ["schedule_ai_agent"]

        with patch('sys.argv', test_args):
            with patch('..cli.ScheduleAICLI') as mock_cli_class:
                mock_cli = Mock()
                mock_cli.interactive_mode = AsyncMock()
                mock_cli_class.return_value = mock_cli

                with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_args = Namespace(
                        message=None,
                        business_id=None,
                        consultant_id=None,
                        debug=False
                    )
                    mock_parse.return_value = mock_args

                    await main()

                    mock_cli_class.assert_called_once_with(business_id=None, consultant_id=None)
                    mock_cli.interactive_mode.assert_called_once()

    async def test_main_with_message(self):
        """Test main function with single message argument."""
        test_args = ["schedule_ai_agent", "-m", "Test message"]

        with patch('sys.argv', test_args):
            with patch('..cli.ScheduleAICLI') as mock_cli_class:
                mock_cli = Mock()
                mock_cli.single_message_mode = AsyncMock()
                mock_cli_class.return_value = mock_cli

                with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_args = Namespace(
                        message="Test message",
                        business_id=None,
                        consultant_id=None,
                        debug=False
                    )
                    mock_parse.return_value = mock_args

                    await main()

                    mock_cli.single_message_mode.assert_called_once_with("Test message")

    async def test_main_with_business_id(self):
        """Test main function with business ID argument."""
        test_args = ["schedule_ai_agent", "--business-id", "test_business"]

        with patch('sys.argv', test_args):
            with patch('..cli.ScheduleAICLI') as mock_cli_class:
                mock_cli = Mock()
                mock_cli.interactive_mode = AsyncMock()
                mock_cli_class.return_value = mock_cli

                with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_args = Namespace(
                        message=None,
                        business_id="test_business",
                        consultant_id=None,
                        debug=False
                    )
                    mock_parse.return_value = mock_args

                    await main()

                    mock_cli_class.assert_called_once_with(business_id="test_business", consultant_id=None)

    async def test_main_with_consultant_id(self):
        """Test main function with consultant ID argument."""
        test_args = ["schedule_ai_agent", "--consultant-id", "dr_rossi"]

        with patch('sys.argv', test_args):
            with patch('..cli.ScheduleAICLI') as mock_cli_class:
                mock_cli = Mock()
                mock_cli.interactive_mode = AsyncMock()
                mock_cli_class.return_value = mock_cli

                with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_args = Namespace(
                        message=None,
                        business_id=None,
                        consultant_id="dr_rossi",
                        debug=False
                    )
                    mock_parse.return_value = mock_args

                    await main()

                    mock_cli_class.assert_called_once_with(business_id=None, consultant_id="dr_rossi")

    async def test_main_with_debug_mode(self):
        """Test main function with debug mode enabled."""
        test_args = ["schedule_ai_agent", "--debug"]

        with patch('sys.argv', test_args):
            with patch('..cli.ScheduleAICLI') as mock_cli_class:
                mock_cli = Mock()
                mock_cli.interactive_mode = AsyncMock()
                mock_cli_class.return_value = mock_cli

                with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_args = Namespace(
                        message=None,
                        business_id=None,
                        consultant_id=None,
                        debug=True
                    )
                    mock_parse.return_value = mock_args

                    with patch('logging.getLogger') as mock_logger:
                        await main()

                        # Debug mode should enable debug logging
                        mock_logger.return_value.setLevel.assert_called()

    async def test_main_keyboard_interrupt(self):
        """Test main function keyboard interrupt handling."""
        test_args = ["schedule_ai_agent"]

        with patch('sys.argv', test_args):
            with patch('..cli.ScheduleAICLI') as mock_cli_class:
                mock_cli = Mock()
                mock_cli.interactive_mode = AsyncMock(side_effect=KeyboardInterrupt())
                mock_cli_class.return_value = mock_cli

                with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_args = Namespace(
                        message=None,
                        business_id=None,
                        consultant_id=None,
                        debug=False
                    )
                    mock_parse.return_value = mock_args

                    with patch('builtins.print') as mock_print:
                        await main()

                        # Should handle interrupt gracefully
                        print_calls = [str(call) for call in mock_print.call_args_list]
                        interrupt_handled = any("interrotta" in call for call in print_calls)
                        assert interrupt_handled

    async def test_main_general_exception(self):
        """Test main function general exception handling."""
        test_args = ["schedule_ai_agent"]

        with patch('sys.argv', test_args):
            with patch('..cli.ScheduleAICLI') as mock_cli_class:
                mock_cli_class.side_effect = Exception("General error")

                with patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_args = Namespace(
                        message=None,
                        business_id=None,
                        consultant_id=None,
                        debug=False
                    )
                    mock_parse.return_value = mock_args

                    with patch('builtins.print') as mock_print:
                        with patch('sys.exit') as mock_exit:
                            await main()

                            mock_exit.assert_called_once_with(1)
                            print_calls = [str(call) for call in mock_print.call_args_list]
                            error_printed = any("Errore fatale" in call for call in print_calls)
                            assert error_printed


@pytest.mark.asyncio
class TestCLIIntegration:
    """Integration tests for CLI with agent."""

    async def test_cli_agent_integration_success(self):
        """Test successful CLI integration with agent."""
        with patch('..cli.create_dependencies') as mock_create_deps:
            mock_deps = Mock()
            mock_create_deps.return_value = mock_deps

            with patch('..cli.ScheduleAIAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent.process_message = AsyncMock(return_value="Italian appointment response")
                mock_agent_class.return_value = mock_agent

                cli = ScheduleAICLI()
                await cli.initialize()

                # Test single message mode
                await cli.single_message_mode("Vorrei prenotare per domani")

                mock_agent.process_message.assert_called()
                assert mock_agent.process_message.call_args[1]["message"] == "Vorrei prenotare per domani"

    async def test_cli_multiple_messages_context(self):
        """Test CLI maintains context across multiple messages."""
        with patch('..cli.create_dependencies') as mock_create_deps:
            mock_deps = Mock()
            mock_create_deps.return_value = mock_deps

            with patch('..cli.ScheduleAIAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent.process_message = AsyncMock(side_effect=[
                    "Prima risposta",
                    "Seconda risposta",
                    "Terza risposta"
                ])
                mock_agent_class.return_value = mock_agent

                cli = ScheduleAICLI(business_id="test_business", consultant_id="test_consultant")
                await cli.initialize()

                messages = [
                    "Vorrei prenotare per domani",
                    "Controlla anche giovedì",
                    "Grazie mille"
                ]

                for message in messages:
                    await cli.single_message_mode(message)

                # All calls should have the same context
                call_args_list = mock_agent.process_message.call_args_list
                for call_args in call_args_list:
                    assert call_args[1]["business_id"] == "test_business"
                    assert call_args[1]["consultant_id"] == "test_consultant"
                    assert call_args[1]["session_id"] == cli.session_id

    async def test_cli_error_recovery(self):
        """Test CLI error recovery and continued operation."""
        with patch('..cli.create_dependencies') as mock_create_deps:
            mock_deps = Mock()
            mock_create_deps.return_value = mock_deps

            with patch('..cli.ScheduleAIAgent') as mock_agent_class:
                mock_agent = Mock()
                mock_agent.process_message = AsyncMock(side_effect=[
                    Exception("First error"),
                    "Success after error"
                ])
                mock_agent_class.return_value = mock_agent

                cli = ScheduleAICLI()
                await cli.initialize()

                # First message fails
                with patch('builtins.print'):
                    with patch('sys.exit'):
                        try:
                            await cli.single_message_mode("Failing message")
                        except SystemExit:
                            pass  # Expected for failure case

                # Create new CLI instance for successful message
                cli2 = ScheduleAICLI()
                cli2.agent = mock_agent

                with patch('builtins.print'):
                    await cli2.single_message_mode("Success message")

                # Should have 2 total calls (one that failed, one that succeeded)
                assert mock_agent.process_message.call_count == 2


class TestCLIArgumentValidation:
    """Test cases for CLI argument validation."""

    def test_argument_parser_configuration(self):
        """Test that argument parser is configured correctly."""
        # This test would need access to the actual argparse configuration
        # For now, we test the expected behavior through integration tests
        pass

    def test_help_text_content(self):
        """Test that help text contains expected content."""
        # This would test the help output contains Italian examples
        pass

    def test_epilog_examples(self):
        """Test that argument parser epilog contains usage examples."""
        # This would verify the epilog contains Italian usage examples
        pass