"""
File: main.py
Author: Chuncheng Zhang
Date: 2024-06-19
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Animation as spot-light walking in the image.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-06-19 ------------------------
# Requirements and constants
import os
import cv2
import sys
import random
import contextlib
import numpy as np

from PIL import Image
from pathlib import Path

# %% ---- 2024-06-19 ------------------------
# Function and class

folder = Path(os.environ['OneDriveConsumer'], 'Pictures/DesktopPictures')
winname = 'Image'
img_width = 800


def get_image(filename: str = None):
    paths = list(folder.iterdir())
    random.shuffle(paths)

    path = None

    # Select the filename file
    with contextlib.suppress(Exception):
        path = [e for e in paths if e.name == filename][0]

    # Select file randomly
    if path is None:
        path = paths[0]

    print(f'Selected path: {path}')
    return path


def read_image(path: Path):
    img = Image.open(path).convert('RGB')
    width, height = img.size
    img_height = int(img_width / width * height)
    img = img.resize((img_width, img_height))
    return np.array(img)


class Plot_Option(object):
    light = 122
    x = 0
    y = 0
    r = int(img_width*0.1)

    def safe_options(self):
        self.light = int(min(max(0, self.light), 255))
        self.r = int(max(10, self.r))


# %% ---- 2024-06-19 ------------------------
# Play ground
if __name__ == "__main__":
    path = get_image(
        'Canal,_Giovanni_Antonio_Canal_-_Venice,_A_Regatta_on_the_Grand_Canal_-_National_Gallery_NG938.jpg')
    path = get_image(
        'fluid-flow-in-lauterbrunnen-wallpaper-for-3840x2160-hdtv-21-77.jpg')
    # path = get_image()
    mat = read_image(path)
    height, width, _ = mat.shape

    po = Plot_Option()

    cv2.namedWindow(winname)

    def mouse_callback(event, x, y, flags, parameters):
        po.x = x
        po.y = y

        # Click to change spot radius
        if event == 1:
            po.r += 10
        elif event == 2:
            po.r -= 10

        # Scroll to change light
        if event == 10:
            if flags > 0:
                po.light += 10
            elif flags < 0:
                po.light -= 10

    cv2.setMouseCallback(winname, mouse_callback)

    while True:
        po.safe_options()

        # ----------------------------------------
        # ---- Generate image matrix ----
        # RGB
        rgb = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
        # HLS
        hls = cv2.cvtColor(mat, cv2.COLOR_BGR2HLS)
        # HLS set L
        hls_l = cv2.cvtColor(mat, cv2.COLOR_BGR2HLS)
        hls_l_1 = cv2.cvtColor(mat, cv2.COLOR_BGR2HLS)
        hls_l_1[:, :, 2] = po.light
        hls_mask = cv2.circle(
            hls_l_1[:, :, 0]*0, (po.x, po.y), po.r, 255, -1)
        hls_l[:, :, 2][hls_mask > 0] = hls_l_1[:, :, 2][hls_mask > 0]

        # ----------------------------------------
        # ---- Generate image to display ----
        mat2x2 = np.zeros((height*2, width*2, 3), dtype=np.uint8)
        # Put RGB on WN
        mat2x2[:height, :width] = rgb
        # Put L on EN
        mat2x2[:height, width:] = cv2.cvtColor(
            hls[:, :, 1], cv2.COLOR_GRAY2RGB)
        # Put S on WS
        mat2x2[height:, :width] = cv2.cvtColor(
            hls[:, :, 2], cv2.COLOR_GRAY2RGB)
        # Adjust L on ES
        mat2x2[height:, width:] = cv2.cvtColor(hls_l, cv2.COLOR_HLS2RGB)

        cv2.imshow(winname, mat2x2)
        cv2.setWindowTitle(winname, f'Light: {po.light}')

        # ----------------------------------------
        # ---- Keyboard Control ----
        key_code = cv2.pollKey()
        if key_code > -1:
            char = chr(key_code)
            print(f'Char: {char}, code: {key_code}')

            # Quit on 'q' or '<esc>'
            if char == 'q' or key_code == 27:
                break

            # Increase spot radius on '+'
            if char in '+=':
                po.r += 10

            # Decrease spot radius on '-'
            if char in '-_':
                po.r -= 10

    cv2.destroyWindow(winname)
    print('Bye bye')
    sys.exit(0)


# %% ---- 2024-06-19 ------------------------
# Pending


# %% ---- 2024-06-19 ------------------------
# Pending
