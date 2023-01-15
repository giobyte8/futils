from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "info" : "cyan",
    "success": "green",
    "warning": "orange1",
    "error": "red"
})

console = Console(theme=theme)
