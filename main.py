import json
import os.path
import traceback

from bs4 import BeautifulSoup
import requests
from flask import Flask, request, Response, render_template, stream_with_context, jsonify

import config
from chatdb import generate_chat_responses
from log_tools import slogger

from dotenv import load_dotenv

from tables import init_database, database_info, table_details
load_dotenv()

from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # 这行代码将允许所有的跨源请求

@app.route('/health')
def health():
    return {"status": "ok"}

@app.route('/dbqa', methods=['POST'])
def dbqa_handler():
    user = request.form.get("user", "")
    domain = request.form.get("domain", "faq")
    lang = request.form.get("lang", "简体中文")  # lang字面量必须和query的语言一致才可以
    query = request.form.get("query", "hello")
    slogger.info(f"user:{user}, domain:{domain}, lang:{lang}, query:{query}")
    try:
        init_db = False
        use_semantic_answer = True
        db_path = r"D:\vm_share\xinkang_workspace\sqa_chat\med_db"  # TODO
        db_file = os.path.join(db_path,f"{user}")
        slogger.info(f"db file:{db_file}")
        mysql_db = init_database(database_info, db_file, init_db=init_db)
        # mysql_db = init_database(database_info, "try1024", init_db=init_db)
        his_msgs = []
        print("START!")
        text = query
        result,sql_results_history = generate_chat_responses(text, mysql_db, his_msgs, use_semantic_answer)
        if not result and sql_results_history:
            data_len = len(sql_results_history[-1])  # history是所有轮，-1是当前轮
            _info = f"数据总条数：{data_len}，\n前3条数据：\n{flatten_list(sql_results_history[-1][:3])}"
            result = _info
    except Exception as e:
        traceback.print_exc()
        result = {'error': str(e)}

    return {'data': result}

def flatten_list(nested_list):
    # 将内层的列表转化为字符串，元素之间用","拼接
    inner_join = [",".join(map(str, sublist)) for sublist in nested_list]

    # 将转化后的字符串列表再转化为一个字符串，每个元素间用"\n"拼接
    final_str = "\n".join(inner_join)

    print(final_str)

    return final_str

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)