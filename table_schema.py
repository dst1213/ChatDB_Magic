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

# clinical_trials_detail = """
# CREATE TABLE clinical_trials_detail (
# 	id INTEGER NOT NULL,
# 	doctor_id VARCHAR,
# 	identification_module_nct_id VARCHAR,
# 	identification_module_org_study_id_info_id VARCHAR,
# 	identification_module_organization_full_name VARCHAR,
# 	identification_module_organization_class VARCHAR,
# 	identification_module_brief_title VARCHAR,
# 	identification_module_official_title VARCHAR,
# 	status_module_status_verified_date VARCHAR,
# 	status_module_overall_status VARCHAR,
# 	status_module_start_date_struct_date VARCHAR,
# 	status_module_study_first_submit_date VARCHAR,
# 	status_module_study_first_submit_qc_date VARCHAR,
# 	status_module_study_first_post_date_struct_date VARCHAR,
# 	status_module_study_first_post_date_struct_type VARCHAR,
# 	status_module_last_update_submit_date VARCHAR,
# 	status_module_last_update_post_date_struct_date VARCHAR,
# 	status_module_last_update_post_date_struct_type VARCHAR,
# 	sponsor_collaborators_module_lead_sponsor_name VARCHAR,
# 	sponsor_collaborators_module_lead_sponsor_class VARCHAR,
# 	description_module_brief_summary VARCHAR,
# 	conditions_module_conditions VARCHAR,
# 	conditions_module_keywords VARCHAR,
# 	design_module_study_type VARCHAR,
# 	design_module_phases VARCHAR,
# 	design_module_design_info_allocation VARCHAR,
# 	design_module_design_info_intervention_model VARCHAR,
# 	design_module_design_info_primary_purpose VARCHAR,
# 	design_module_design_info_masking_info_masking VARCHAR,
# 	arms_interventions_module_interventions VARCHAR,
# 	eligibility_module_eligibility_criteria VARCHAR,
# 	eligibility_module_healthy_volunteers VARCHAR,
# 	eligibility_module_sex VARCHAR,
# 	eligibility_module_minimum_age VARCHAR,
# 	eligibility_module_std_ages VARCHAR,
# 	PRIMARY KEY (id)
# );
# """
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
