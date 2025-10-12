"""Utility functions for working with Anki notes and fields."""

from anki.notes import Note
from aqt import mw


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
    mw.col = unwrap(mw.col)
    index, _ = mw.col.models.field_map(model)[field_name]
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
