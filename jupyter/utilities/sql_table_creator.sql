CREATE DATABASE IF NOT EXISTS cs670research;

CREATE TABLE IF NOT EXISTS cs670research.research_exploration (
file_name VARCHAR(255) NOT NULL, 
dataset VARCHAR(255) NOT NULL, 
label VARCHAR(255) NOT NULL,
status VARCHAR(255),
score VARCHAR(255),
time VARCHAR(255),
actual_str VARCHAR(2000), 
detected_str VARCHAR(2000),
PRIMARY KEY (file_name, dataset, label) 
);
