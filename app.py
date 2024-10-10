import os
import requests
import nacl.signing
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
CORS(app)  # Enable CORS for all routes

def get_real_location():
    """Automatically fetches the user's real location based on IP."""
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()
        return f"{data['country']}"
    except Exception as e:
        return None

def load_or_create_private_key():
    """Loads or creates a new private key."""
    if not os.path.exists('private_key'):
        private_key = nacl.signing.SigningKey.generate()
        with open('private_key', "wb") as f:
            f.write(private_key.encode())
        with open('public_key', "wb") as f:
            f.write(private_key.verify_key.encode())
    else:
        with open('private_key', "rb") as f:
            private_key = nacl.signing.SigningKey(f.read())
    return private_key

def sign_message(user_country):
    """Sign the user-provided country with a timestamp."""
    private_key = load_or_create_private_key()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"Timestamp: {timestamp} | User Country: {user_country}".encode('utf-8')
    signed_message = private_key.sign(full_message)
    return signed_message

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_country = request.form['country']
        real_country = get_real_location()

        if real_country is None:
            flash('Could not retrieve real location. Please try again.', 'error')
            return redirect(url_for('index'))

        # Sign the user-provided country
        signed_message = sign_message(user_country)

        # Save the signed message
        with open('signed_message', "wb") as f:
            f.write(signed_message)

        # Check if the user is lying
        if real_country.strip().lower() != user_country.strip().lower():
            flash('You have entered a different country than your real location!', 'error')
        else:
            flash('Your location matches! Thank you for providing accurate information.', 'success')

        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/get_real_country', methods=['GET'])
def get_real_country():
    """Return the real country based on the user's IP."""
    real_country = get_real_location()
    if real_country:
        return jsonify({'real_country': real_country})
    else:
        return jsonify({'real_country': 'Could not detect location'}), 400

if __name__ == '__main__':
    app.run(debug=True)
