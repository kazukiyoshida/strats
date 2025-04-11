import typer

from .monitors import app as monitors_app
from .strategy import app as strategy_app

app = typer.Typer(
    rich_markup_mode=None,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(strategy_app, name="strategy")
app.add_typer(monitors_app, name="monitors")
