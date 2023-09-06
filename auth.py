import pymysql
#from app import app
from flask import Flask, request , session,render_template,jsonify
from flask_session import Session
from config import mysql ,app
import os
import main
import hashlib
import jwt
import datetime
import secrets
import json
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, JWTManager 
from datetime import datetime, timedelta, timezone
import aiapi


# Générer une clé secrète aléatoire de 24 caractères
# secret_key = os.urandom(24)

# # Convertir la clé binaire en une chaîne de caractères hexadécimaux
# app.config['SECRET_KEY'] = secret_key.hex()

# # Configuration de Flask-Session
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# Initialisation de l'extension Flask-Session
# Session(app)

#Oussama 
app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)
def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()
def showMessage(error=None):
    if error is None:
        error = {'status': 404, 'message': 'Record not found: ' + request.url}

    response = jsonify(error)
    response.status_code = error.get('status', 500)
    return response
# @app.route('/login', methods=['POST'])
# def login_user():
 
#     _json = request.json
#     print(request.json)
#     _Email = _json['Email']
#     _password = _json['password']
#     if not _Email or not _password:
#        print("none")
#        return jsonify({'error': 'Please provide email and password.'}) , 400
     
#     conn = mysql.connect()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
#     cursor.execute("SELECT * FROM users WHERE Email = %s", _Email)

#     user = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     if user is None:
#         return jsonify({'error':'Email incorrect.'}), 400

#     hashed_password = hash_password(_password)
        
#     if user['password'] != hashed_password:
#             print("incorect !")
#             return jsonify({'error': 'Incorrect password!'}) ,401
#     payload = {
#         'user_id': user['id'],
#         'email': user['Email'],
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
#     }
#     token = jwt.encode(payload, app.secret_key, algorithm='HS256')

    
#     session['user_id'] = user['id']

    
#     return jsonify({'message': 'successful login ! Welcome, {}.'.format(user['Lastname']),  'token': token,'status_code':'200'})

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response
#Create User:     
@app.route('/create', methods=['POST'])
def create_user():
    print("Entering create_user function")
    cursor = None  
    conn = None  
    try:        
        print("Entering create_user function")
        _json = request.json
        _Firstname = _json['Firstname']
        _Lastname = _json['Lastname']
        _email= _json['Email']
        _password = _json['password']	
        
        if _Firstname and _Lastname and _email and _password and request.method == 'POST':
            print("Entering create_user function")           
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            cursor.execute("SELECT * FROM users WHERE email = %s", _email)
            
            existing_user = cursor.fetchone()
            
            if existing_user:
                print("Entering create_user function exist")
                return jsonify({'error': 'Email address already used'}), 400
            print("Entering create_user function2")
            hashed_password = hash_password(_password) 
            
            sqlQuery = "INSERT INTO users(Firstname,Lastname ,  email,password) VALUES(%s, %s, %s, %s)"
            
            bindData = (_Firstname,_Lastname, _email, hashed_password)    
                    
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            user_id = cursor.lastrowid  # Assuming user id is an auto-incremented column
            access_token = create_access_token(identity=user_id)
            response = {"access_token": access_token}
            return jsonify({'message': 'User added successfully!', 'token': access_token}), 200

           # return jsonify({'User added successfully!', 'token': token.decode('utf-8')}), 200
        else:
            
            return showMessage({'error': 'Invalid requestt'}), 400
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()        
    
    return jsonify({'error': 'Invalid request'}), 400


@app.route('/login', methods=['POST'])
def login_user():
    _json = request.json
    print(request.json)
    _Email = _json['Email']
    _password = _json['password']
    if not _Email or not _password:
       print("none")
       return jsonify({'error': 'Please provide email and password.'}) , 400
     
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE Email = %s", _Email)

    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user is None:
        return jsonify({'error':'Email incorrect.'}), 400

    hashed_password = hash_password(_password)
        
    if user['password'] != hashed_password:
            print("incorect !")
            return jsonify({'error': 'Incorrect password!'}) ,401
    access_token = create_access_token(identity=user['id'])
    response = {"access_token": access_token}
    
    return jsonify({'message': 'successful login ! Welcome, {}.'.format(user['id']),  'token':  access_token,'status_code':'200'})

