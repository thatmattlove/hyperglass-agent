"""Helper functions for CLI message printing."""
# Standard Library
import re

# Third Party
from click import echo, style
from inquirer import prompt
from inquirer.themes import load_theme_from_dict

# Project
from hyperglass_agent.util import color_support
from hyperglass_agent.cli.static import Message
from hyperglass_agent.cli.exceptions import CliError


def inquire(questions):
    """Run inquire.prompt() with a theme if supported."""
    theme = None

    supports_color, num_colors = color_support()

    if supports_color:
        color_themes = {
            "8": {
                "Question": {"mark_color": "green", "brackets_color": "green"},
                "List": {
                    "selection_color": "green",
                    "selection_cursor": ">",
                    "unselected_color": "white",
                },
                "Checkbox": {
                    "selection_color": "blue",
                    "selected_color": "green",
                    "selection_icon": ">",
                    "selected_icon": "X",
                    "unselected_icon": "O",
                    "unselected_color": "white",
                },
            },
            "256": {
                "Question": {"mark_color": "bright_green", "brackets_color": "green"},
                "List": {
                    "selection_color": "bold_green",
                    "selection_cursor": "→",
                    "unselected_color": "white",
                },
                "Checkbox": {
                    "selection_color": "bold_white",
                    "selected_color": "bold_green",
                    "selection_icon": "→",
                    "selected_icon": "●",
                    "unselected_icon": "◯",
                    "unselected_color": "white",
                },
            },
        }
        color_theme = color_themes.get(num_colors)
        if color_theme is not None:
            theme = load_theme_from_dict(color_theme)

    return prompt(questions, theme=theme)


def _base_formatter(state, text, callback, **kwargs):
    """Format text block, replace template strings with keyword arguments.

    Arguments:
        state {dict} -- Text format attributes
        label {dict} -- Keyword format attributes
        text {[type]} -- Text to format
        callback {function} -- Callback function

    Returns:
        {str|ClickException} -- Formatted output
    """
    fmt = Message(state)

    if callback is None:
        callback = style

    for k, v in kwargs.items():
        if not isinstance(v, str):
            v = str(v)
        kwargs[k] = style(v, **fmt.kw)

    if not isinstance(text, str):
        text = str(text)

    text_all = re.split(r"(\{\w+\})", text)
    text_all = [style(i, **fmt.msg) for i in text_all]
    text_all = [i.format(**kwargs) for i in text_all]

    if fmt.emoji:
        text_all.insert(0, fmt.emoji)

    text_fmt = "".join(text_all)

    return callback(text_fmt)


def info(text, callback=echo, **kwargs):
    """Generate formatted informational text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Informational output
    """
    return _base_formatter(state="info", text=text, callback=callback, **kwargs)


def error(text, callback=CliError, **kwargs):
    """Generate formatted exception.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Raises:
        ClickException: Raised after formatting
    """
    raise _base_formatter(state="error", text=text, callback=callback, **kwargs)


def success(text, callback=echo, **kwargs):
    """Generate formatted success text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Success output
    """
    return _base_formatter(state="success", text=text, callback=callback, **kwargs)


def warning(text, callback=echo, **kwargs):
    """Generate formatted warning text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Warning output
    """
    return _base_formatter(state="warning", text=text, callback=callback, **kwargs)


def label(text, callback=echo, **kwargs):
    """Generate formatted info text with accented labels.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Label output
    """
    return _base_formatter(state="label", text=text, callback=callback, **kwargs)


def status(text, callback=echo, **kwargs):
    """Generate formatted status text.

    Arguments:
        text {str} -- Text to format
        callback {callable} -- Callback function (default: {echo})

    Returns:
        {str} -- Status output
    """
    return _base_formatter(state="status", text=text, callback=callback, **kwargs)
