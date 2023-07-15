from langchain.prompts import PromptTemplate
from sql_examples import egs


# prompt_ask_steps_temp = """
# Please tell me what standard SQL statements should I use in order to respond to the "USER INPUT". \
# If it needs multiple SQL operations on the database, please list them step by step concisely. \
# If there is no need to use the database, reply to the "USER INPUT" directly.
# The output should be a markdown code snippet formatted in the following schema, \
# including the leading and trailing "\`\`\`" and "\`\`\`":
# ```
# Step1: <Description of first step>
# SQL command for step1
#
# Step2: <Description of second step>
# SQL command for step2
#
# ......
# ```
# Here are some examples:
# {egs}
#
# Notice:
# When generating SQL, it's better to use like than =
# Example：
# SELECT email FROM doctor WHERE name = 'Alice Shaw';
# Better usage:
# SELECT email FROM doctor WHERE name LIKE '%Alice Shaw%';
#
# USER INPUT: {user_inp}
# ANSWER:
# """
# prompt_ask_steps_temp = """
# Please tell me what standard SQL statements should I use in order to respond to the "USER INPUT". \
# If it needs multiple SQL operations on the database, please list them step by step concisely. \
# If there is no need to use the database, reply to the "USER INPUT" directly.
# The output should be formatted in the following schema of python tuple list:
# [(1,<Description of first step>,<SQL command for step1>),(2,<Description of second step>,<SQL command for step2>)]
#
# Here are some synonyms for the keywords of the tables:
# __synonyms_str__
#
# Here are some examples:
# {egs}
#
# Notice:
# When generating SQL, it's better to use like than =
# Example：
# SELECT email FROM doctor WHERE name = 'Alice Shaw';
# Better usage:
# SELECT email FROM doctor WHERE name LIKE '%Alice Shaw%';
#
# USER INPUT: {user_inp}
# ANSWER:
# """

prompt_ask_steps_temp = """
Please tell me what standard SQL statements should I use in order to respond to the "USER INPUT". \
If it needs multiple SQL operations on the database, please list them step by step concisely. \
If there is no need to use the database, reply to the "USER INPUT" directly.
The output should be formatted in the following schema of python tuple list:
[(1,<Description of first step>,<SQL command for step1>),(2,<Description of second step>,<SQL command for step2>)]

Here are some synonyms for the keywords of the tables:
__synonyms_str__

Here are some examples:
{egs}

Notice:
When generating SQL, it's better to use like than =
Example：
SELECT email FROM doctor WHERE name = 'Alice Shaw';
Better usage:
SELECT email FROM doctor WHERE name LIKE '%Alice Shaw%';

USER INPUT: {user_inp}
ANSWER:
"""


prompt_ask_steps = PromptTemplate(
        template=prompt_ask_steps_temp,
        input_variables=["user_inp"],
        partial_variables={
            "egs": '\n'.join(egs),
        }
    )

prompt_ask_steps_no_egs = PromptTemplate(
        template=prompt_ask_steps_temp,
        input_variables=["user_inp"],
        partial_variables={
            "egs": ""
        }
    )



def dict_to_str(data):
    result = []
    for key, value_list in data.items():
        value_string = ",".join(value_list)
        result.append(f"{key}:{value_string}")

    output_string = "\n".join(result)
    return output_string

FIELD_SYNONYM_V2 = {"name": ["姓名", "name"],
                    "organization": ["医院机构", "诊所", "药厂", "公司", "hospital", "clinic", "Centers & Institutes"],
                    "department": ["科室", "部门", "department", "Departments / Divisions"],
                    "position": ["职务", "职位", "position", "Academic Appointments", "Administrative Appointments"],
                    "title": ["职称", "title", "Titles"],
                    "phone": ["电话", "contact", "phone", "mobile", "Contact for Research Inquiries"],
                    "email": ["邮箱", "email", "电邮"],
                    "location": ["位置", "地址", "城市", "location", "office location", "Locations",
                                 "Locations & Patient Information"],
                    "introduce": ["个人介绍", "自我介绍", "专家介绍", "简介", "about me", "introduce", "biology", "Bio",
                                  "Background", "About"],
                    "expertise": ["专长", "擅长", "specialty", "expertise", "interests", "Expertise",
                                  "Research Interests",
                                  "Specialties", "Areas of Expertise"],
                    "visit_time": ["出诊时间", "出诊信息", "visit time", "visit hours"],
                    "qualification": ["资格证书", "qualification"],
                    "insurance": ["适用医保", "医疗保险", "医保", "insurance", "Accepted Insurance"],
                    "academic": ["学术兼职", "part-time", "academic", "Boards", "Advisory Committees",
                                 "Professional Organizations", "Memberships", "Professional Activities"],
                    "work_experience": ["工作经历", "work experience", "career", "short bio"],
                    "education": ["学习经历", "学历", "education", "Professional Education", "Education", "Degrees",
                                  "Residencies", "Fellowships", "Board Certifications", "Additional Training",
                                  "Education & Professional Summary"],
                    "publications": ["文献著作", "出版", "论文", "publications", "abstract", "all publications",
                                     "selected publications"],
                    "clinical_trial": ["临床研究", "研究", "clinical_trial", "clinical trials","clinical trial",
                                       "Current Research and Scholarly Interests", "Clinical Trials", "Projects",
                                       "Clinical Trial Keywords", "Clinical Trials & Research"],
                    "achievement": ["荣誉成就", "honor", "achievement", "Honors & Awards", "Honors"],
                    "service_language": ["服务语言", "service language", "language"],
                    "avatar": ["头像", "head", "profile"],
                    "nct_no":["nct number","clinical trial number","临床研究编号"]
                    }


# synonyms = "clinical trials: clinical trial, 临床研究\nnct_no:nct number,clinical trial number,临床研究编号"
synonyms = dict_to_str(FIELD_SYNONYM_V2)


if __name__ == '__main__':
    print(prompt_ask_steps.format(user_inp="Hi"))
    # print(prompt_ask_steps_no_egs.format(user_inp="Hi"))
