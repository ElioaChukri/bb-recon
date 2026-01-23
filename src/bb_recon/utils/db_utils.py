import json
import logging
import sqlite3
from pathlib import Path

from ..models import SubfinderResult

logger = logging.getLogger(__name__)

def get_connection(db_path: Path) -> sqlite3.Connection:
    """
    Establish and return a connection to the SQLite database at the specified path.

    :param db_path: Path to the SQLite database file.
    :return: sqlite3.Connection object.
    :raises sqlite3.OperationalError: If unable to connect to the database.
    :raises sqlite3.Error: For any other SQLite-related errors.
    """
    try:
        logging.debug(f"Connecting to SQLite database at {db_path}")
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(f"Unable to connect to the database file at {db_path}: {e}") from e
    except sqlite3.Error as e:
        raise sqlite3.Error(f"An unexpected SQLite error occurred: {e}") from e

def insert_domain(conn: sqlite3.Connection, domain: str) -> None:
    """
    Insert a domain into the database
    :param conn: The SQLite database connection.
    :param domain: The domain to insert
    :return: None
    """
    logger.debug(f"Inserting {domain} into database")
    conn.execute("INSERT INTO domains (domain_name) VALUES (?) ON CONFLICT DO NOTHING",(domain,))

def get_domain_id(conn: sqlite3.Connection, domain: str) -> int | None:
    """
    Retrieve the ID of a domain from the database.
    :param conn: The SQLite database connection.
    :param domain: The domain to look up.
    :return: The ID of the domain if found, otherwise None.
    """

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM domains WHERE domain_name = ?", (domain,))
    row = cursor.fetchone()
    domain_id = row[0] if row else None
    logger.debug(f"Domain {domain} mapped to ID {domain_id}")
    return domain_id


def store_subfinder_results(conn: sqlite3.Connection, domain: str, results: list[SubfinderResult]) -> None:
    """
    Store subfinder results into the database.
    :param conn: The SQLite database connection.
    :param domain: The target domain for which the results were obtained.
    :param results: A list of SubfinderResult objects to store.
    :return: None
    """

    cursor = conn.cursor()
    domain_id = get_domain_id(conn, domain)
    if domain_id is None:
        raise ValueError(f"Domain '{domain}' not found in the database.")
    logger.debug(f"Storing {len(results)} subfinder results for domain ID {domain_id}")
    cursor.executemany(
        "INSERT INTO subdomains (domain_id, subdomain, sources) VALUES (?, ?, ?)",
        [(domain_id, r.host, json.dumps(r.sources)) for r in results],
    )
    conn.commit()
