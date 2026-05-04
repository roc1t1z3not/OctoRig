-- BreachSQL Fire Range — MySQL seed data
-- This file is the single source of truth for all MySQL challenge data.
-- It runs automatically when the MySQL container first starts.

-- ============================================================
-- T I E R  1  —  Beginner  (100 pts)
-- Classic integer injection, raw string concat, UNION target
-- ============================================================

CREATE TABLE IF NOT EXISTS my1_users (
    id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64)  NOT NULL,
    email    VARCHAR(128) NOT NULL,
    role     VARCHAR(32)  NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS my1_secrets (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
    value VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my1_notes (
    id      INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    author  VARCHAR(64)  NOT NULL,
    content VARCHAR(512) NOT NULL
);

INSERT INTO my1_users (username, email, role) VALUES
    ('admin',   'admin@firerange.local',   'admin'),
    ('alice',   'alice@firerange.local',   'user'),
    ('bob',     'bob@firerange.local',     'user'),
    ('charlie', 'charlie@firerange.local', 'user');

INSERT INTO my1_secrets (name, value) VALUES
    ('flag',    'FIRE{my1b_union_secrets_extracted}'),
    ('api_key', 'sk-firerange-0xdeadbeef');

INSERT INTO my1_notes (author, content) VALUES
    ('admin', 'FIRE{my1c_double_quote_error}'),
    ('alice', 'meeting at 3pm'),
    ('bob',   'remember to patch the server');

-- ============================================================
-- T I E R  2  —  Intermediate  (250 pts)
-- String param boolean-blind; POST login; OR-based; two-step
-- ============================================================

CREATE TABLE IF NOT EXISTS my2_members (
    id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64)  NOT NULL,
    password VARCHAR(128) NOT NULL,
    secret   VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my2_inbox (
    id        INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    owner     VARCHAR(64)  NOT NULL,
    message   VARCHAR(512) NOT NULL
);

INSERT INTO my2_members (username, password, secret) VALUES
    ('admin',   'hunter2',     'FIRE{my2a_boolean_blind_enumerated}'),
    ('alice',   'p@ssw0rd',    'alice_private_note'),
    ('bob',     'qwerty123',   'bob_private_note'),
    ('mallory', 'evil1337',    'FIRE{my2c_or_based_bypass}');

INSERT INTO my2_inbox (owner, message) VALUES
    ('admin', 'FIRE{my2d_second_step_extracted}'),
    ('alice', 'Hello Alice'),
    ('bob',   'Hello Bob');

-- ============================================================
-- T I E R  3  —  Advanced  (500 pts)
-- Time-blind, path-param, multi-column UNION, paren context
-- ============================================================

CREATE TABLE IF NOT EXISTS my3_items (
    id          INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(64)  NOT NULL,
    description VARCHAR(256) NOT NULL,
    price       DECIMAL(8,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS my3_products (
    id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(64)  NOT NULL,
    category VARCHAR(64)  NOT NULL,
    flag     VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my3_catalog (
    id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title    VARCHAR(64)  NOT NULL,
    brand    VARCHAR(64)  NOT NULL,
    sku      VARCHAR(32)  NOT NULL,
    price    DECIMAL(8,2) NOT NULL,
    flag     VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my3_accounts (
    id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64)  NOT NULL,
    dept     VARCHAR(64)  NOT NULL,
    flag     VARCHAR(256) NOT NULL
);

INSERT INTO my3_items (name, description, price) VALUES
    ('Widget A',  'Standard widget',            9.99),
    ('Widget B',  'Premium widget',             19.99),
    ('Flag Item', 'FIRE{my3b_path_param_pwned}', 0.01);

INSERT INTO my3_products (name, category, flag) VALUES
    ('Product X', 'electronics', 'FIRE{my3c_multicolumn_union}'),
    ('Product Y', 'clothing',    'red_herring_1'),
    ('Product Z', 'food',        'red_herring_2');

INSERT INTO my3_catalog (title, brand, sku, price, flag) VALUES
    ('Laptop Pro', 'TechCo',  'LP-001', 999.99, 'FIRE{my3d_five_col_union}'),
    ('Mouse',      'TechCo',  'MS-001',  29.99, 'not_the_flag'),
    ('Keyboard',   'TypeFast','KB-001',  79.99, 'not_the_flag');

INSERT INTO my3_accounts (username, dept, flag) VALUES
    ('jsmith', 'engineering', 'FIRE{my3e_paren_context_blind}'),
    ('jdoe',   'marketing',   'not_the_flag');

-- ============================================================
-- T I E R  4  —  Expert  (1000 pts)
-- WAF bypass, JSON body, stacked, numeric time-blind, cookie,
-- header injection
-- ============================================================

CREATE TABLE IF NOT EXISTS my4_entries (
    id      INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    label   VARCHAR(64)  NOT NULL,
    payload VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my4_api_users (
    user_id  INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64)  NOT NULL,
    token    VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my4_sessions (
    session_id VARCHAR(64)  NOT NULL PRIMARY KEY,
    username   VARCHAR(64)  NOT NULL,
    flag       VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my4_numeric_store (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    value INT          NOT NULL,
    flag  VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my4_agent_log (
    id      INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    agent   VARCHAR(512) NOT NULL,
    flag    VARCHAR(256) NOT NULL
);

INSERT INTO my4_entries (label, payload) VALUES
    ('normal',  'benign data'),
    ('flag',    'FIRE{my4a_waf_bypass_comment}'),
    ('decoy',   'nothing_here');

INSERT INTO my4_api_users (username, token) VALUES
    ('system',  'FIRE{my4b_json_body_injection}'),
    ('service', 'not_a_flag_yet');

INSERT INTO my4_sessions (session_id, username, flag) VALUES
    ('sess_abc123', 'admin', 'FIRE{my4e_cookie_injection}'),
    ('sess_def456', 'alice', 'not_the_flag');

INSERT INTO my4_numeric_store (value, flag) VALUES
    (42,   'FIRE{my4d_numeric_time_blind}'),
    (1337, 'not_the_flag');

INSERT INTO my4_agent_log (agent, flag) VALUES
    ('Mozilla/5.0', 'FIRE{my4f_header_injection}'),
    ('curl/7.0',    'not_the_flag');

-- ============================================================
-- T I E R  5  —  Legend  (2500+ pts)
-- Full-chain, crawl-discovered endpoint
-- ============================================================

CREATE TABLE IF NOT EXISTS my5_reports (
    id       INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title    VARCHAR(128) NOT NULL,
    body     TEXT         NOT NULL,
    author   VARCHAR(64)  NOT NULL,
    status   VARCHAR(32)  NOT NULL DEFAULT 'draft'
);

CREATE TABLE IF NOT EXISTS my5_vault (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(32)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS my5_hidden (
    id   INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    key  VARCHAR(64)  NOT NULL,
    flag VARCHAR(256) NOT NULL
);

INSERT INTO my5_reports (title, body, author, status) VALUES
    ('Q1 Review',   'Financial summary for Q1.',       'admin',  'published'),
    ('Incident Log','Security incident details here.', 'secteam','classified'),
    ('Dev Notes',   'Internal architecture notes.',    'devops', 'draft');

INSERT INTO my5_vault (level, flag) VALUES
    ('legend', 'FIRE{my5a_legend_full_chain_owned}');

INSERT INTO my5_hidden (`key`, flag) VALUES
    ('secret', 'FIRE{my5b_crawl_and_conquer}'),
    ('decoy',  'not_a_flag');

-- ============================================================
-- NEW CHALLENGES (my2e, my3f, my4g, my4h, my4j, my5c)
-- ============================================================

-- my2e: HAVING/GROUP BY leak
CREATE TABLE IF NOT EXISTS my2_group_targets (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    dept  VARCHAR(64)  NOT NULL,
    score INT          NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO my2_group_targets (dept, score, flag) VALUES
    ('engineering', 42, 'FIRE{my2e_having_group_by}'),
    ('marketing',   17, 'not_the_flag'),
    ('sales',       99, 'not_the_flag');

-- my3f: hidden schema-flag table (never shown by any normal endpoint)
CREATE TABLE IF NOT EXISTS my3_schema_flag (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    note  VARCHAR(64)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO my3_schema_flag (note, flag) VALUES
    ('hidden', 'FIRE{my3f_schema_walker}');

-- my4h: hex / CHAR() bypass store
CREATE TABLE IF NOT EXISTS my4_hex_store (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(64)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO my4_hex_store (label, flag) VALUES
    ('public',  'not_the_flag'),
    ('secret',  'FIRE{my4h_hex_char_bypass}');

-- my4g / my4j: reuse my4_entries (already seeded with my4a flag)
-- my4i: reuse my4_numeric_store
-- my5c: keyword-doubling vault
CREATE TABLE IF NOT EXISTS my5_kwvault (
    id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(32)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO my5_kwvault (level, flag) VALUES
    ('legend', 'FIRE{my5c_keyword_doubling}');

-- ============================================================
-- Challenge registry (informational — app uses registry.py)
-- ============================================================

CREATE TABLE IF NOT EXISTS challenges (
    challenge_id  VARCHAR(16)  NOT NULL PRIMARY KEY,
    tier          INT          NOT NULL,
    title         VARCHAR(128) NOT NULL,
    description   TEXT         NOT NULL,
    technique     VARCHAR(64)  NOT NULL,
    endpoint      VARCHAR(256) NOT NULL,
    points        INT          NOT NULL,
    flag          VARCHAR(256) NOT NULL
);
