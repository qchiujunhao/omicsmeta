"""SQLite cache for ontology terms and synonyms."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from omicsmeta.core.normalizer import normalize_text
from omicsmeta.core.types import OntologyTerm


class OntologyCache:
    """Persist ontology labels and synonyms for offline lookup."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.connection = sqlite3.connect(self.path)
        self._init_schema()

    def close(self) -> None:
        self.connection.close()

    def add_terms(self, terms: list[OntologyTerm]) -> None:
        with self.connection:
            for term in terms:
                self.connection.execute(
                    """
                    INSERT OR REPLACE INTO terms (term_id, label, ontology)
                    VALUES (?, ?, ?)
                    """,
                    (term.term_id, term.label, term.ontology),
                )
                for synonym in (term.label, *term.synonyms):
                    self.connection.execute(
                        """
                        INSERT OR IGNORE INTO synonyms (term_id, synonym, normalized_synonym)
                        VALUES (?, ?, ?)
                        """,
                        (term.term_id, synonym, normalize_text(synonym, expand_abbreviations=False)),
                    )

    def search_exact(self, text: str, *, ontology: str | None = None) -> list[OntologyTerm]:
        normalized = normalize_text(text, expand_abbreviations=False)
        query = """
            SELECT terms.term_id, terms.label, terms.ontology
            FROM synonyms
            JOIN terms ON terms.term_id = synonyms.term_id
            WHERE synonyms.normalized_synonym = ?
        """
        params: list[object] = [normalized]
        if ontology:
            query += " AND terms.ontology = ?"
            params.append(ontology)

        rows = self.connection.execute(query, params).fetchall()
        return [OntologyTerm(term_id=row[0], label=row[1], ontology=row[2]) for row in rows]

    def _init_schema(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS terms (
                    term_id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    ontology TEXT NOT NULL
                )
                """
            )
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS synonyms (
                    term_id TEXT NOT NULL,
                    synonym TEXT NOT NULL,
                    normalized_synonym TEXT NOT NULL,
                    UNIQUE(term_id, normalized_synonym),
                    FOREIGN KEY(term_id) REFERENCES terms(term_id)
                )
                """
            )
            self.connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_synonyms_normalized ON synonyms(normalized_synonym)"
            )

