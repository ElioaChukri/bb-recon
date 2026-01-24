import argparse

from bb_recon.utils.path_utils import DEFAULT_DATA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))
    parser.add_argument("--target-domain", required=True, help="The root target domain on which to perform recon.")
    parser.add_argument(
        "--enumerate-subdomains",
        action="store_true",
        help="Whether to perform subdomain enumeration in the reconnaissance (subfinder and dnsx).",
    )
    parser.add_argument(
        "--app-data-dir",
        required=False,
        default=None,
        help=f"Path to the base application data directory. (default: {DEFAULT_DATA_DIR})",
    )
    return parser.parse_args()
