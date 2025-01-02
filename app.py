from flask import Flask, request, jsonify, make_response
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

KULULAJIT = {
    "1": "Ammattikirjallisuus",
    "2": "Edustuskulut",
    "3": "Henkilökunnan koulutus",
    "0": "ATK-laite ja -ohjelmakulut",
    "4": "Matkakulut",
    "7": "Polttoainekulut",
    "5": "Posti- ja lähetyskulut",
    "6": "Toimistotarvikkeet"
}
INSTRUCTIONS = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Käyttöohjeet</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                color: #333;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .container {{
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
                max-width: 600px;
                text-align: center;
                line-height: 1.6;
            }}
            h1 {{
                color: #007BFF;
            }}
            p {{
                margin: 10px 0;
            }}
            pre {{
                background: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                text-align: left;
                overflow-x: auto;
            }}
            a {{
                color: #007BFF;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Käyttöhjeet:</h1>
            <p>Osoite johon lähetetään selitteet POST metodilla:</p>
            <p><a href="{url}" target="_blank">{url}predict</a></p>
            <p>Lisää payload:</p>
            <pre>{{"data": ["selite1", "selite2"]}}</pre>
        </div>
    </body>
    </html>
    """

TESTPAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POST Request Example</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f8ff;
            color: #333;
        }
        header {
            background-color: #1e90ff;
            color: white;
            padding: 10px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        main {
            max-width: 600px;
            margin: 30px auto;
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }
        h1, h2 {
            color: #1e90ff;
            text-align: center;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        label {
            font-weight: bold;
            color: #333;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 10px;
            border: 1px solid #b0c4de;
            border-radius: 5px;
            resize: vertical;
        }
        button {
            background-color: #1e90ff;
            color: white;
            border: none;
            padding: 10px 15px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #4682b4;
        }
        pre {
            background: #e6f7ff;
            border: 1px solid #b0c4de;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        footer {
            text-align: center;
            padding: 10px;
            margin-top: 20px;
            font-size: 14px;
            color: #777;
        }
    </style>
</head>
<body>

    <header>
        <h1>POST Request Example</h1>
    </header>

    <main>
        <h1>Send POST Request and View Results</h1>

        <!-- Form to collect input -->
        <form id="postForm">
            <label for="selite">Selite:</label>
            <textarea id="selite" name="selite" required></textarea>

            <button type="submit">Submit</button>
        </form>

        <h2>Response:</h2>
        <pre id="responseOutput">No response yet.</pre>
    </main>

    <footer>
        © 2024 POST Request Demo
    </footer>

    <script>
        // Add event listener for form submission
        document.getElementById('postForm').addEventListener('submit', function(event) {
            event.preventDefault();  // Prevent form from refreshing the page

            // Collect form data
            const selite = document.getElementById('selite').value;

            // Prepare data to send in POST request
            const data = {
                data: [selite]
            };

            // Send POST request using fetch
            fetch(`http://${window.location.href}:8443/predict`, { // Replace with actual API URL
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())  // Assume response is JSON
            .then(result => {
                // Display response in the "responseOutput" section
                document.getElementById('responseOutput').textContent = JSON.stringify(result, null, 2);
            })
            .catch(error => {
                document.getElementById('responseOutput').textContent = 'Error: ' + error.message;
            });
        });
    </script>

</body
"""

app = Flask(__name__)
model = LogisticRegression()
vectorizer = TfidfVectorizer()

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def load_trained_model():
    global model, vectorizer
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    return _corsify_actual_response(make_response(INSTRUCTIONS.format(url=request.base_url)))

# Endpoint to make predictions
@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    data = request.get_json()
    text = data.get('data', '')

    if not text:
        return jsonify({'error': 'No input text provided'}), 400
    
    resp = []
    sentences = list(text)
    for sentence in sentences:
        # Transform the input text
        text_tfidf = vectorizer.transform([sentence])
    
        # Predict the class
        prediction = model.predict(text_tfidf)

        resp.append(KULULAJIT[str(prediction[0])])

    return _corsify_actual_response(jsonify(resp))

@app.route('/testaa' , methods=['GET', 'OPTIONS'])
def test():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    return _corsify_actual_response(make_response(TESTPAGE))

if __name__ == '__main__':
    
    # Load trained model before starting the Flask app
    load_trained_model()
    
    # Run the Flask app
    app.run(debug=True)