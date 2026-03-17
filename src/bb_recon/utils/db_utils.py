import json
import logging
import sqlite3
from pathlib import Path

from ..models import DnsStatusCode, DnsxResult, HttpxResult, KatanaResult, SubfinderResult

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
        logger.debug(f"Connecting to SQLite database at {db_path}")
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
    logger.debug(f"Upserting {domain} into database")
    conn.execute(
        "INSERT INTO domains (name) VALUES (?) ON CONFLICT DO UPDATE SET updated_at = CURRENT_TIMESTAMP", (domain,)
    )
    conn.commit()


def get_domain_id(conn: sqlite3.Connection, domain: str) -> int | None:
    """
    Retrieve the ID of a domain from the database.
    :param conn: The SQLite database connection.
    :param domain: The domain to look up.
    :return: The ID of the domain if found, otherwise None.
    """

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM domains WHERE name = ?", (domain,))
    row = cursor.fetchone()
    domain_id = row[0] if row else None
    logger.debug(f"Domain {domain} mapped to ID {domain_id}")
    return domain_id


def get_subdomains_by_domain(conn: sqlite3.Connection, domain: str, active: bool = True) -> list[str]:
    """
    Retrieve a list of subdomains by their domain.
    :param conn: The SQLite database connection.
    :param domain: The domain to use for lookup
    :param active: Whether the returned subdomain should be marked as "active" or not
    :return: A list of subdomain names.
    """

    active_param = 1 if active else 0

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.name FROM subdomains s
        JOIN endpoints e ON e.subdomain_id = s.id 
        JOIN domains d ON s.domain_id = d.id
        WHERE d.name = ? AND e.active = ?;
        """,
        (domain, active_param),
    )
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def get_domains(conn: sqlite3.Connection) -> list[str]:
    """
    Retrieve all domains present in the DB.
    :param conn: The SQLite database connection.
    :return: A list of all domain names
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT name FROM domains;
        """
    )
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def get_subdomain_id(conn: sqlite3.Connection, subdomain: str) -> int | None:
    """
    Retrieve the ID of a subdomain from the database.
    :param conn: The SQLite database connection.
    :param subdomain: The subdomain to look up.
    :return: The ID of the subdomain if found, otherwise None.
    """

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subdomains WHERE name = ?", (subdomain,))
    row = cursor.fetchone()
    subdomain_id = row[0] if row else None
    logger.debug(f"Subdomain {subdomain} mapped to ID {subdomain_id}")
    return subdomain_id


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
    logger.info(f"Storing {len(results)} subfinder results for domain {domain} with ID {domain_id}")
    cursor.executemany(
        "INSERT INTO subdomains (domain_id, name, sources) VALUES (?, ?, ?) ON CONFLICT DO UPDATE SET updated_at = CURRENT_TIMESTAMP",
        [(domain_id, r.host, json.dumps(r.sources)) for r in results],
    )
    conn.commit()
    logger.debug("Subfinder results stored successfully.")


def store_dnsx_results(conn: sqlite3.Connection, domain: str, results: list[DnsxResult]) -> None:
    """
    Store dnsx results into the database.
    :param conn: The SQLite database connection.
    :param domain: The target domain for which the results were obtained.
    :param results: A list of dnsx result objects to store.
    :return: None
    """
    cursor = conn.cursor()
    domain_id = get_domain_id(conn, domain)
    logger.info(f"Storing {len(results)} dnsx results for domain {domain} with ID {domain_id}")

    for r in results:
        if r.status_code != DnsStatusCode.NOERROR:
            logger.debug(f"Skipping DNS result for {r.host} due to DNS status code: {r.status_code}")
            continue

        # insert IPs first (shared path)
        cursor.executemany(
            "INSERT INTO ip_addresses (ip) VALUES (?) ON CONFLICT DO NOTHING",
            [(ip,) for ip in r.a_record],
        )

        if r.host == domain:
            # root domain -> insert into domain_ips
            cursor.executemany(
                """
                INSERT INTO domain_ips (domain_id, ip_id)
                SELECT ?, ip.id
                FROM ip_addresses ip
                WHERE ip.ip = ?
                ON CONFLICT DO UPDATE SET last_updated = CURRENT_TIMESTAMP
                """,
                [(domain_id, ip) for ip in r.a_record],
            )

        else:
            # subdomain case -> insert into subdomains and subdomain_ips
            cursor.execute(
                """
                INSERT INTO subdomains (domain_id, name)
                VALUES (?, ?)
                ON CONFLICT DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                """,
                (domain_id, r.host),
            )

            subdomain_id = get_subdomain_id(conn, r.host)

            cursor.executemany(
                """
                INSERT INTO subdomain_ips (subdomain_id, ip_id)
                SELECT ?, ip.id
                FROM ip_addresses ip
                WHERE ip.ip = ?
                ON CONFLICT DO UPDATE SET last_updated = CURRENT_TIMESTAMP
                """,
                [(subdomain_id, ip) for ip in r.a_record],
            )

        conn.commit()

    conn.commit()
    logger.debug("dnsx results stored successfully.")


def store_httpx_results(conn: sqlite3.Connection, domain: str, results: list[HttpxResult]) -> None:
    """
    Store httpx results into the database.
    :param conn: The SQLite database connection.
    :param domain: The target domain for which the results were obtained.
    :param results: A list of httpx result objects to store.
    :return: None
    """
    domain_id = get_domain_id(conn, domain)
    logger.info(f"Storing {len(results)} httpx results for domain {domain} with ID {domain_id}")

    conn.executemany(
        """
        INSERT INTO endpoints (subdomain_id, url, title, status_code, content_length, content_type)
        SELECT s.id, ?, ?, ?, ?, ?
        FROM subdomains s
        WHERE s.name = ?
        ON CONFLICT DO NOTHING;
        """,
        [
            (r.url, r.title, r.status_code, r.content_length, r.content_type, r.host)
            for r in results
            if r.host != domain
        ],
    )

    conn.commit()
    logger.debug("httpx results stored successfully.")


def store_katana_results(conn: sqlite3.Connection, domain: str, results: list[KatanaResult]) -> None:
    domain_id = get_domain_id(conn, domain)
    logger.info(f"Storing {len(results)} katana results for domain {domain} with ID {domain_id}")

    conn.executemany(
        """
        INSERT INTO endpoints (subdomain_id, url, method, status_code, content_length, content_type)
        SELECT s.id, ?, ?, ?, ?, ?
        FROM subdomains s
        WHERE s.name = ?
        ON CONFLICT DO NOTHING;
        """,
        [
            (r.url, r.method, r.status_code, r.content_length, r.content_type, r.host)
            for r in results
            if r.host != domain and r.status_code is not None  # only store if status_code is present
        ],
    )

    conn.commit()
    logger.debug("katana results stored successfully.")
