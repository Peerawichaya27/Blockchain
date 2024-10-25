from flask import Flask, request, jsonify
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import binascii

app = Flask(__name__)

# RSA Public Key
PUBLIC_KEY_PEM = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq1U2sopY+ktpsV/stESi
cL+G5eU0j9c4zOxyGUVUbM3N/69CfmMrjG9Y57Jpuq6QXYXvg+sPNOs71Wo7JdZt
oTTpk6z89hzg6ZgT0583oxEyPZNbh657YTLNuQJayPm2LTXmbVERa884eLO/Ifvp
seRLQSXkOu+9cYaT6gtmZprf+9mRlotejLxRJvZuiCcuwVlNssM1v/nvPdN5jS1j
GrwOGgXAQyouHbO9n1Sc5zJSeJrhFu7JCeIsvcCZQrUQqM5/hYPinbHsyKSDJ3ww
y8yVnfQ9xkG0bKL942QedmN7fUuyNtGWmC8Xp21dQqdgSlz7f5T+XKm/D2qoywyJ
kQIDAQAB
-----END PUBLIC KEY-----'''

PUBLIC_KEY = RSA.import_key(PUBLIC_KEY_PEM)

@app.route('/verify_signature', methods=['POST'])
def verify_signature():
    message = request.json.get('message')
    signature_hex = request.json.get('signature')

    if not message or not signature_hex:
        return jsonify({'error': 'Message and signature are required'}), 400

    try:
        signature = binascii.unhexlify(signature_hex)
    except binascii.Error:
        return jsonify({'error': 'Invalid signature format'}), 400

    # Hash the message
    h = SHA256.new(message.encode('utf-8'))

    try:
        # Verify the signature
        pkcs1_15.new(PUBLIC_KEY).verify(h, signature)
        return jsonify({
            'status': 'success',
            'message': 'Signature verified successfully'
        })
    except (ValueError, TypeError):
        return jsonify({
            'status': 'failed',
            'message': 'Signature verification failed'
        }), 400

if __name__ == '__main__':
    app.run(port=5001, debug=True)