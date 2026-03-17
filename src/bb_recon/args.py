import argparse

from bb_recon.utils.path_utils import DEFAULT_DATA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))
    parser.add_argument("--target-domain", required=True, help="The root target domain on which to perform recon.")
    parser.add_argument(
        "--enumerate-subdomains",
        action="store_true",
        help="Perform subdomain enumeration in the reconnaissance (subfinder and dnsx).",
    )
    parser.add_argument(
        "--app-data-dir",
        required=False,
        default=None,
        help=f"Path to the base application data directory. (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--crawl-endpoints",
        action="store_true",
        help="Crawl discovered endpoints to find more endpoints.",
    )
    parser.add_argument(
        "--log-level",
        help="Set the logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG). (default: INFO)",
    )
    parser.add_argument(
        "--disable-telegram-notifications",
        action="store_true",
        help="Disable telegram notifications.",
    )
    return parser.parse_args()
