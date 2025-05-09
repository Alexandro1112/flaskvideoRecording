from flask import Flask, render_template, jsonify
import threading
import AVFoundation

app = Flask(__name__)
recording_thread = None
is_recording = False

class VideoRecorder:
    def __init__(self):
        self.session = AVFoundation.AVCaptureSession.alloc().init()
        self.video_output = AVFoundation.AVCaptureMovieFileOutput.alloc().init()
        self.session.addOutput_(self.video_output)

        devices = AVFoundation.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
            [AVFoundation.AVCaptureDeviceTypeBuiltInWideAngleCamera],
            'video',
            1
        ).devices()

        if devices:
            self.device = devices[0]
            input_device, err = AVFoundation.AVCaptureDeviceInput.deviceInputWithDevice_error_(self.device, None)
            self.session.addInput_(input_device)

    def start_recording(self, filename):
        self.is_recording = True
        self.session.startRunning()
        output_url = AVFoundation.NSURL.fileURLWithPath_(f"recordings/{filename}")
        self.video_output.startRecordingToOutputFileURL_recordingDelegate_(output_url, self)

    def stop_recording(self):
        print('Closing recording')
        self.video_output.stopRecording()
        self.session.stopRunning()
        return

recorder = VideoRecorder()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_recording():
    global recording_thread
    if not is_recording:
        filename = "video.mov"
        recording_thread = threading.Thread(target=recorder.start_recording, args=(filename,))
        recording_thread.start()
        return jsonify({"status": "Recording started"})
    return jsonify({"status": "Already recording"})

@app.route('/stop', methods=['POST'])
def stop_recording():

    recorder.stop_recording()
    return jsonify({"status": "Recording stopped"})

if __name__ == '__main__':
    app.run(debug=True)