@app.route('/logout', methods=["POST"])
def logout_user():
    # Déconnecter l'utilisateur en supprimant les données de session
    # session.clear()
    # return jsonify({'message': 'You have been successfully logged out.', 'status_code':'200'})
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response
@app.route('/createchtbot', methods=['POST'])
@jwt_required()
def create_chatbot():
    cursor = None  
    conn = None  
    try:        
        _json = request.json
        _name = _json['name']
        _nameColor =_json['nameColor']
        _prompt = _json['prompt']
        _senderColor = _json['senderColor']
        _chatbotmsgColor = _json['chatbotmsgColor']
        _headerColor = _json['headerColor']
        _bodyColor = _json['bodyColor']
        _photo_data = _json['photo_data']
        _user_id = get_jwt_identity()
        print( _user_id)
        if _name and _prompt and _senderColor and _chatbotmsgColor and _headerColor and _bodyColor and _photo_data and _nameColor and request.method == 'POST':
            print('aaa')
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)	
            user_query = "SELECT id FROM users WHERE id = %s"
            cursor.execute(user_query, (_user_id,))
            user = cursor.fetchone()
            if user:
                print('aaa')
                sqlQuery = "INSERT INTO chatbots (name, prompt, senderColor, chatbotmsgColor, headerColor, bodyColor, photo_data, user_id , nameColor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                bindData = (_name, _prompt, _senderColor, _chatbotmsgColor, _headerColor, _bodyColor, _photo_data, _user_id, _nameColor)
                 
                cursor.execute(sqlQuery, bindData)
                conn.commit()
                new_chatbot_id = cursor.lastrowid
                return jsonify({'message': 'Chatbot added successfully!', 'chatbot_id': new_chatbot_id}), 200
            else:
                return jsonify({'error': 'Invalid user_id'}), 400
        else:
            return jsonify({'error': 'Invalid request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()        

    return jsonify({'error': 'Invalid request'}), 400
#update the chatbot 
@app.route('/updatechatbot/<chatbots_id>', methods=['PUT'])
@jwt_required()
def update_chatbots(chatbots_id):
    cursor = None  
    conn = None 
    try:
        _json = request.json
        
        _name = _json['name']
        _prompt = _json['prompt']
        _senderColor = _json['senderColor']
        _chatbotmsgColor = _json['chatbotmsgColor']
        _headerColor = _json['headerColor']
        _bodyColor = _json['bodyColor']
        _photo_data = _json['photo_data']
        
        _nameColor = _json['nameColor']
        _user_id = get_jwt_identity()
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        user_query = "SELECT id FROM users WHERE id = %s"
        cursor.execute(user_query, (_user_id,))
        user = cursor.fetchone()
        if user:
                print('aaa')
        # Check if the provided chatbotid exists
                chatbot_query = "SELECT id FROM chatbots WHERE id  = %s"
                print(chatbot_query)
                print(chatbots_id)
                cursor.execute(chatbot_query, ( chatbots_id,))
                chatbot = cursor.fetchone()
        
                if not chatbot:
                     return jsonify({'message': 'Chatbot not found'}), 404
        
        # Use PUT method condition here
                print(_name, _prompt, _senderColor, _chatbotmsgColor, _headerColor, _bodyColor, _photo_data, _user_id, _nameColor,chatbots_id)
                if _name and _prompt and _senderColor and _chatbotmsgColor and _headerColor and _bodyColor and _photo_data and _user_id and _nameColor:
                      print('here!')
                      sqlQuery = "UPDATE chatbots SET name=%s, prompt=%s, senderColor=%s, chatbotmsgColor=%s, headerColor=%s, bodyColor=%s, photo_data=%s, user_id=%s , nameColor	=%s WHERE id=%s"
                      bindData = (_name, _prompt, _senderColor, _chatbotmsgColor, _headerColor, _bodyColor, _photo_data, _user_id, _nameColor,chatbots_id)     
                      cursor.execute(sqlQuery, bindData)
                      conn.commit()
                      return jsonify('Chatbot Updated successfully!'), 200
                      
                else:
                    return jsonify({'error': 'Invalid request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return jsonify({'error': 'Invalid request'}), 400
#get les données de tous les chatbots creer par le user connecté : 

@app.route('/chatbots')
@jwt_required()
def chatbots():
        
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        _user_id = get_jwt_identity()
        print(_user_id)
        user_query = "SELECT id FROM chatbots WHERE user_id  = %s"
        cursor.execute(user_query, (_user_id,))
        user = cursor.fetchone()
        if user:
           print(_user_id,"user exist")
           cursor.execute("SELECT id ,name, prompt, senderColor, chatbotmsgColor, headerColor, bodyColor, photo_data, user_id , nameColor FROM chatbots where user_id=%s ",_user_id)
           empRows = cursor.fetchall()
           for row in empRows:
               row['photo_data'] = row['photo_data'].decode('utf-8')
           response = jsonify(empRows)
           response.status_code = 200
           return response
        else : print("user does not exists!")  
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        if cursor:
            cursor.close() 
        if conn:
            conn.close()
    return jsonify({'error': 'Invalid request'}), 400

#get des données du chatbot selon lid du chatbot et l'id du user coonnecté : 
@app.route('/chatbots/<chatbots_id>',methods=["GET"])
@jwt_required()
def chatbots_details(chatbots_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        _user_id = get_jwt_identity()
        print (_user_id)
        user_query = "SELECT id FROM chatbots WHERE user_id  = %s"
        cursor.execute(user_query, (_user_id,))
        user = cursor.fetchone()
        if user:
            print(_user_id , "user exists ! ")
            
            chatbot_query = "SELECT id FROM chatbots WHERE id  = %s"
            print(chatbot_query)
            print(chatbots_id)
            cursor.execute(chatbot_query, ( chatbots_id,))
            chatbot = cursor.fetchone()
            if chatbot : 
                print(chatbots_id)
                cursor.execute("SELECT name, prompt, senderColor, chatbotmsgColor, headerColor, bodyColor, photo_data, user_id ,nameColor	 FROM chatbots WHERE user_id=%s and id =%s",(_user_id , chatbots_id))
                chatbotRow = cursor.fetchone()
                if chatbotRow is not None:
                    chatbotRow['photo_data'] = chatbotRow['photo_data'].decode('utf-8')
                    return jsonify(chatbotRow), 200
                else:
                    return jsonify({'error': 'Chatbot not found'}), 404
        else : 
                return jsonify({'error': 'user not found'}), 404
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close() 
        if conn:
            conn.close()
    return jsonify({'error': 'Invalid request'}), 400

# Delete du chatbot 
@app.route('/deletechatbot/<chatbotid>', methods=['DELETE'])
@jwt_required()
def delete_chatbot(chatbotid):
    try:
        conn = mysql.connect()

        cursor = conn.cursor()
        _user_id = get_jwt_identity()
        print (_user_id)
        user_query = "SELECT id FROM chatbots WHERE user_id  = %s"
        cursor.execute(user_query, (_user_id,))
        user = cursor.fetchone()
        if user:
            print(_user_id , "user exists ! ")
            cursor.execute("DELETE FROM chatbots WHERE id =%s", (chatbotid,))
            conn.commit()
            respone = jsonify('Chatbot deleted successfully!')
            respone.status_code = 200
            return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()

#generation de la prompt initiale 
initprompt_value = None

@app.route('/initialpompt', methods = ['POST'])
def initi():
    global initprompt_value
    data = request.json  # This should contain the 'prompt' key
    prompt = data.get('initprompt')
    initprompt_value = prompt
    return prompt

#Chatbot relation avec lopen ai : 
@app.route('/openaires', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
       #prompt = request.form['prompt']
       data = request.json  # This should contain the 'prompt' key
       prompt = data.get('prompt')
       global initprompt_value
       answer = aiapi.generate_chatbot_response(prompt,initprompt_value)
       res = {"answer": answer}
      # res['answer']  = aiapi.generate_chatbot_response(prompt)
       return jsonify(res) , 200
    return render_template('index.html', **locals())

getdataa = None
#get des données du chatbot selon lid du chatbot sans user connecté : 
@app.route('/chatboturl/<chatbots_id>',methods=["GET"])
def chat(chatbots_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        chatbot_query = "SELECT id FROM chatbots WHERE id  = %s"
        print(chatbot_query)
        print(chatbots_id)
        cursor.execute(chatbot_query, ( chatbots_id,))
        chatbot = cursor.fetchone()
        print(chatbots_id)
        cursor.execute("SELECT name, prompt, senderColor, chatbotmsgColor, headerColor, bodyColor, photo_data, user_id ,nameColor	 FROM chatbots WHERE   id =%s",( chatbots_id))
        chatbotRow = cursor.fetchone()
        
        if chatbotRow is not None:
                    chatbotRow['photo_data'] = chatbotRow['photo_data'].decode('utf-8')
                   
                    return jsonify(chatbotRow), 200
        else:
                 return jsonify({'error': 'Chatbot not found'}), 404
        
    except Exception as e:
      print(e)
    finally:
      if cursor:
        cursor.close() 
      if conn:
        conn.close()
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/getdata')
def getdata():
    global getdataa

    return getdataa

if __name__ == "__main__":
    app.run(debug=True)