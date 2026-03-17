import logging
from datetime import datetime

from dotenv import load_dotenv

from bb_recon.config.recon_config import ReconConfig
from bb_recon.models import parse_dnsx_output, parse_httpx_output, parse_katana_output, parse_subfinder_output
from bb_recon.utils.db_utils import (
    get_connection,
    get_subdomains_by_domain,
    insert_domain,
    store_dnsx_results,
    store_httpx_results,
    store_katana_results,
    store_subfinder_results,
)
from bb_recon.utils.log_utils import setup_logging
from bb_recon.utils.path_utils import check_if_required_commands_exist
from bb_recon.utils.subprocess_utils import log_and_run
from bb_recon.utils.telegram_utils import TelegramBot


def joy():
    load_dotenv()
    config = ReconConfig.load()
    setup_logging(config.cli.log_level)
    logger = logging.getLogger(__name__)
    config.initialize_database()
    target_domain = config.cli.target_domain

    if not check_if_required_commands_exist():
        return

    with get_connection(config.cli.db_path) as conn:
        insert_domain(conn, target_domain)

        domains_to_check_liveness = [target_domain]
        if config.cli.enumerate_subdomains:
            subfinder_command = [
                "subfinder",
                "-silent",
                "-domain",
                target_domain,
                "-json",
                "-collect-sources",  # Use JSON output and include all sources which matched this entry
                "-r",
                "8.8.8.8",  # Use Google's public DNS resolver
                "-max-time",
                "20",  # Minutes to wait for enumeration results
            ]

            subfinder_stdout = log_and_run(subfinder_command).stdout
            subfinder_results = parse_subfinder_output(subfinder_stdout)
            store_subfinder_results(conn, target_domain, subfinder_results)

            dnsx_command = [
                "dnsx",
                "-silent",
                "-l",
                "-",  # Read subdomains from stdin
                "-a",  # Perform A record look
                "-r",
                "8.8.8.8",  # Use Google's public DNS resolver
                "-json",  # Output results in JSON format
                "-omit-raw",  # Omit raw DNS response data
            ]
            dnsx_stdin = "\n".join(r.host for r in subfinder_results)
            dnsx_stdout = log_and_run(dnsx_command, stdin=dnsx_stdin).stdout
            dnsx_results = parse_dnsx_output(dnsx_stdout)
            store_dnsx_results(conn, target_domain, dnsx_results)

            domains_to_check_liveness.extend([r.host for r in dnsx_results])

        httpx_command = [
            "httpx",
            "-silent",
            "-fc",
            "404",  # Filter out 404 responses
            "-json",
            "-omit-body",
            "-r",
            "8.8.8.8",  # Use Google's public DNS resolver
            "-auto-referer",
            "-follow-redirects",
            "-e",
            "cdn",  # Exclude hosts with "cdn" in their name
        ]

        httpx_stdin = "\n".join(domains_to_check_liveness)
        httpx_stdout = log_and_run(httpx_command, stdin=httpx_stdin).stdout
        httpx_results = parse_httpx_output(httpx_stdout)

        if config.cli.send_telegram_notification:
            logger.debug("Telegram notifications enabled")
            live_hosts = [r.host for r in httpx_results if r.status_code != 404]
            logger.debug("Live hosts: %s", live_hosts)
            stored_hosts = get_subdomains_by_domain(conn, target_domain, active=True)
            logger.debug("Stored hosts: %s", stored_hosts)
            new_hosts = sorted(set(live_hosts) - set(stored_hosts))
            logger.debug("New hosts: %s", new_hosts)

            now = datetime.now()
            message = f"New subdomains discovered on {now}:\n\n" + "\n".join(new_hosts)
            logger.info("Sending telegram notification: %s", message)
            TelegramBot().send_message(message)

        store_httpx_results(conn, target_domain, httpx_results)

        if config.cli.crawl_endpoints:
            endpoints_to_crawl = [r.url for r in httpx_results if r.status_code != 404]
            katana_command = [
                "katana",
                "-silent",
                "-e",
                "cdn",  # Exclude hosts with "cdn" in their name
                "-r",
                "8.8.8.8",  # Use Google's public DNS resolver
                "-d",
                "3",  # Crawl a depth of 10
                "-js-crawl",
                "-jsluice",
                "-ignore-query-params",
                "-headless",  # Use headless mode
                "-jsonl",  # Output results in JSON Lines format
                "-omit-raw",
                "-omit-body",
                "-crawl-duration",
                "10m",
            ]

            katana_stdin = "\n".join(endpoints_to_crawl)
            katana_stdout = log_and_run(katana_command, stdin=katana_stdin).stdout
            katana_results = parse_katana_output(katana_stdout)
            store_katana_results(conn, target_domain, katana_results)


if __name__ == "__main__":
    joy()
