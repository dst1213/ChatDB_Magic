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

app = Flask(__name__)

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
        mysql_db = init_database(database_info, "try1024", init_db=init_db)
        his_msgs = []
        print("START!")
        text = query
        res = generate_chat_responses(text, mysql_db, his_msgs, use_semantic_answer)
    except Exception as e:
        traceback.print_exc()
        res = {'error': str(e)}
    return {'data': res}



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)