import threading
import cv2
import imutils
import numpy as np

def get_webcams():
    from pygrabber.dshow_graph import FilterGraph

    devices = FilterGraph().get_input_devices()
    available_cameras = {}

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name

    return available_cameras

class webcam:
    def __init__(self):
        self.webcams = get_webcams()  # list of webcams
        self.selected_webcam = dict.fromkeys(self.webcams.keys())  # selected webcam number
        self.selected_webcam[0] = 'SELECTED'
        self.vs = None  # video stream
        self.outputFrame = None
        self.lock = threading.Lock()

        self.data = [] # measurement data
        self.i = 0
        self.n = 0
        self.normalize_value = 0
        self.first_Data = True

    def __del__(self):
        # release the video stream pointer
        if self.vs is not None:
            self.vs.release()
            self.vs = None
        cv2.destroyAllWindows()

    def manual_settings(self):
        if self.vs is not None:
            exp = self.vs.get(cv2.CAP_PROP_EXPOSURE)
            focus = self.vs.get(cv2.CAP_PROP_FOCUS)
            wb = self.vs.get(cv2.CAP_PROP_WB_TEMPERATURE)

            self.vs.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            self.vs.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            self.vs.set(cv2.CAP_PROP_AUTO_WB, 0)

            self.vs.set(cv2.CAP_PROP_EXPOSURE, exp)
            self.vs.set(cv2.CAP_PROP_FOCUS, focus)
            self.vs.set(cv2.CAP_PROP_WB_TEMPERATURE, wb)
            self.vs.set(cv2.CAP_PROP_BACKLIGHT, 0)

            return

    def auto_settings(self):
        if self.vs is not None:
            self.vs.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.vs.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            # self.vs.set(cv2.CAP_PROP_AUTO_WB, 1)
            return

    def select_webcam(self, index=0):
        if self.vs is not None:
            self.vs.release()
            self.vs = None

        with self.lock:
            self.outputFrame = None
        cv2.destroyAllWindows()

        self.selected_webcam = dict.fromkeys(self.webcams.keys())
        self.selected_webcam[index] = 'SELECTED'
        self.vs = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        self.auto_settings()
        return

    def get_frame(self):
        # loop over frames from the output stream
        # wait until the lock is acquired
        while True:
            with self.lock:
                if self.vs is None:
                    continue
                # check if the output frame is available, otherwise skip
                # the iteration of the loop
                if self.outputFrame is None:
                    continue
                # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", self.outputFrame)
                # ensure the frame was successfully encoded
                if not flag:
                    continue
                # yield the output frame in the byte format
            return bytearray(encodedImage)

    def process_frame(self, measure_masked=False):
        # loop over frames from the video stream
        while True:
            # read the next frame from the video stream, resize it,
            # convert the frame to grayscale, and blur it
            if self.vs is None:
                continue

            ret, frame = self.vs.read()

            if frame is None:
                continue

            self.n = self.n + 1
            if self.n % 1 == 0:
                self.i = self.i + 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if measure_masked:
                    center = [int(n / 2) for n in reversed(np.shape(gray))]
                    radius = int(np.min(center) * 0.75)
                    offset = (np.min(center) - radius)
                    center[1] = int(center[1] + offset)
                    center = tuple(center)

                    mask = np.zeros(gray.shape[:2], dtype="uint8")
                    cv2.circle(mask, center, radius, 255, -1)

                    masked = cv2.bitwise_and(gray, gray, mask=mask)
                    gray = masked

                tot_value, _, _, _ = cv2.sumElems(gray)

                if self.first_Data and tot_value != 0:
                    self.normalize_value = tot_value
                    self.first_Data = False
                if self.normalize_value != 0 and self.first_Data is False:
                    tot_value = tot_value / self.normalize_value

                self.data.append((self.i, tot_value))

            frame = imutils.resize(frame, width=720)

            # update the total number of frames read thus far
            # total += 1
            # acquire the lock, set the output frame, and release the
            # lock
            with self.lock:
                self.outputFrame = frame.copy()

    def reset_data(self):
        self.data = []
        self.i = 0
        self.n = 0
        self.normalize_value = 0
        self.first_Data = True
        return

