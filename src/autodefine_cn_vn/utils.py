"""Utility functions for working with Anki notes and fields."""

import inspect
from pathlib import Path

from anki.notes import Note
from aqt import mw
from aqt.utils import tooltip


def notify(message: str, period: int = 3000) -> None:
    """Show a tooltip in Anki UI and print the same message to stdout.

    Automatically includes the caller's filename and line number for debugging.

    Args:
        message: The message to display and print
        period: How long to show the tooltip in milliseconds (default: 3000)
    """
    # Get caller's frame info
    frame = inspect.currentframe()
    if frame and frame.f_back:
        caller_frame = frame.f_back
        filename = Path(caller_frame.f_code.co_filename).name
        line_number = caller_frame.f_lineno
        formatted_message = f"[{filename}:{line_number}] {message}"
    else:
        formatted_message = message

    tooltip(formatted_message, period=period)
    print(formatted_message)


def get_field(note: Note, field_name: str) -> str:
    """Get the value of a field from a note by field name.

    Args:
        note: The Anki note to read from
        field_name: The name of the field to retrieve

    Returns:
        The value of the specified field

    Raises:
        KeyError: If the field name does not exist in the note type
    """
    model = unwrap(note.note_type())
    index, _ = unwrap(mw.col).models.field_map(model)[field_name]
    return note.fields[index]


def set_field(note: Note, field: str, value: str) -> None:
    """Set the value of a note field. Overwrite any existing value.

    Args:
        note: The Anki note to modify
        field: The name of the field to set
        value: The value to set in the field

    Raises:
        KeyError: If the field name does not exist in the note type
    """
    model = unwrap(note.note_type())
    index, _ = unwrap(mw.col).models.field_map(model)[field]
    note.fields[index] = value


def unwrap[T](obj: T | None) -> T:
    """Unwrap an optional value, raising an error if None.

    Args:
        obj: The object to unwrap
    """
    if obj is None:
        raise ValueError("Expected object to be not None.")

    return obj
