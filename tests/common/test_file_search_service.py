"""
tests/common/test_file_search_service.py

Focused tests for fuzzy file resolution across PDFs, Word documents, and Excel workbooks.
"""

import sqlite3
from pathlib import Path

import pytest

from aether.tools.file_search_service import FileSearchService


class PromptRecorder:
    def __init__(self, response: str):
        self.response = response
        self.calls = []

    def __call__(self, title, options):
        self.calls.append((title, options))
        return self.response


@pytest.fixture
def indexed_db(tmp_path, monkeypatch):
    db_path = tmp_path / "indexed.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE indexed_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            extension TEXT,
            relative_location TEXT,
            absolute_path TEXT UNIQUE,
            modified_time DATETIME,
            is_directory BOOLEAN
        )
        """
    )

    monkeypatch.setattr(
        "aether.tools.file_search_service.get_db_connection",
        lambda: _connect_rows(db_path),
    )
    monkeypatch.setattr(
        FileSearchService,
        "get_user_directories",
        staticmethod(lambda: [tmp_path]),
    )
    monkeypatch.setattr(
        FileSearchService,
        "find_all_files_on_disk",
        staticmethod(lambda *args, **kwargs: []),
    )

    import aether.api.prompt as prompt_module

    monkeypatch.setattr(
        prompt_module,
        "prompt_user_sync",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("prompt should not be used for clear matches")),
    )

    yield conn
    conn.close()


def _connect_rows(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _add_index_row(conn: sqlite3.Connection, path: Path) -> None:
    conn.execute(
        """
        INSERT INTO indexed_files (filename, extension, relative_location, absolute_path, modified_time, is_directory)
        VALUES (?, ?, ?, ?, datetime('now'), 0)
        """,
        (
            path.name,
            path.suffix,
            path.parent.name,
            str(path),
        ),
    )
    conn.commit()


def test_resolve_keyword_matches_pdf_word_and_excel(indexed_db, tmp_path):
    pdf_file = tmp_path / "GRASPINTLT - Website Development Questionnaire.pdf"
    docx_file = tmp_path / "Team Meeting Notes.docx"
    xlsx_file = tmp_path / "Budget Forecast.xlsx"

    for file_path in [pdf_file, docx_file, xlsx_file]:
        file_path.write_text("placeholder", encoding="utf-8")
        _add_index_row(indexed_db, file_path)

    recorder = PromptRecorder("1")

    import aether.api.prompt as prompt_module
    prompt_module.prompt_user_sync = recorder

    assert FileSearchService.resolve("graspintlt pdf") == pdf_file
    assert FileSearchService.resolve("meeting notes word") == docx_file
    assert FileSearchService.resolve("budget excel") == xlsx_file
    assert len(recorder.calls) == 3
    assert all("Did you mean:" in call[0] for call in recorder.calls)