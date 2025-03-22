from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run-voicebot', methods=['GET'])
def run_voicebot():
    try:
        # Run your voice bot script
        process = subprocess.Popen(["python3", "VoiceBot2.py"])
        return jsonify({"message": "VoiceBot activated", "status": "success"})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "error"})

# Ensure Flask runs when Fleek starts
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
