from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
import pyttsx3

app = Flask(__name__)
CORS(app)  # Allow frontend requests
app.secret_key = 'your-secret-key'  # Needed for session memory

# Set your Groq API Key (Store it securely in env variables)
os.environ['GROQ_API_KEY'] = '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'

# Initialize LLM model
llm = ChatGroq(model_name='llama-3.3-70b-versatile')

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Adjust speed
tts_engine.setProperty('volume', 1.0)  # Adjust volume

# Define mathematician personas
mathematicians = {
    "aryabhatta": "You are Aryabhatta, the ancient Indian mathematician and astronomer. Respond in a formal yet engaging tone, referencing your discoveries such as the place-value system, zero, and your work on planetary motion. Answer as if you are Aryabhatta himself, speaking from the 5th century.",
    "euclid": "You are Euclid, the Greek mathematician known as the Father of Geometry. Respond with logical precision, referencing axioms, postulates, and theorems from your famous book 'Elements'.",
    "gauss": "You are Carl Friedrich Gauss, the Prince of Mathematicians. Respond with analytical depth, referencing number theory, modular arithmetic, and Gaussian distribution.",
    "ramanujan": "You are Srinivasa Ramanujan, the Indian mathematical genius. Respond with intuitive insights, discussing your infinite series, partition functions, and prime number insights."
}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    mathematician = data.get('mathematician', '').lower()

    if not user_input or not mathematician:
        return jsonify({'error': 'Mathematician and message are required'}), 400

    if mathematician not in mathematicians:
        return jsonify({'error': 'Mathematician not supported'}), 400

    # Retrieve conversation history for this mathematician
    history_key = f"history_{mathematician}"
    history = session.get(history_key, '')

    # Generate response using the selected persona
    prompt = f"{mathematicians[mathematician]}\n\nConversation History:\n{history}\n\nUser: {user_input}\n\n{mathematician.capitalize()}:"
    response = llm.predict(prompt)

    # Update conversation history
    history += f"User: {user_input}\n{mathematician.capitalize()}: {response}\n"
    session[history_key] = history

    # Convert response to speech
    audio_file = f"response_{mathematician}.mp3"
    tts_engine.save_to_file(response, audio_file)
    tts_engine.runAndWait()

    return jsonify({'response': response, 'audio_url': f'http://127.0.0.1:5000/audio/{mathematician}'})

@app.route('/audio/<mathematician>', methods=['GET'])
def get_audio(mathematician):
    audio_file = f"response_{mathematician}.mp3"
    if os.path.exists(audio_file):
        return send_file(audio_file, mimetype="audio/mpeg")
    return jsonify({'error': 'Audio file not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
