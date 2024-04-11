from flask import Flask, request, jsonify
import subprocess
import threading

app = Flask(__name__)

# Add a global variable to track service status
is_service_busy = False

def run_inference_process(data):
    """Function to handle the long-running process in a separate thread."""
    global is_service_busy
    is_service_busy = True  # Mark the service as busy

    cmd = ['python', 'inference.py']
    param_keys = [
        'source_image', 'driven_audio', 'result_dir', 'size', 'preprocess', 'pose_style',
        'input_yaw', 'input_pitch', 'input_roll', 'ref_eyeblink', 'ref_pose'
    ]
    param_flags = [
        'half', "still"
    ]
    for key in param_keys:
        value = data.get(key)
        if value is not None:
            cmd += [f'--{key}', str(value)]
    for key in param_flags:
        value = data.get(key)
        if value is not None:
            cmd += [f'--{key}']

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Inference process failed: {str(e)}")
    finally:
        is_service_busy = False  # Reset service status once the process is complete

@app.route('/status', methods=['GET'])
def service_status():
    """Respond with the current service status."""
    return jsonify({"isBusy": is_service_busy})

@app.route('/avatar', methods=['POST'])
def create_avatar():
    if is_service_busy:
        return jsonify({"error": "Service is currently processing another request."}), 503
    
    data = request.json
    # Start the long-running process in a new thread
    threading.Thread(target=run_inference_process, args=(data,)).start()
    
    # Immediately respond to the client
    return jsonify({"message": "Inference process started"}), 202

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
