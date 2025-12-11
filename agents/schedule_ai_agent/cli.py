"""
Command Line Interface for Italian Appointment Scheduling AI Agent.

This module provides a CLI for interacting with the appointment scheduling agent
through natural Italian language conversations.
"""

import asyncio
import argparse
import sys
from typing import Optional

# Handle both relative and absolute imports
try:
    from .agent import get_agent, ScheduleAIAgent
    from .dependencies import create_dependencies
except ImportError:
    # Running as script directly
    try:
        from agent import get_agent, ScheduleAIAgent
        from dependencies import create_dependencies
    except ImportError:
        # Try adding current directory to path
        import os
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from agent import get_agent, ScheduleAIAgent
        from dependencies import create_dependencies
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScheduleAICLI:
    """Command Line Interface for Schedule AI Agent."""

    def __init__(self, business_id: Optional[str] = None, consultant_id: Optional[str] = None):
        """
        Initialize the CLI.

        Args:
            business_id: Optional business identifier
            consultant_id: Optional consultant identifier
        """
        self.business_id = business_id
        self.consultant_id = consultant_id
        self.session_id = f"cli_session_{asyncio.get_event_loop().time()}"
        self.agent: Optional[ScheduleAIAgent] = None

    async def initialize(self):
        """Initialize the agent and dependencies."""
        try:
            dependencies = create_dependencies(
                business_id=self.business_id,
                consultant_id=self.consultant_id
            )
            self.agent = ScheduleAIAgent(dependencies)
            print("🤖 Assistente AI per Appuntamenti inizializzato con successo!")
            print("💬 Digita i tuoi messaggi in italiano. Digita 'esci' per terminare.")
            print("-" * 60)
        except Exception as e:
            print(f"❌ Errore durante l'inizializzazione: {e}")
            sys.exit(1)

    async def interactive_mode(self):
        """Run the agent in interactive mode."""
        if not self.agent:
            await self.initialize()

        print("\nCiao! Sono l'assistente virtuale per la gestione appuntamenti.")
        print("Come posso aiutarti oggi?")

        while True:
            try:
                # Get user input
                user_input = input("\n👤 Tu: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['esci', 'exit', 'quit', 'chiudi']:
                    print("\n👋 Arrivederci e buona giornata!")
                    break

                if user_input.lower() in ['aiuto', 'help', '?']:
                    self._print_help()
                    continue

                # Process the message
                print("\n🤖 Sto elaborando...")
                response = await self.agent.process_message(
                    message=user_input,
                    session_id=self.session_id,
                    business_id=self.business_id,
                    consultant_id=self.consultant_id
                )

                print(f"\n🤖 Assistente: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Sessione interrotta. Arrivederci!")
                break
            except Exception as e:
                print(f"\n❌ Errore: {e}")
                logger.error(f"CLI error: {e}")

    def _print_help(self):
        """Print help information."""
        help_text = """
📋 Guida Rapida:

🔸 CREARE APPUNTAMENTO:
   "Vorrei prenotare una consulenza per domani alle 14:30"
   "Prenota un appunto con il Dr. Rossi per giovedì prossimo"

🔸 CONTROLLARE DISPONIBILITÀ:
   "Ci sono posti liberi oggi pomeriggio?"
   "Sono disponibili orari per la prossima settimana?"

🔸 MODIFICARE APPUNTAMENTO:
   "Vorrei spostare il mio appuntamento di domani alle 15"
   "Posso cambiare l'orario della consulenza di giovedì?"

🔸 CANCELLARE APPUNTAMENTO:
   "Devo cancellare il mio appuntamento di venerdì"
   "Annulla la prenotazione per domani mattina"

🔸 COMANDI:
   'aiuto' - Mostra questa guida
   'esci' - Termina la sessione

💡 Suggerimenti:
- Sii specifico con date e orari
- Specifica il tipo di servizio richiesto
- Includi il nome del consulente se noto
        """
        print(help_text)

    async def single_message_mode(self, message: str):
        """Process a single message and exit."""
        if not self.agent:
            await self.initialize()

        try:
            print(f"👤 Messaggio: {message}")
            print("🤖 Sto elaborando...")

            response = await self.agent.process_message(
                message=message,
                session_id=self.session_id,
                business_id=self.business_id,
                consultant_id=self.consultant_id
            )

            print(f"\n🤖 Risposta: {response}")

        except Exception as e:
            print(f"\n❌ Errore: {e}")
            sys.exit(1)


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Assistente AI Italiano per Gestione Appuntamenti",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:
  python -m schedule_ai_agent                          # Modalità interattiva
  python -m schedule_ai_agent -m "Prenota per domani"  # Messaggio singolo
  python -m schedule_ai_agent --business-id "studio123" # Business specifico
  python -m schedule_ai_agent --consultant-id "dr_rossi" # Consulente specifico
        """
    )

    parser.add_argument(
        "-m", "--message",
        help="Messaggio singolo da processare (modalità non interattiva)"
    )

    parser.add_argument(
        "--business-id",
        help="ID del business per configurazione multi-tenant"
    )

    parser.add_argument(
        "--consultant-id",
        help="ID del consulente per filtri specifici"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Abilita modalità debug con logging dettagliato"
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Modalità debug abilitata")

    # Create CLI instance
    cli = ScheduleAICLI(
        business_id=args.business_id,
        consultant_id=args.consultant_id
    )

    try:
        if args.message:
            # Single message mode
            await cli.single_message_mode(args.message)
        else:
            # Interactive mode
            await cli.interactive_mode()

    except KeyboardInterrupt:
        print("\n👋 Sessione interrotta. Arrivederci!")
    except Exception as e:
        print(f"\n❌ Errore fatale: {e}")
        logger.error(f"Fatal CLI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())