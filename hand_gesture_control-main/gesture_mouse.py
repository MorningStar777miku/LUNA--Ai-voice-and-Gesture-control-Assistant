import sys
if "--start-luna" in sys.argv:
    from setup import run_setup
    run_setup()
import cv2
import time
import math
import numpy as np
import HandTrackingModule as htm
import pyautogui, autopy
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize webcam and constants
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Detector for hand tracking
detector = htm.handDetector(maxHands=1, detectionCon=0.85, trackCon=0.8)

# Audio volume control setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = -63
maxVol = volRange[1]

# Hand gesture detection setup
hmin = 50
hmax = 200
volBar = 400
volPer = 0
vol = 0
color = (0, 215, 255)
tipIds = [4, 8, 12, 16, 20]
mode = ''
active = 0

# Click state flags and timing
left_click_active = False
right_click_active = False
last_left_click_time = 0
double_click_time_limit = 0.3  # Time in seconds to detect double click

pyautogui.FAILSAFE = False

def putText(mode, loc=(250, 450), color=(0, 255, 255)):
    cv2.putText(img, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, color, 3)

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture image.")
        break

    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    fingers = []
    if len(lmList) != 0:
        # Thumb
        fingers.append(int(lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]))
        # Other fingers
        for id in range(1, 5):
            fingers.append(int(lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]))

        if fingers == [1, 1, 1, 1, 0]:
            putText('Minimize', loc=(250, 100), color=(255, 0, 255))
            pyautogui.hotkey('win', 'down')
            time.sleep(0.5)
        if fingers == [1, 1, 1, 0, 1]:
            putText('Maximize', loc=(250, 100), color=(0, 255, 255))
            pyautogui.hotkey('win', 'up')
            time.sleep(0.5)

        if (fingers == [0, 0, 0, 0, 0]) and (active == 0):
            mode = 'N'
        elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) and (active == 0):
            mode = 'Scroll'
            active = 1
        elif (fingers == [1, 1, 0, 0, 0]) and (active == 0):
            mode = 'Volume'
            active = 1
        elif (fingers == [1, 1, 1, 1, 1]) and (active == 0):
            mode = 'Cursor'
            active = 1

    if mode == 'Scroll':
        active = 1
        putText(mode)
        cv2.rectangle(img, (200, 410), (245, 460), (255, 255, 255), cv2.FILLED)

        if len(lmList) != 0:
            if fingers == [0, 1, 0, 0, 0]:
                putText(mode='U', loc=(200, 455), color=(0, 255, 0))
                pyautogui.scroll(300)
            if fingers == [0, 1, 1, 0, 0]:
                putText(mode='D', loc=(200, 455), color=(0, 0, 255))
                pyautogui.scroll(-300)
            elif fingers == [0, 0, 0, 0, 0]:
                active = 0
                mode = 'N'

    if mode == 'Volume':
        active = 1
        putText(mode)

        if len(lmList) != 0:
            if fingers[-1] == 1:
                active = 0
                mode = 'N'
            else:
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), color, 3)
                cv2.circle(img, (cx, cy), 8, color, cv2.FILLED)

                length = math.hypot(x2 - x1, y2 - y1)
                vol = np.interp(length, [hmin, hmax], [minVol, maxVol])
                volBar = np.interp(vol, [minVol, maxVol], [400, 150])
                volPer = np.interp(vol, [minVol, maxVol], [0, 100])
                volume.SetMasterVolumeLevel(vol, None)

                if length < 50:
                    cv2.circle(img, (cx, cy), 11, (0, 0, 255), cv2.FILLED)

                cv2.rectangle(img, (30, 150), (55, 400), (209, 206, 0), 3)
                cv2.rectangle(img, (30, int(volBar)), (55, 400), (215, 255, 127), cv2.FILLED)
                cv2.putText(img, f'{int(volPer)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (209, 206, 0), 3)

    if mode == 'Cursor':
        active = 1
        putText(mode)
        cv2.rectangle(img, (110, 20), (630, 400), (255, 255, 255), 1)

        if fingers[1:] == [0,0,0,0]: # thumb excluded
            active = 0
            mode = 'N'
            print(mode)
        else:
            if len(lmList) != 0:
                x1, y1 = lmList[8][1], lmList[8][2]
                w, h = autopy.screen.size()
                X = int(np.interp(x1, [110, 620], [0, w - 1]))
                Y = int(np.interp(y1, [20, 350], [0, h - 1]))
                cv2.circle(img, (lmList[8][1], lmList[8][2]), 7, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 255, 0), cv2.FILLED)  # thumb

                if X % 2 != 0:
                    X = X - X % 2
                if Y % 2 != 0:
                    Y = Y - Y % 2
                print(X, Y)
                autopy.mouse.move(X, Y)

                # ---- Gesture Distance Calculations ----
                middle_ring_dist = math.hypot(lmList[12][1] - lmList[16][1], lmList[12][2] - lmList[16][2])
                index_tip = lmList[8]
                middle_tip = lmList[12]
                index_middle_dist = math.hypot(index_tip[1] - middle_tip[1], index_tip[2] - middle_tip[2])

                # ---- Left Click & Double Click: Only thumb down ----
                if fingers == [0, 1, 1, 1, 1]:
                    current_time = time.time()
                    if not left_click_active:
                        if current_time - last_left_click_time < double_click_time_limit:
                            pyautogui.doubleClick()
                        else:
                            pyautogui.click(button='left')
                        last_left_click_time = current_time
                        left_click_active = True
                        cv2.circle(img, (lmList[8][1], lmList[8][2]), 15, (0, 255, 0), cv2.FILLED)
                else:
                    left_click_active = False

                # ---- Right Click: Index + Middle fingers joined, palm open ----
                if fingers == [1, 1, 0, 0, 0] and index_middle_dist < 30:  # index and middle joined
                    if not right_click_active:
                        pyautogui.click(button='right')
                        right_click_active = True
                        cv2.circle(img, (lmList[8][1], lmList[8][2]), 15, (0, 0, 255), cv2.FILLED)  # index
                        cv2.circle(img, (lmList[12][1], lmList[12][2]), 15, (0, 0, 255), cv2.FILLED)  # middle
                else:
                    right_click_active = False

    cTime = time.time()
    fps = 1 / ((cTime + 0.01) - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
    cv2.imshow('Hand LiveFeed', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
