import os
import re
import cv2
import numpy as np
import multiprocessing as mp
from functools import partial


def getFileInfo(s):
    pat = r"(.+?)(\.png|\.jpg|\.jpeg)$"
    m = re.search(pat, s, re.IGNORECASE)
    if m is None:
        return m
    return m.groups()


def path_fix(path: str):
    if path[-1] != "/" or path[-1] != "\\":
        path += "\\"
    return path


def openImage(path):
    with open(path, 'rb') as file:
        content = file.read()
        image = cv2.imdecode(np.frombuffer(
            content, np.uint8), cv2.IMREAD_COLOR)
    return image


def mainFunc(images: list[str], source, dest, jpeg_quality, direction) -> None:
    for i in images:
        fileInfo = getFileInfo(i)
        if not fileInfo is None:
            filename = ''.join(fileInfo)
            image = openImage(source+filename)
            if direction == "diagonal":
                image = np.flip(image, axis=0)
                image = np.flip(image, axis=1)
            else:
                axis = 0 if direction == "vertical" else 1
                image = np.flip(image, axis=axis)
            cv2.imwrite(dest+filename, image,
                        [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])


if __name__ == "__main__":
    mp.freeze_support()
    source = input("Source folder: ")
    source = path_fix(source)
    images = os.listdir(source)
    dest = input("Target folder: ")
    dest = path_fix(dest)
    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)
    jpeg_quality = int(input(r"JPEG/JPG quality(0 - 100): "))
    while True:
        direction = input(
            "Flip direction(diagonal/vertical/horizontal): ").lower()
        if direction in ["diagonal", "vertical", "horizontal"]:
            break
        print("Please input a legal flip direction")

    process_count = mp.cpu_count()
    images_length = len(images)
    step = images_length // process_count
    task: list[list] = []
    if step == 0:
        task = [[i] for i in images]
    else:
        for i in range(process_count):
            start_index = i*step
            element = [images[j] for j in range(start_index, start_index+step)]
            task.append(element)

        start_index = start_index+step
        counter = 0
        for remain in range(start_index, images_length):
            task[counter].append(images[remain])
            counter += 1

    func = partial(mainFunc, source=source, dest=dest,
                   jpeg_quality=jpeg_quality, direction=direction)
    with mp.Pool(processes=process_count) as pool:
        pool.map(func, task)
