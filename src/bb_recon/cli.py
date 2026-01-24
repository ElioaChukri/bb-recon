from dotenv import load_dotenv

from bb_recon.config.recon_config import ReconConfig
from bb_recon.models import parse_dnsx_output, parse_subfinder_output
from bb_recon.utils.db_utils import get_connection, insert_domain, store_dnsx_results, store_subfinder_results
from bb_recon.utils.log_utils import setup_logging
from bb_recon.utils.subprocess_utils import log_and_run


def joy():
    load_dotenv()
    setup_logging()
    config = ReconConfig.load()
    config.initialize_database()
    target_domain = config.cli.target_domain

    with get_connection(config.cli.db_path) as conn:
        insert_domain(conn, target_domain)

        if config.cli.enumerate_subdomains:
            subfinder_command = [
                "subfinder",
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


if __name__ == "__main__":
    joy()
