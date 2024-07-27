
# Imports go here
from openai import AzureOpenAI
import os
from dotenv import load_dotenv, dotenv_values
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from flask import Flask, request, render_template,redirect,url_for

load_dotenv()

STOP_WORDS = set([
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", 
    "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", 
    "their", "then", "there", "these", "they", "this", "to", "was", "will", "with"
    ])

# Put the keys and endpoints here (never put your real keys in the code)
AOAI_ENDPOINT = os.getenv('AOAI_ENDPOINT')
AOAI_KEY = os.getenv('AOAI_KEY')
MODEL_NAME = "shesharp-fp-hack-gpt35-turbo-16k"

# Define background information for each persona
common_issues = {
    "junior-marketer": [
        "Difficulty in measuring return on investment (ROI).",
        "Challenges in understanding and targeting the right audience.",
        "Difficulty in creating engaging content.",
        "Managing and analyzing data.",
        "Keeping up with marketing trends."
    ],
    "senior-marketer": [
        "Managing large marketing teams and budgets.",
        "Navigating complex market dynamics.",
        "Ensuring alignment with business goals.",
        "Optimizing marketing strategies.",
        "Handling high-level client relationships."
    ],
    "junior-engineer": [
        "Understanding and applying advanced technologies.",
        "Debugging and troubleshooting code.",
        "Limited experience in project management.",
        "Adapting to new development tools.",
        "Collaborating effectively with team members."
    ],
    "senior-engineer": [
        "Leading and mentoring junior engineers.",
        "Managing complex technical projects.",
        "Staying updated with evolving technologies.",
        "Ensuring code quality and standards.",
        "Balancing technical and managerial responsibilities."
    ]
}

# Search keys and endpoints
SEARCH_ENDPOINT = AOAI_ENDPOINT
SEARCH_KEY = AOAI_KEY
AZURE_SEARCH_INDEX = 'margiestraveldocs'

# Set up the client for AI Chat using the contstants and API Version
client = AzureOpenAI(
    api_key= AOAI_KEY,
    azure_endpoint= AOAI_ENDPOINT,
    api_version="2024-05-01-preview",
)

# for search client
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    credential=AzureKeyCredential(SEARCH_KEY),
    index_name=AZURE_SEARCH_INDEX,
)

# Set the tone of the conversation
SYSTEM_MESSAGE = "You are a helpful AI assistant that can answer questions and provide information. You must use the provided sources for your information."

# Function
# def get_response(question,message_history=[]):
#     search_results = search_client.search(search_text=question)
#     search_summary = " ".join(result["content"] for result in search_results)
    
#     # Create a new message history if there isn't one
#     if not message_history:
#         messages=[
#             {"role": "system", "content": SYSTEM_MESSAGE},
#             {"role": "user", "content": question + "\nSources: " + search_summary},
#         ]
#     # Otherwise, append the user's question to the message history
#     else:
#         messages = message_history + [
#             {"role": "user", "content": question + "\nSources: " + search_summary},
#         ]

#     response = client.chat.completions.create(model=MODEL_NAME,temperature=0.7,n=1,messages=messages)
#     answer = response.choices[0].message.content
#     return answer, message_history


#HOKITIKA
# def get_ai_suggestions(persona):
#     # Get the background information for the selected persona
#     issues = common_issues.get(persona, [])
#     # Create the prompt for a chat-based model
#     prompt = (
#         f"Given the following common issues for a {persona.replace('-', ' ')}:\n"
#         f"{', '.join(issues)}\n\n"
#         f"Please select the most relevant issues from this list."
#     )
    
#     # Use the client to generate a response with chat completions
#     response = client.completions.create(
#         model=MODEL_NAME,
#         prompt=prompt,
#         max_tokens=150,
#         temperature=0.5  # Adjust the temperature for more controlled responses
#     )
    
#     # Extract the selected issues from the response
#     selected_issues = response.choices[0].text.strip()
    
#     # Split the response into a list
#     selected_issues_list = selected_issues.split('\n')
    
#     return selected_issues_list

############################################
######## THIS IS THE WEB APP CODE  #########
############################################

# Create a flask app
app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
)


# This is the route for the home page (it links to the pages we'll create)
@app.get('/')
def index():
  # Return a page that links to these three pages /test-ai, /ask, /chat
  return redirect(url_for('chat'))

@app.get('/ask')
def ask():
    return render_template("ask.html")

@app.get('/persona')
def persona():
    return render_template("persona.html")

@app.route('/submit', methods=['POST'])
def submit():
    chosenPersona = request.form['chosenPersona']
    return redirect(url_for('result', chosenPersona=chosenPersona))

@app.route('/result')
def result():
    chosenPersona = request.args.get('chosenPersona')
    issues = common_issues.get(chosenPersona, [])
    return render_template('result.html', issues=issues, chosenPersona=chosenPersona)

@app.route('/contextless-message', methods=['GET', 'POST'])
def contextless_message():
    question = request.json['message']
    resp = get_response(question)
    return {"resp": resp[0]}

@app.get('/chat')
def chat():
    return render_template('chat.html')

@app.route("/context-message", methods=["GET", "POST"])
def context_message():
    question = request.json["message"]
    context = request.json["context"]

    resp, context = get_response(question, context)
    return {"resp": resp, "context": context}

# This is for when there is not a matching route. 
@app.errorhandler(404)
def handle_404(e):
    return '<h1>404</h1><p>File not found!</p><img src="https://httpcats.com/404.jpg" alt="cat in box" width=400>', 404


if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0', debug=True, port=8080)