import json, re, time
import os

from chatgpt import create_chat_completion
from mysql import MySQLDB
from config import cfg
from chatdb_prompts import prompt_ask_steps, prompt_ask_steps_no_egs, synonyms
from tables import init_database, database_info, table_details
from langchain.prompts import PromptTemplate
from langchain.input import get_colored_text
from call_ai_function import populate_sql_statement
from chat import chat_with_ai


def get_steps_from_response(response):
    # Regular expression patterns to extract step number, description, and SQL query
    # pattern = r"```\nStep(\d+):\s+(.*?)\n(.*?)\n```"
    # pattern = r"Step(\d+):\s+(.*?)\n(.*?)\n\n"  # 修改后的模式
    # matches = re.findall(pattern, response, re.DOTALL)
    color_text = get_colored_text(f"SQL generate response:\n{response}",'yellow')
    print(color_text)
    data = eval(response)
    if not isinstance(data,list):
        return

    result = []
    for item in data:
        if isinstance(item,tuple):
            result.append({
                    "id": int(item[0]),
                    "description": item[1].strip(),
                    "sql": item[2].strip(),
                })
        if isinstance(item,dict):
            result.append({
                "id": int(item["step_num"]),
                "description": item["description"].strip(),
                "sql": item["sql"].strip(),
            })

    # Extract information and create list of dictionaries

    # for match in matches:
    #     step_number = int(match[0])
    #     description = match[1]
    #     sql_query = match[2]
    #     # print(sql_query+'\n')
    #     result.append({
    #         "id": step_number,
    #         "description": description.strip(),
    #         "sql": sql_query.replace("`","").strip(),
    #     })

    return result


def init_system_msg():
    sys_temp = """
You are ChatDB, a powerful AI assistant, a variant of ChatGPT that can utilize databases as external symbolic memory. \
You are an expert in databases, proficient in SQL statements and can use the database to help users. \
The details of tables in the database are delimited by triple quotes.
\"\"\"
{table_details}
\"\"\"
"""
    sys_prompt = PromptTemplate(
        template=sys_temp,
        input_variables=[],
        partial_variables={"table_details": table_details, }
    )
    sys_prompt_str = sys_prompt.format()
    return sys_prompt_str


def chain_of_memory(sql_steps, mysql_db):
    num_step = len(sql_steps)
    sql_results_history = []
    new_mem_ops = []
    for i in range(num_step):
        cur_step = sql_steps[i]
        ori_sql_cmd = cur_step['sql']
        color_text = get_colored_text(f"\nStep{cur_step['id']}: {cur_step['description']}\n", 'yellow')
        print(color_text)
        if need_update_sql(ori_sql_cmd):
            list_of_sql_str = populate_sql_statement(ori_sql_cmd, sql_results_history)
            color_text = get_colored_text(f"SQL command: \n{ori_sql_cmd}\n", 'yellow')
            print(color_text)
            new_mem_ops.append(list_of_sql_str)
            for sql_str in list_of_sql_str:
                color_text = get_colored_text(f"Execute: \n{sql_str}\n", 'yellow')
                print(color_text)
                sql_results, sql_res_str = mysql_db.execute_sql(sql_str)
                color_text = get_colored_text(f"Database response:\n{sql_res_str}\n", 'yellow')
                print(color_text)
                if sql_results:
                    sql_results_history.append(sql_results)
        else:
            color_text = get_colored_text(f"Execute: \n{ori_sql_cmd}\n", 'yellow')
            print(color_text)
            sql_results, sql_res_str = mysql_db.execute_sql(ori_sql_cmd)
            new_mem_ops.append([ori_sql_cmd])
            color_text = get_colored_text(f"Database response:\n{sql_res_str}\n", 'yellow')
            print(color_text)
            if sql_results:
                sql_results_history.append(sql_results)
    return sql_results_history, new_mem_ops


def generate_chat_responses(user_inp, mysql_db, historical_message,use_semantic_answer=True):
    # ask steps
    prompt_ask_steps_str = prompt_ask_steps.format(user_inp=user_inp).replace("__synonyms_str__",synonyms)
    response_steps = chat_with_ai(init_system_msg(), prompt_ask_steps_str, historical_message, None,
                                  token_limit=cfg.fast_token_limit)

    historical_message[-2]["content"] = prompt_ask_steps_no_egs.format(user_inp=user_inp).replace("__synonyms_str__",synonyms)

    response_steps_list_of_dict = get_steps_from_response(response_steps)

    if len(response_steps_list_of_dict) == 0:
        print(f"NOT NEED MEMORY: {response_steps}")
        return

    sql_results_history, new_mem_ops = chain_of_memory(response_steps_list_of_dict, mysql_db)
    # print(sql_results_history)
    # print(new_mem_ops)
    if use_semantic_answer:
        try:
            result = semantic_handler(user_inp,response_steps_list_of_dict,sql_results_history)
            color_text = get_colored_text(f"Answer:{result}",'green')
            print(color_text)
            return result,sql_results_history
        except Exception as e:
            print(f"generate_chat_responses error:{e}")
            return None,sql_results_history

    print(f"sql_results_history:\n{sql_results_history}")

    print("Finish!")
    return sql_results_history


def need_update_sql(input_string):
    pattern = r"<\S+>"
    matches = re.findall(pattern, input_string)
    # print(matches)
    # if matches:
    #     print("The pattern was found in the input string.")
    # else:
    #     print("The pattern was not found in the input string.")
    return matches

def semantic_handler(user_inp,response_steps_list_of_dict,sql_results_history):
    prompt_template = """
    Inputs:
    - Question: __query_str__
    - SQLQuery: __sql_str__
    - SQLResult: __sql_result_str__
    
    Requirements:
    - Analyze and interpret the results carefully, combining SQLResult and Question, answer the question accurately and professionally.
    - If the answer is too long, use markdown format to prettify it silently.
    
    Answer:
    
    Reply in the language that the Question used.
    """
    query = str(user_inp)
    sql = str(response_steps_list_of_dict)
    sql_result = str(sql_results_history)

    user_content = prompt_template.replace("__query_str__",query).replace("__sql_str__",sql).replace("__sql_result_str__",sql_result)
    assistant_reply = create_chat_completion(
        model = cfg.fast_llm_model,
        messages=[{
            'role': 'system',
            'content': 'You are a sql master.'
        }, {
            "role":
                "user",
            "content":user_content
        }]
    )

    return assistant_reply

def print_info():
    db_type = os.getenv("DB_TYPE", "sqlite")
    model = os.getenv("FAST_LLM_MODEL","gpt-3.5-turbo")
    color_text = get_colored_text(f"db_type:{db_type}, model:{model}",'red')
    print(color_text)

if __name__ == '__main__':
    # Whether to build examples using the sample files './csvs/*.csv'. Default is True. If data already exists,
    # such as in 'try1024.db', you can select False.
    print_info()
    init_db = False
    use_semantic_answer = True
    mysql_db = init_database(database_info, "try1024", init_db=init_db)
    his_msgs = []
    print("START!")
    text = input("USER INPUT: ")
    while True:
        generate_chat_responses(text, mysql_db, his_msgs,use_semantic_answer)
        text = input("USER INPUT: ")
