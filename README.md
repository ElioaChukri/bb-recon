# bb-recon

A reconnaissance automation tool for bug bounty hunting that orchestrates multiple security scanning tools and stores results in a structured SQLite database.

## Overview

bb-recon chains together several open-source security tools to perform comprehensive reconnaissance on target domains:

- **Subdomain enumeration** via `subfinder`
- **DNS resolution** via `dnsx`
- **HTTP probing** via `httpx`
- **Endpoint crawling** via `katana`

All discovered data (subdomains, IP addresses, endpoints, HTTP metadata) is persisted to SQLite with proper relationships, making it easy to query and track findings over time. Optional Telegram notifications alert you when new live hosts are discovered.

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager
- The following tools must be in your PATH:
  - [subfinder](https://github.com/projectdiscovery/subfinder)
  - [dnsx](https://github.com/projectdiscovery/dnsx)
  - [httpx](https://github.com/projectdiscovery/httpx)
  - [katana](https://github.com/projectdiscovery/katana)

## Installation

```bash
git clone https://github.com/youruser/bb-recon.git
cd bb-recon
uv sync
```

Copy `.env.example` to `.env` and configure your Telegram credentials if you want notifications:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Usage

Basic usage (Probe domain for liveness):

```bash
recon --target-domain example.com
```

Full reconnaissance with subdomain enumeration and endpoint crawling:

```bash
recon --target-domain example.com --enumerate-subdomains --crawl-endpoints
```

### Options

| Flag                               | Description                                                |
|------------------------------------|------------------------------------------------------------|
| `--target-domain`                  | Root domain to scan (required)                             |
| `--enumerate-subdomains`           | Discover subdomains and resolve them to IPs                |
| `--crawl-endpoints`                | Crawl discovered endpoints with headless browser           |
| `--app-data-dir`                   | Custom data directory (default: `~/.local/share/bb-recon`) |
| `--log-level`                      | DEBUG, INFO, WARNING, ERROR, or CRITICAL                   |
| `--disable-telegram-notifications` | Skip Telegram alerts                                       |

## Database

Results are stored in SQLite with the following structure:

- `domains` - Target root domains
- `subdomains` - Discovered subdomains with discovery source
- `ip_addresses` - Resolved IPs
- `endpoints` - HTTP endpoints with status codes, titles, content types

The schema includes proper foreign keys and indexes for efficient querying. See `db_schema/00_init_db.sql` for the full schema.

## Development

```bash
just build   # Sync dependencies
just lint    # Run ruff with auto-fixes
```
