from data_upserted import get_answer
from flask import Flask, request, jsonify

import os
import time

app = Flask(__name__)

@app.route('/ask_question', methods=['POST'])
def ask_query():
    try:
        query =  request.form['query']
        print("query received")
    except KeyError as e:
        print(f"key error {str(e)}")
        return jsonify({"message": "query is not given" , "status": 400})
    try:
        res , docs = get_answer(query)
        return jsonify({
        "response": res,
        "documents": docs
        }), 200

    except RuntimeError as e:
        print(f"Error -> {str(e)}")
        return jsonify({'message': f'{str(e)}', 'status': 500})
    
    except Exception as e:
        print(f"error -> {str(e)}")
        return jsonify({'message' : f'Internal error. {str(e)}' , 'status': 500})





if __name__ == '__main__':
    app.run(debug=True)

# Print the response


