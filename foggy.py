import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolo12n.pt")


def dark_channel(im, size):
    b, g, r = cv2.split(im)
    min_channel = cv2.min(cv2.min(r, g), b)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    dark = cv2.erode(min_channel, kernel)
    return dark


def atmospheric_light(im, dark, percent):
    im_flat = im.reshape(im.shape[0] * im.shape[1], 3)
    dark_flat = dark.flatten()
    indices = dark_flat.argsort()[-int(im_flat.shape[0] * percent) :]
    atm_light = np.max(im_flat[indices], axis=0)
    return atm_light


def transmission(im, atmospheric_light, omega, size):
    im = im.astype(np.float64) / atmospheric_light
    transmission = 1 - omega * dark_channel(im, size)
    return transmission


def refine_transmission(transmission, im, size):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    transmission = cv2.morphologyEx(transmission, cv2.MORPH_CLOSE, kernel)
    return transmission


def recover_scene(im, transmission, atmospheric_light):
    transmission = np.maximum(transmission, 0.1)
    im = im.astype(np.float64)
    J = (im - atmospheric_light) / transmission[:, :, np.newaxis] + atmospheric_light
    J = np.clip(J, 0, 255)
    return J.astype(np.uint8)


# url = "http://192.168.0.106:8080/video"
def defog_webcam():
    cap = cv2.VideoCapture(0)
    # cap = "data/images/train/foggy-001.jpg"

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        omega = 0.95
        dark_channel_size = 15
        atmospheric_light_percent = 0.1
        transmission_refine_size = 3
        dark = dark_channel(frame, dark_channel_size)
        atm_light = atmospheric_light(frame, dark, atmospheric_light_percent)
        transmission_map = transmission(frame, atm_light, omega, dark_channel_size)
        transmission_map = refine_transmission(
            transmission_map, frame, transmission_refine_size
        )
        defogged_frame = recover_scene(frame, transmission_map, atm_light)

        cv2.imshow("Original", frame)
        cv2.imshow("Defogged", defogged_frame)
        # url = defogged_frame
        # results = model.predict(source=url, show=True, stream=True)
        # for r in results:
        #     boxes = r.boxes
        #     masks = r.masks
        #     probs = r.probs

        # print(results)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    defog_webcam()