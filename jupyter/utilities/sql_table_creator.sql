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


CREATE TABLE IF NOT EXISTS cs670research.research_exploration_label1 (
file_name VARCHAR(255) NOT NULL, 
dataset VARCHAR(255) NOT NULL, 
label VARCHAR(255) NOT NULL,
severity VARCHAR(255) NOT NULL,
noise_type VARCHAR(255) NOT NULL,
status VARCHAR(255),
score_1 varchar(255) DEFAULT NULL,
score_2 varchar(255) DEFAULT NULL,
score_3 varchar(255) DEFAULT NULL,
time VARCHAR(255),
actual_str VARCHAR(2000), 
detected_str VARCHAR(2000),
PRIMARY KEY (file_name, dataset, label, severity, noise_type) 
);

CREATE TABLE IF NOT EXISTS cs670research.research_exploration1 (
file_name VARCHAR(255) NOT NULL, 
dataset VARCHAR(255) NOT NULL, 
label VARCHAR(255) NOT NULL,
severity VARCHAR(255) NOT NULL,
noise_type VARCHAR(255) NOT NULL,
status VARCHAR(255),
score VARCHAR(255),
time VARCHAR(255),
actual_str VARCHAR(2000), 
detected_str VARCHAR(2000),
PRIMARY KEY (file_name, dataset, label, severity, noise_type) 
);

