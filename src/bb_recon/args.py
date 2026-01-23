import argparse

from bb_recon.utils.path_utils import DEFAULT_DATA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))
    parser.add_argument("--target-domain", required=True, help="The root target domain on which to perform recon.")
    parser.add_argument(
        "--include-subdomains",
        action="store_true",
        help="Whether to include subdomain enumeration in the reconnaissance (amass and assetfinder).",
    )
    parser.add_argument(
        "--app-data-dir",
        required=False,
        default=None,
        help=f"Path to the base application data directory. (default: {DEFAULT_DATA_DIR})",
    )
    return parser.parse_args()
