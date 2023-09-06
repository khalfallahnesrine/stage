import hashlib
import pymysql
#from app import app
from config import mysql ,app
from flask import jsonify
from flask import flash, request,session
import jwt
import datetime
import secrets
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask_session import Session

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
secret_key = secrets.token_urlsafe(32)
print(secret_key)
def showMessage(error=None):
    if error is None:
        error = {'status': 404, 'message': 'Record not found: ' + request.url}

    response = jsonify(error)
    response.status_code = error.get('status', 500)
    return response

def hash_password(password):
    # Hash the password using SHA-256
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()
#user : 
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
                print("Entering create_user function")
                return jsonify({'error': 'Email address already used'}), 400
            print("Entering create_user function")
            hashed_password = hash_password(_password) 
            
            sqlQuery = "INSERT INTO users(Firstname,Lastname ,  email,password) VALUES(%s, %s, %s, %s)"
            
            bindData = (_Firstname,_Lastname, _email, hashed_password)    
                    
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            token = jwt.encode({
                'user_id': cursor.lastrowid,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration time
            }, secret_key, algorithm='HS256')  # Replace 'your_secret_key' with your actual secret key
            
            return jsonify({'message': 'User added successfully!', 'token': token}), 200

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

@app.route('/users')
def user():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, Firstname,Lastname, email,password FROM users")
        empRows = cursor.fetchall()
        respone = jsonify(empRows)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()  
def user_is_logged_in(request):
    return request.user.is_authenticated

# Helper function to check if the session is active
def session_is_active(request):
    # Check if the session is valid and not expired
    return request.session.is_active
@app.route('/users/<users_id>',methods=["GET"])

def users_details(users_id):
    cursor = None  
    conn = None  
    try:
      if user_is_logged_in(users_id) and session_is_active(users_id):
        print("aaaa")
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, Firstname, Lastname, email, password FROM users WHERE id =%s", users_id)
        userRow = cursor.fetchone()
        if userRow is not None:
            return jsonify(userRow), 200
        else:
            return jsonify({'error': 'User not found'}), 404
      else:
            return jsonify({'error': 'Unauthorized'}), 401
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()        
    return jsonify({'error': 'Invalid requestT'}), 400 
        

@app.route('/update/<userid>', methods=['PUT'])
def update_users(userid):
    cursor = None
    conn = None
    try:
        token = request.headers.get('Authorization')  # Get the token from the request headers
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])  # Decode the token
        
        _json = request.json
        _Firstname = _json['Firstname']
        _Lastname = _json['Lastname']
        _email = _json['email']
        _password = _json['password']
        
        # Check if the provided user ID matches the user ID in the token
        if decoded_token.get('user_id') != int(userid.lstrip('0')):
            print("Invalid user ID mismatch:", decoded_token.get('user_id'), userid)
            return jsonify({'error': 'Invalid user ID'}), 400

        # Proceed with the update if the user ID matches
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        hashed_password = hash_password(_password)
        sqlQuery = "UPDATE users SET Firstname=%s, Lastname=%s, email=%s, password=%s WHERE id=%s"
        bindData = (_Firstname, _Lastname, _email, hashed_password, userid)
        cursor.execute(sqlQuery, bindData)
        conn.commit()

        return jsonify({'message': 'User updated successfully!'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return jsonify({'error': 'Invalid request'}), 400



@app.route('/delete//<userid>', methods=['DELETE'])
def delete_user(userid):

	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM users WHERE id =%s", (userid,))
		conn.commit()
		respone = jsonify('User deleted successfully!')
		respone.status_code = 200
		return respone
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
  
  
 #Chatbot :        
app.secret_key = 'herehere'
#Chatbots Crud : 
@app.route('/chatbots')
def chatbots():
        
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT name, prompt, senderColor, chatbotmsgColor, headerColor, bodyColor, photo_data, user_id , nameColor FROM chatbots ")
        empRows = cursor.fetchall()
        for row in empRows:
            row['photo_data'] = row['photo_data'].decode('utf-8')

        response = jsonify(empRows)
        response.status_code = 200
        return response  
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500
    finally:
        if cursor:
            cursor.close() 
        if conn:
            conn.close()

@app.route('/chatbots/<chatbots_id>',methods=["GET"])
def chatbots_details(chatbots_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT name, prompt, senderColor, chatbotmsgColor, headerColor, bodyColor, photo_data, user_id ,nameColor	 FROM chatbots WHERE id =%s", chatbots_id)
        chatbotRow = cursor.fetchone()
        if chatbotRow is not None:
            chatbotRow['photo_data'] = chatbotRow['photo_data'].decode('utf-8')
            return jsonify(chatbotRow), 200
        else:
            return jsonify({'message': 'Chatbot not found'}), 404
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close() 
        if conn:
            conn.close()

@app.route('/updatechatbot/<chatbotid>', methods=['PUT'])
def update_chatbots(chatbotid):
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
        _user_id = _json['user_id']
        _nameColor = _json['nameColor']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Check if the provided chatbotid exists
        chatbot_query = "SELECT id FROM chatbots WHERE id = %s"
        cursor.execute(chatbot_query, chatbotid)
        chatbot = cursor.fetchone()
        
        if not chatbot:
            return jsonify({'message': 'Chatbot not found'}), 404
        
        # Use PUT method condition here
        if _name and _prompt and _senderColor and _chatbotmsgColor and _headerColor and _bodyColor and _photo_data and _user_id and _nameColor:
            sqlQuery = "UPDATE chatbots SET name=%s, prompt=%s, senderColor=%s, chatbotmsgColor=%s, headerColor=%s, bodyColor=%s, photo_data=%s, user_id=%s , nameColor	=%s WHERE id=%s"
            bindData = (_name, _prompt, _senderColor, _chatbotmsgColor, _headerColor, _bodyColor, _photo_data, _user_id, _nameColor,chatbotid)     
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

@app.route('/deletechatbot//<chatbotid>', methods=['DELETE'])
def delete_chatbot(chatbotid):

	try:
		conn = mysql.connect()
		cursor = conn.cursor()
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

@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone
        
if __name__ == "__main__":
    app.run(debug=True)