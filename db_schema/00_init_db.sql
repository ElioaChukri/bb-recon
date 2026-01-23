CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_domain_name ON domains(domain_name);

CREATE TRIGGER IF NOT EXISTS domains_updated_at
AFTER UPDATE ON domains
FOR EACH ROW
BEGIN
    UPDATE domains SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
end;

CREATE TABLE IF NOT EXISTS subdomains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_id INT NOT NULL,
    subdomain TEXT,
    sources TEXT,
    active BOOLEAN DEFAULT 0,
    ip_address TEXT,
    record_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subdomain ON subdomains(subdomain);
