from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Minimal Flask app works'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test route works'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)