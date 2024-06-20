"""
File: image-spot-light.py
Author: Chuncheng Zhang
Date: 2024-06-19
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Spot-light walking on the image.
    Changes the light or saturation within the lighting area in real-time.

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
import numpy as np

from PIL import Image
from enum import Enum
from pathlib import Path

# %% ---- 2024-06-19 ------------------------
# Function and class

folder = Path(os.environ['OneDriveConsumer'], 'Pictures/DesktopPictures')
win_name = 'Image'
img_width = 800


def get_image(filename: str = None):
    paths = list(folder.iterdir())

    # Select the filename file as given name
    # If fail, select file randomly if path is still invalid
    try:
        path = [e for e in paths if e.name == filename][0]
    except Exception as e:
        random.shuffle(paths)
        path = paths[0]

    print(f'Selected path: {path}')
    return path


def read_image(path: Path):
    img = Image.open(path).convert('RGB')
    width, height = img.size
    img_height = int(img_width / width * height)
    img = img.resize((img_width, img_height))
    return np.array(img)


class Channel(Enum):
    lightness = 1
    saturation = 2
    illumination = 3


class Plot_Option(object):
    channel = Channel.lightness
    lightness = 122
    saturation = 255
    illumination = 100
    x = 0
    y = 0
    r = int(img_width*0.2)

    def safe_options(self):
        self.lightness = int(min(max(0, self.lightness), 255))
        self.saturation = int(min(max(0, self.saturation), 255))
        self.illumination = int(min(max(0, self.illumination), 255))
        self.r = int(max(10, self.r))


# %% ---- 2024-06-19 ------------------------
# Play ground
if __name__ == "__main__":
    path = get_image(
        'Canal,_Giovanni_Antonio_Canal_-_Venice,_A_Regatta_on_the_Grand_Canal_-_National_Gallery_NG938.jpg')

    # path = get_image(
    #     'fluid-flow-in-lauterbrunnen-wallpaper-for-3840x2160-hdtv-21-77.jpg')

    # path = get_image()

    mat = read_image(path)
    height, width, _ = mat.shape

    po = Plot_Option()

    cv2.namedWindow(win_name)

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
                if po.channel == Channel.lightness:
                    po.lightness += 10
                elif po.channel == Channel.saturation:
                    po.saturation += 10
                elif po.channel == Channel.illumination:
                    po.illumination += 10
            elif flags < 0:
                if po.channel == Channel.lightness:
                    po.lightness -= 10
                elif po.channel == Channel.saturation:
                    po.saturation -= 10
                elif po.channel == Channel.illumination:
                    po.illumination -= 10

    cv2.setMouseCallback(win_name, mouse_callback)

    while True:
        po.safe_options()

        # ----------------------------------------
        # ---- Generate image matrix ----
        # RGB
        rgb = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
        # HLS
        hls = cv2.cvtColor(mat, cv2.COLOR_BGR2HLS)
        # LUV
        luv = cv2.cvtColor(rgb, cv2.COLOR_RGB2LUV)
        # Mask
        spot_mask = cv2.circle(
            rgb[:, :, 0]*0, (po.x, po.y), po.r, 255, -1)

        if po.channel == Channel.lightness:
            foreground = hls.copy()
            foreground[:, :, 1] = po.lightness
            new_hls = hls.copy()
            new_hls[:, :, 1][
                spot_mask > 0] = foreground[:, :, 1][spot_mask > 0]
            new_rgb = cv2.cvtColor(new_hls, cv2.COLOR_HLS2RGB)

        elif po.channel == Channel.saturation:
            foreground = hls.copy()
            foreground[:, :, 2] = po.saturation
            new_hls = hls.copy()
            new_hls[:, :, 2][
                spot_mask > 0] = foreground[:, :, 2][spot_mask > 0]
            new_rgb = cv2.cvtColor(new_hls, cv2.COLOR_HLS2RGB)

        elif po.channel == Channel.illumination:
            foreground = luv.copy()
            foreground[:, :, 0] = po.illumination
            new_luv = luv.copy()
            new_luv[:, :, 0][
                spot_mask > 0] = foreground[:, :, 0][spot_mask > 0]
            new_rgb = cv2.cvtColor(new_luv, cv2.COLOR_LUV2RGB)

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
        mat2x2[height:, width:] = new_rgb

        cv2.imshow(win_name, mat2x2)

        if po.channel == Channel.lightness:
            cv2.setWindowTitle(win_name, f'{po.channel}: {po.lightness}')
        elif po.channel == Channel.saturation:
            cv2.setWindowTitle(win_name, f'{po.channel}: {po.saturation}')
        elif po.channel == Channel.illumination:
            cv2.setWindowTitle(win_name, f'{po.channel}: {po.illumination}')

        # ----------------------------------------
        # ---- Keyboard Control ----
        # > q or <esc>: quit
        # > + or =: increase value
        # > - or _: decrease value
        # > s: switch to saturation
        # > l: switch to light
        # > <tab>: switch between l and s
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

            # Switch mode to [l]light or [s]saturation
            if char in 's':
                po.channel = Channel.saturation
            elif char in 'l':
                po.channel = Channel.lightness
            elif char in 'i':
                po.channel = Channel.illumination

            # <tab> key
            # Switch mode between 'light' and 'saturation'
            if key_code == 9:
                if po.channel == Channel.lightness:
                    po.channel = Channel.saturation
                elif po.channel == Channel.saturation:
                    po.channel = Channel.illumination
                elif po.channel == Channel.illumination:
                    po.channel = Channel.lightness

    cv2.destroyWindow(win_name)
    print('Bye bye')
    sys.exit(0)


# %% ---- 2024-06-19 ------------------------
# Pending


# %% ---- 2024-06-19 ------------------------
# Pending
