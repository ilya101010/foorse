-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create tags table
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL,
    tag_type TEXT
);

-- Create table standards
CREATE TABLE table_std (
    table_std_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_title_tag_id INTEGER NOT NULL UNIQUE,
    description TEXT, -- created using OpenAI probably based on data
    indicator_count INTEGER DEFAULT 2,
    FOREIGN KEY (table_title_tag_id) REFERENCES tags(tag_id)
);

-- Create tables table

CREATE TABLE tables (
    table_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_std_id INTEGER NOT NULL,
    table_name TEXT,
    table_filename TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table_std_id) REFERENCES table_std(table_std_id)
);

-- Create indicators table
CREATE TABLE indicators (
    indicator_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_std_id INTEGER NOT NULL,
    indicator_name TEXT NOT NULL, -- indicator parts are seperated with " / ",
    description TEXT,  -- created using OpenAI probably based on data
    FOREIGN KEY (table_std_id) REFERENCES table_std(table_std_id)
);

-- Create subindicators table
CREATE TABLE subindicators (
    subindicator_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subindicator_name TEXT NOT NULL, -- subindicator hierarchical parts are seperated with " > "
    table_std_id INTEGER NOT NULL,
    description TEXT, -- created using OpenAI based on our data
    FOREIGN KEY (table_std_id) REFERENCES table_std(table_std_id)
);

-- Create values table
CREATE TABLE data (
    value_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER NOT NULL,
    indicator_id INTEGER NOT NULL,
    subindicator_id INTEGER NOT NULL,
    value NUMERIC NOT NULL,
    FOREIGN KEY (table_id) REFERENCES tables(table_id),
    FOREIGN KEY (indicator_id) REFERENCES indicators(indicator_id),
    FOREIGN KEY (subindicator_id) REFERENCES subindicators(subindicator_id)
);

-- Create table_tags table
CREATE TABLE table_tags (
    table_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (table_id, tag_id),
    FOREIGN KEY (table_id) REFERENCES tables(table_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);