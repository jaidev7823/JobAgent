CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    base_url TEXT,
    type TEXT, -- vc, media, accelerator, directory
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE companies_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    company_name TEXT,
    company_url TEXT,
    page_url TEXT,
    raw_html TEXT,
    raw_text TEXT,
    extracted_json TEXT, -- optional structured scrape
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    website TEXT,
    description TEXT,
    stage TEXT, -- Seed / Pre-Seed / Series A
    total_funding TEXT,
    funding_amount INTEGER,
    team_size INTEGER,
    stack TEXT, -- JSON string
    ai_focus INTEGER, -- 1 or 0
    devtools_focus INTEGER,
    saas_focus INTEGER,
    automation_focus INTEGER,
    product_company INTEGER, -- 1=yes, 0=no
    founder TEXT,
    founder_linkedin TEXT,
    hiring_page TEXT,
    estimated_salary_min INTEGER,
    estimated_salary_max INTEGER,
    yc_backed INTEGER,
    accelerator TEXT,
    location TEXT,
    score INTEGER, -- relevance score for you
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE funding_rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    round_type TEXT,
    amount INTEGER,
    date DATE,
    investors TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE company_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    source_id INTEGER,
    source_url TEXT,
    confidence_score REAL,
    FOREIGN KEY(company_id) REFERENCES companies(id),
    FOREIGN KEY(source_id) REFERENCES sources(id)
);

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    title TEXT,
    description TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    remote INTEGER,
    location TEXT,
    url TEXT,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE company_ai_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    raw_analysis TEXT,
    qualifies INTEGER, -- 1 or 0
    reasoning TEXT,
    score INTEGER,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);
