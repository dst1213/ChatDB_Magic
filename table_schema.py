achievements = """
CREATE TABLE achievements (
	id INTEGER NOT NULL, 
	doctor_id VARCHAR, 
	type VARCHAR, 
	info VARCHAR, 
	time VARCHAR, 
	PRIMARY KEY (id)
);
"""

doctor = """
CREATE TABLE doctor (
	id INTEGER NOT NULL, 
	doctor_id VARCHAR, 
	name VARCHAR, 
	english_name VARCHAR, 
	email VARCHAR, 
	sex VARCHAR, 
	title VARCHAR, 
	position VARCHAR, 
	contact VARCHAR, 
	biography VARCHAR, 
	expertise VARCHAR, 
	visit_time VARCHAR, 
	qualification VARCHAR, 
	insurance VARCHAR, 
	language VARCHAR, 
	PRIMARY KEY (id)
);
"""
publications = """
CREATE TABLE publications (
	id INTEGER NOT NULL, 
	doctor_id VARCHAR, 
	type VARCHAR, 
	info VARCHAR, 
	time VARCHAR, 
	PRIMARY KEY (id)
);
"""

clinical_trials_detail = """
CREATE TABLE clinical_trials_detail (
	id INTEGER NOT NULL, 
	doctor_id VARCHAR, 
	nct_no VARCHAR, 
	brief_title VARCHAR, 
	inclusion_criteria VARCHAR, 
	exclusion_criteria VARCHAR, 
	PRIMARY KEY (id)
);
"""

medical_research = """
CREATE TABLE medical_research (
	id INTEGER NOT NULL, 
	doctor_id VARCHAR, 
	type VARCHAR, 
	info VARCHAR, 
	time VARCHAR, 
	PRIMARY KEY (id)
);
"""

personal_experience = """
CREATE TABLE personal_experience (
	id INTEGER NOT NULL, 
	doctor_id VARCHAR, 
	type VARCHAR, 
	info VARCHAR, 
	time VARCHAR, 
	PRIMARY KEY (id)
);
"""

pubmed_detail = """
CREATE TABLE pubmed_detail (
	id INTEGER NOT NULL, 
	doctor_id VARCHAR, 
	pid VARCHAR, 
	title VARCHAR, 
	PRIMARY KEY (id)
);
"""

tables = [doctor, publications, achievements,clinical_trials_detail,medical_research,personal_experience,pubmed_detail]
