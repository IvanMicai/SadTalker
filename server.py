from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Global variable to track service status
is_service_busy = False


@app.route('/status', methods=['GET'])
def service_status():
    """Respond with the current service status."""
    global is_service_busy
    return jsonify({"isBusy": is_service_busy})

@app.route('/avatar', methods=['POST'])
def create_avatar():
    if request.method == 'POST':
        global is_service_busy

        if is_service_busy:
            # Early response if the service is busy
            return jsonify({"error": "Service is currently processing another request."}), 503
        is_service_busy = True  # Mark service as busy before starting the process
    

        # Extracting body data
        data = request.json
        
        # Base command
        cmd = ['python', 'inference.py']
        
        # Parameters that should be included only if they are provided
        param_keys = [
            'source_image', 'size', 'driven_audio', 'result_dir', 'preprocess', 'pose_style',
            'input_yaw', 'input_pitch', 'input_roll', 
            'ref_eyeblink', 'ref_pose'
        ]
        
        # Building the command by iterating over the parameters
        for key in param_keys:
            value = data.get(key)
            if value is not None:  # This checks if the parameter exists
                print(key, value)
                cmd += [f'--{key}', str(value)]
        
        # Execute the command
        try:
            subprocess.run(cmd, check=True)
            is_service_busy = False

            # Respond with status 200
            return jsonify({"message": "Inference process started successfully"}), 200
        except subprocess.CalledProcessError as e:
            is_service_busy = False
            # Handle errors in the subprocess
            return jsonify({"error": "Inference process failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
