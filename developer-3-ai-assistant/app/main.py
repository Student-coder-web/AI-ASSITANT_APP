"""CLI entrypoint for local testing."""

from __future__ import annotations

import sys

from app.assistant import Assistant
from app.config import get_settings


def main() -> None:
	settings = get_settings()
	assistant = Assistant(settings)

	pdf_path = input("Enter PDF path (or press Enter to skip): ").strip()
	if pdf_path.startswith("'") and pdf_path.endswith("'"):
		pdf_path = pdf_path[1:-1]
	if pdf_path.startswith('"') and pdf_path.endswith('"'):
		pdf_path = pdf_path[1:-1]
	if pdf_path and pdf_path.lower() != "skip":
		try:
			assistant.ingest_pdf(pdf_path)
		except FileNotFoundError as exc:
			print(f"Warning: {exc}. Skipping PDF ingestion.")

	print(f"{settings.app_name} (type 'exit' to quit)")

	while True:
		try:
			user_input = input("\nYou: ").strip()
		except (EOFError, KeyboardInterrupt):
			print("\nExiting...")
			return

		if not user_input:
			continue
		if user_input.lower() in {"exit", "quit"}:
			print("Goodbye!")
			return

		response = assistant.ask(user_input)
		print(f"\nAssistant: {response}")


if __name__ == "__main__":
	sys.exit(main())
