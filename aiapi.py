import openai
import config 
Api_key = config.DevelopmentConfig.OPENAI_KEY

openai.api_key = Api_key 


def generate_chatbot_response( prompt,initiprompt ) : 
    print('entring')
      #message =[]Welcome to Teskerti!  As a virtual assistant for Teskerti,I'm here to assist you with all your travel and tunisian event ticketing needs. Feel free to ask me about upcoming events, ticket options, booking details, and any other information related to the exciting experiences we offer.Please ask questions related to tunisian events for accurate responses.","you can ask about the upcoming Music Festival in Tunis happening on September 15th presented by Edsheron 
      #initial_prompt =("",
   # "Or you can inquire about ticket prices for the 'Culinary Tour' taking place next month. ",
   # "I'm here to help you discover the best experiences Tunisia has to offer!")
    #data = request.get_json()
    #initial_prompt = data.get('initialPrompt', '') 
   
    initial_prompt =initiprompt
    #initial_prompt =("I want you to act as a chef of our website Gourmandise . I will provide you with specific keywords, present arguments and specific guidelines or instructions . Your task is to write detailed responses to those keywords and provide me with specific examples of what should be said to help me to buy food from your restaurent ,  our speciality is italian food and our chef's plat is seafood paella we are open from 2pm to 3am the client can order for a delivery from our website or by calling 22233777 also he can order to prepare it and come after that to receive it by his self  . You should only reply with short answers and some examples and nothing else. Do not write explanations and do not recommend other restaurants  . My first request is : I need help to buy dinner for 2 people.")
    #initial_prompt = userPrompt 
    message = [   {"role": "system", "content": "system message"}, {"role": "user", "content": f"{initial_prompt}\nUser: {prompt}"}]
   
    response = openai.ChatCompletion.create(  model="gpt-3.5-turbo", messages=message,)   
    try : 
           
    
      
         # response = openai.ChatCompletion.create( prompt, model="gpt-3.5-turbo", messages=message )
          answer =  response['choices'][0]['message']['content'].replace('\n','<br>')
         # answer =  response.choices[0].text.strip()
          #relevant_keywords = ["travel", "trip", "vacation", "destination",  "event", "ticket", "Teskerti"]
          #if not any(keyword in answer.lower() for keyword in relevant_keywords):
           # answer =     ("I'm specialized in travel and event ticketing and might not have information about that. ",
                   # "Please refer to our website for more details." )
         # if not is_in_domain(answer):
               # answer = (
           # "I'm specialized in travel and event ticketing and might not have information about that. "
            #"Please refer to our website for more details."
        #)
      
          
    except IndexError : 
          answer = 'Please try a  diffrent question ! '
    return answer 
  
  
# def is_in_domain(answer):
#     # Define phrases or keywords related to your website's domain
#     domain_related_phrases = ["Teskerti", "travel", "event", "ticket", "booking" , "concerts", "festivals", "hi", "thanks"]
    
#     # Check if any of the domain-related phrases are present in the answer
#     for phrase in domain_related_phrases:
#         if phrase.lower() in answer.lower():
#             return True
#     return False