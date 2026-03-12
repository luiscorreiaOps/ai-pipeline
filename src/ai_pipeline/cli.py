import typer
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .scanner import scan_repo
from .detector import detect_stack
from .generator import generate_pipeline
from .config import config
from .providers import PROVIDERS_CONFIG, KNOWN_KEYS
from . import __version__
import ai_pipeline.providers as providers_mod

app = typer.Typer()
console = Console()

@app.command()
def debug():
    """Prints debug information about providers and environment."""
    console.print(f"CLI Version: {__version__}")
    console.print(f"Providers File: {providers_mod.__file__}")
    console.print(f"Known Keys in Code: {KNOWN_KEYS}")
    found = config.scan_environment()
    console.print(f"Keys found in Environment: {list(found.keys())}")

@app.command()
def version():
    """Prints the current version of ai-pipeline-tool."""
    console.print(f"[bold blue]ai-pipeline-tool[/bold blue] version: [green]{__version__}[/green]")

def select_from_found(found_dict: dict, message: str = "Choose an AI provider key:"):
    """Exibe uma lista numerada e permite seleção por número ou nome."""
    keys = list(found_dict.keys())

    if not keys:
        return None, None

    table = Table(title=message, show_header=True, header_style="bold magenta")
    table.add_column("No.", style="dim", width=4)
    table.add_column("Key Name", style="cyan")

    for i, key in enumerate(keys, 1):
        table.add_row(str(i), key)

    console.print(table)

    choice = Prompt.ask(f"Enter number (1-{len(keys)}) or the key name")

    # Tenta converter para num
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            return keys[idx], found_dict[keys[idx]]

    # pelo nome direto
    if choice in found_dict:
        return choice, found_dict[choice]

    console.print("[red]Invalid selection. Using the first one found.[/red]")
    return keys[0], found_dict[keys[0]]

def get_best_provider():
    """Identifies which AI keys are in the environment and chooses one."""
    if config.ai_api_key and config.ai_provider_key:
        return config.ai_provider_key, config.ai_api_key

    # Scan
    found = config.scan_environment()

    if len(found) == 0:
        return None, None
    elif len(found) == 1:
        key_name = list(found.keys())[0]
        return key_name, found[key_name]
    else:
        return select_from_found(found, "Multiple AI keys found in environment")

@app.command()
def generate():
    """Scans repo, detects stack, and generates a CI/CD pipeline."""
    console.print("[bold blue]Scanning repository...[/bold blue]")
    files = scan_repo()

    if not files:
        console.print("[yellow]No relevant files found in the current directory.[/yellow]")
        return

    stack = detect_stack(files)

    provider_key, api_key = get_best_provider()

    if not api_key:
        console.print("[bold red]Error:[/bold red] No AI API Key found in environment.")
        console.print("Please run [code]ai-pipeline init[/code] to set a key.")
        return

    console.print(Panel(f"""
    [bold]Detected Stack:[/bold]
    Language: {stack.language or 'Unknown'}
    Tests: {stack.tests or 'Unknown'}
    Container: {'Docker' if stack.container else 'None'}
    [bold]Using AI Provider Key:[/bold] {provider_key or 'Custom'}
    """, title="Analysis", expand=False))

    console.print("[bold blue]Generating pipeline with AI...[/bold blue]")
    try:
        pipeline_content = generate_pipeline(stack, api_key, provider_key)

        output_dir = Path(".github/workflows")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "ci.yml"

        with open(output_file, "w") as f:
            f.write(pipeline_content)

        console.print(f"[bold green]Success![/bold green] Pipeline generated at {output_file}")
        console.print(Panel(pipeline_content, title="Generated Pipeline", border_style="green"))

    except Exception as e:
        console.print(f"[bold red]Error generating pipeline:[/bold red] {e}")

@app.command()
def analyze():
    """Prints detected stack."""
    files = scan_repo()
    if not files:
        console.print("[yellow]No relevant files found.[/yellow]")
        return

    stack = detect_stack(files)

    security = ", ".join(stack.security_tools) if stack.security_tools else "None"

    console.print(Panel(f"""
    [bold]Detected Stack:[/bold]
    Language: {stack.language or 'Unknown'} (Version: {stack.language_version or 'Latest'})
    Tests: {stack.tests or 'Unknown'}
    Container: {'Docker' if stack.container else 'None'}
    Infrastructure: {stack.infrastructure or 'None'}
    Cloud: {stack.cloud or 'None'}
    Security Tools: {security}
    """, title="Stack Analysis", expand=False))

@app.command()
def init():
    """Configures AI API key."""
    # Scan environment
    found = config.scan_environment()

    key_name = ""
    key_val = ""

    if found:
        console.print("[green]Existing keys found in your environment:[/green]")
        key_name, key_val = select_from_found(found, "Select a key to save as default or enter '0' to add a new one")

        # fail
        if not key_name or key_name == "0":
            key_name = Prompt.ask("Enter the Custom AI Key Name")
            key_val = Prompt.ask(f"Enter the value for {key_name}", password=True)
    else:
        key_name = Prompt.ask("Enter the AI Key Name (e.g., your environment variable name)")
        key_val = Prompt.ask(f"Enter the value for {key_name}", password=True)

    console.print(f"\n[bold green]Configuration Selected:[/bold green]")
    console.print(f"To use this key as default, run the following command in your terminal:")
    console.print(f"\n[cyan]export AI_PROVIDER_KEY={key_name}[/cyan]")
    console.print(f"[cyan]export AI_API_KEY={key_val}[/cyan]")
    console.print(f"\n[yellow]Note: No .env file was created. You must set these variables in your environment.[/yellow]")

if __name__ == "__main__":
    app()
