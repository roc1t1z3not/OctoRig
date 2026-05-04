-- BreachSQL Fire Range — PostgreSQL seed data
-- Mounted at /docker-entrypoint-initdb.d/init_pg.sql
-- Runs automatically when the PostgreSQL container first starts.

-- ============================================================
-- PostgreSQL challenges — pg1a through pg4a
-- ============================================================

CREATE TABLE IF NOT EXISTS pg_users (
    id       SERIAL       PRIMARY KEY,
    username VARCHAR(64)  NOT NULL,
    email    VARCHAR(128) NOT NULL,
    flag     VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS pg_secrets (
    id    SERIAL       PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
    value VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS pg_employees (
    id       SERIAL       PRIMARY KEY,
    name     VARCHAR(64)  NOT NULL,
    dept     VARCHAR(64)  NOT NULL,
    flag     VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS pg_orders (
    id         SERIAL       PRIMARY KEY,
    product    VARCHAR(64)  NOT NULL,
    quantity   INT          NOT NULL,
    status     VARCHAR(32)  NOT NULL,
    flag       VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS pg_logs (
    id         SERIAL       PRIMARY KEY,
    event      VARCHAR(128) NOT NULL,
    source_ip  VARCHAR(64)  NOT NULL,
    flag       VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS pg_sessions (
    id       SERIAL       PRIMARY KEY,
    token    VARCHAR(128) NOT NULL,
    username VARCHAR(64)  NOT NULL,
    flag     VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS pg_vault (
    id    SERIAL       PRIMARY KEY,
    level VARCHAR(32)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS pg_path_orders (
    id       SERIAL       PRIMARY KEY,
    product  VARCHAR(64)  NOT NULL,
    quantity INT          NOT NULL,
    status   VARCHAR(32)  NOT NULL,
    flag     VARCHAR(256) NOT NULL
);

INSERT INTO pg_users (username, email, flag) VALUES
    ('admin',  'admin@pg.local',  'FIRE{pg1a_postgres_error_based}'),
    ('alice',  'alice@pg.local',  'not_the_flag'),
    ('bob',    'bob@pg.local',    'not_the_flag');

INSERT INTO pg_secrets (name, value) VALUES
    ('flag',    'FIRE{pg1b_postgres_boolean_blind}'),
    ('api_key', 'pg-key-0xdeadbeef');

INSERT INTO pg_employees (name, dept, flag) VALUES
    ('Jane Doe',  'security', 'FIRE{pg2a_postgres_sleep}'),
    ('John Smith','devops',   'not_the_flag');

INSERT INTO pg_orders (product, quantity, status, flag) VALUES
    ('Widget',  5,  'shipped',  'FIRE{pg2b_postgres_union}'),
    ('Gadget',  2,  'pending',  'not_the_flag');

INSERT INTO pg_logs (event, source_ip, flag) VALUES
    ('login',   '10.0.0.1',  'FIRE{pg2c_postgres_stacked}'),
    ('logout',  '10.0.0.2',  'not_the_flag');

INSERT INTO pg_path_orders (product, quantity, status, flag) VALUES
    ('Parcel',  1,  'transit',  'FIRE{pg3a_postgres_path_param}'),
    ('Box',     3,  'delivered','not_the_flag');

INSERT INTO pg_sessions (token, username, flag) VALUES
    ('tok_admin',   'admin', 'FIRE{pg3c_postgres_cookie}'),
    ('tok_default', 'guest', 'not_the_flag');

INSERT INTO pg_vault (level, flag) VALUES
    ('legend', 'FIRE{pg4a_postgres_legend}');

-- ============================================================
-- NEW CHALLENGES (pg2d, pg2e, pg2f, pg3d, pg3e, pg4b)
-- ============================================================

-- pg2d: HAVING/GROUP BY leak
CREATE TABLE IF NOT EXISTS pg_group_targets (
    id    SERIAL       PRIMARY KEY,
    dept  VARCHAR(64)  NOT NULL,
    score INT          NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO pg_group_targets (dept, score, flag) VALUES
    ('engineering', 42, 'FIRE{pg2d_pg_having_group_by}'),
    ('marketing',   17, 'not_the_flag');

-- pg2e: hidden schema-flag table
CREATE TABLE IF NOT EXISTS pg_schema_flag (
    id   SERIAL       PRIMARY KEY,
    note VARCHAR(64)  NOT NULL,
    flag VARCHAR(256) NOT NULL
);
INSERT INTO pg_schema_flag (note, flag) VALUES
    ('hidden', 'FIRE{pg2e_pg_schema_walker}');

-- pg2f: second-order injection profiles
CREATE TABLE IF NOT EXISTS pg_profiles (
    id          SERIAL       PRIMARY KEY,
    username    VARCHAR(64)  NOT NULL,
    bio         VARCHAR(512) NOT NULL DEFAULT '',
    flag        VARCHAR(256) NOT NULL DEFAULT 'not_the_flag'
);
INSERT INTO pg_profiles (username, bio, flag) VALUES
    ('admin', '', 'FIRE{pg2f_pg_second_order}'),
    ('alice', '', 'not_the_flag');

-- pg3d: dollar-quoting bypass store
CREATE TABLE IF NOT EXISTS pg_quote_store (
    id    SERIAL       PRIMARY KEY,
    label VARCHAR(64)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO pg_quote_store (label, flag) VALUES
    ('public',  'not_the_flag'),
    ('secret',  'FIRE{pg3d_dollar_quote_bypass}');

-- pg3e: header injection log
CREATE TABLE IF NOT EXISTS pg_agent_log (
    id    SERIAL        PRIMARY KEY,
    agent VARCHAR(512)  NOT NULL,
    flag  VARCHAR(256)  NOT NULL
);
INSERT INTO pg_agent_log (agent, flag) VALUES
    ('Mozilla/5.0', 'FIRE{pg3e_pg_header_injection}'),
    ('curl/7.0',    'not_the_flag');

-- pg4b: pipe-concat vault
CREATE TABLE IF NOT EXISTS pg_pipe_vault (
    id    SERIAL       PRIMARY KEY,
    level VARCHAR(32)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO pg_pipe_vault (level, flag) VALUES
    ('legend', 'FIRE{pg4b_pg_pipe_concat}');

-- pg4c: crawl-and-conquer hidden endpoint
CREATE TABLE IF NOT EXISTS pg_crawl_hidden (
    id    SERIAL       PRIMARY KEY,
    token VARCHAR(64)  NOT NULL,
    flag  VARCHAR(256) NOT NULL
);
INSERT INTO pg_crawl_hidden (token, flag) VALUES
    ('secret', 'FIRE{pg4c_pg_crawl_and_conquer}');
