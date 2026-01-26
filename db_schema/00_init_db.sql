CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_domain_name ON domains(name);

CREATE TABLE IF NOT EXISTS subdomains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id INT NOT NULL,
    name TEXT NOT NULL,
    sources TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    UNIQUE(domain_id, name)
);

CREATE INDEX IF NOT EXISTS idx_subdomain ON subdomains(name);

CREATE TRIGGER IF NOT EXISTS domains_set_updated_at
    BEFORE UPDATE ON domains
    FOR EACH ROW
    BEGIN
        UPDATE domains SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

CREATE TABLE IF NOT EXISTS ip_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_ip_address ON ip_addresses(ip);

CREATE TABLE IF NOT EXISTS domain_ips (
    domain_id INT NOT NULL,
    ip_id INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (domain_id, ip_id),
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    FOREIGN KEY (ip_id) REFERENCES ip_addresses(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_domain_ips ON domain_ips(domain_id, ip_id);

CREATE TRIGGER IF NOT EXISTS domain_ips_set_last_updated
    BEFORE UPDATE ON domain_ips
    FOR EACH ROW
    BEGIN
        UPDATE domain_ips SET last_updated = CURRENT_TIMESTAMP WHERE domain_id = OLD.domain_id AND ip_id = OLD.ip_id;
    END;

CREATE TABLE IF NOT EXISTS subdomain_ips (
    subdomain_id INT NOT NULL,
    ip_id INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (subdomain_id, ip_id),
    FOREIGN KEY (subdomain_id) REFERENCES subdomains(id) ON DELETE CASCADE,
    FOREIGN KEY (ip_id) REFERENCES ip_addresses(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subdomain_ips ON subdomain_ips(subdomain_id, ip_id);

CREATE TRIGGER IF NOT EXISTS subdomain_ips_set_last_updated
    BEFORE UPDATE ON subdomain_ips
    FOR EACH ROW
    BEGIN
        UPDATE subdomain_ips SET last_updated = CURRENT_TIMESTAMP WHERE subdomain_id = OLD.subdomain_id AND ip_id = OLD.ip_id;
    END;

CREATE TABLE IF NOT EXISTS endpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subdomain_id INT NOT NULL,
    url TEXT NOT NULL,
    method TEXT DEFAULT 'GET',
    title TEXT,
    status_code INT,
    active BOOLEAN GENERATED ALWAYS AS (status_code IS NOT NULL AND status_code != 404) STORED,
    content_length INT,
    content_type TEXT,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subdomain_id) REFERENCES subdomains(id) ON DELETE CASCADE,
    UNIQUE(subdomain_id, url)
);

CREATE INDEX IF NOT EXISTS idx_endpoints_url_code ON endpoints(subdomain_id, url, status_code);