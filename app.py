from flask import Flask, render_template, jsonify, request , session
import config
import aiapi
import openai 
from flask_cors import CORS, cross_origin
from flask_login import UserMixin , login_user , LoginManager , login_required , logout_user , current_user
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

CORS(app)




def page_not_found(e):
  return render_template('404.html'), 404
app.register_error_handler(404, page_not_found)

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
       #prompt = request.form['prompt']
       data = request.json  # This should contain the 'prompt' key
       prompt = data.get('prompt')
       answer = aiapi.generate_chatbot_response(prompt)
       res = {"answer": answer}
      # res['answer']  = aiapi.generate_chatbot_response(prompt)
       return jsonify(res) , 200
    return render_template('index.html', **locals())

  
    """ user_input = request.form.get('prompt')  
        if user_input:
            print("User input provided:", user_input)
            answer = aiapi.generate_chatbot_response(user_input)
            session['answer'] = answer
            return jsonify({'answer': answer}), 200
        else:
            print("No input provided")
            return jsonify({'error': 'No input provided'}), 400

    answer = session.get('answer', '')
    return render_template('index.html', answer=answer)"""



  
if __name__ == '__main__':
    app.run(debug=True)
