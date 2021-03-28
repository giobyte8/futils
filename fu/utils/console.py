from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "info" : "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})

console = Console(theme=theme)
