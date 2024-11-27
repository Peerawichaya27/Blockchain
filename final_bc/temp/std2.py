from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
from datetime import datetime, timedelta
import requests
import hashlib

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <h1>Home Page</h1>
        <form action="/config">
            <button type="submit">Go to Config</button>
        </form>
    '''
# Function to get current date + 2 days and format it correctly
def get_expiration_time():
    current_time = datetime.now() + timedelta(days=2)
    formatted_time = int(current_time.timestamp())  # Return as UNIX timestamp
    return formatted_time

@app.route('/config', methods=['GET'])
def config_aci():
    # Serve the ACL configuration UI to the student
    return render_template('acl_config.html')  # The form HTML code provided above

# Route to update ACL and register transcript
@app.route('/update-acl', methods=['POST'])
def update_acl():
    # Load the current acl.json file
    with open('acl.json', 'r') as file:
        acl_data = json.load(file)

    # Get the form data (selected fields and employer details)
    selected_fields = request.form.getlist('fields')
    employer_email = request.form.get('employer_email')

    # Find the student entry to update (assuming student_did is "did:university:student1" for now)
    student_did = "did:university:student1"  # Replace with dynamic handling as needed
    student_acl = next((student for student in acl_data["students"] if student["student_did"] == student_did), None)

    if not student_acl:
        return jsonify({"error": "Student not found in ACL"}), 404

    # Update the ACL for the student
    student_acl["selective_disclosure"] = selected_fields
    student_acl["employer_hashed_email"] = hashlib.sha256(employer_email.encode()).hexdigest()
    student_acl["expiration"] = get_expiration_time()

    # Save the updated acl.json file
    with open('acl.json', 'w') as file:
        json.dump(acl_data, file, indent=4)

    # Trigger the /register-transcript endpoint from uni.py
    register_response = requests.get('http://192.168.1.154:5000/register-transcript')

    # If the transcript registration was successful, generate the QR code
    if register_response.status_code == 200:
        # Now trigger the /generate-token endpoint from uni.py
        generate_response = requests.get('http://192.168.1.154:5000/generate-token')
        if generate_response.status_code == 200:
            qr_code_url = generate_response.json().get("credentials_url")
            return render_template('qr_code.html', qr_code_url=qr_code_url)

    # If something went wrong
    return jsonify({"message": "Error in registration or token generation"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)  # Replace with your actual local IP