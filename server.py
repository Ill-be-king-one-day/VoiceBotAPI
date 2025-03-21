from flask import Flask, request, send_file
import subprocess
import time
import os

app = Flask(__name__)

@app.route('/run-voicebot', methods=['GET'])
def run_voicebot():
    try:
        # Start the voice bot script and generate an MP3
        process = subprocess.Popen(["python3", "your_voicebot_script.py"])
        time.sleep(3)  # Give it time to generate the response.mp3

        # Ensure the MP3 file exists
        file_path = "response.mp3"
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return {"message": "MP3 file not found", "status": "error"}
    
    except Exception as e:
        return {"message": f"Error: {str(e)}", "status": "error"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
