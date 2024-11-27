from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
from datetime import datetime, timedelta
import requests

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
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S+07:00')  # Adjust for +07:00 timezone
    return formatted_time

@app.route('/config', methods=['GET'])
def config_aci():
    # Serve the ACL configuration UI to the student
    return render_template('acl_config.html')  # The form HTML code provided above

# Route to update ACL and register transcript
@app.route('/update-acl', methods=['POST'])
def update_acl():
    # Load the current data.json file
    with open('data.json', 'r') as file:
        data = json.load(file)

    # Get the form data (selected fields and employer details)
    selected_fields = request.form.getlist('fields')
    employer_email = request.form.get('employer_email')
    employer_attribute = request.form.get('employer_attribute')

    # Update the ACL in the data.json file
    data['acl']['selective_disclosure'] = selected_fields
    data['acl']['email'] = employer_email
    data['employer_attribute'] = employer_attribute

    # Get the current date + 2 days as expiration time and update it in the ACL
    new_expiration_time = get_expiration_time()
    data['acl']['expiration_time'] = new_expiration_time

    # Save the updated data.json file
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

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