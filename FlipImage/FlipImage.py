import os
import re
import cv2
import numpy as np
import multiprocessing as mp
from functools import partial


def get_file_info(s):
    pat = r"(.+?)(\.png|\.jpg|\.jpeg)$"
    m = re.search(pat, s, re.IGNORECASE)
    if m is None:
        return m
    return m.groups()


def path_fix(path: str):
    for i in range(len(path)):
        if path[i].isalpha():
            break
    path = path[i:].strip("\"")
    if path[-1] == "'":
        path = path[:-1]
    return os.path.normpath(path)+"\\"


def open_image(path):
    with open(path, 'rb') as file:
        content = file.read()
        image = cv2.imdecode(np.frombuffer(
            content, np.uint8), cv2.IMREAD_COLOR)
    return image


def save_image(folder_name, filename, extension, image, jpeg_quality) -> None:
    ret, image = cv2.imencode(
        extension, image, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
    path = folder_name + filename + extension
    if not ret:
        print(path, "->", ret)
    image.tofile(path)


def main_func(images: list[str], source, dest, jpeg_quality, direction) -> None:
    for i in images:
        fileInfo = get_file_info(i)
        if not fileInfo is None:
            extension = fileInfo[1]
            filename = fileInfo[0]
            image = open_image(source+filename+extension)
            if direction == "diagonal":
                image = np.flip(image, axis=0)
                image = np.flip(image, axis=1)
            else:
                axis = 0 if direction == "vertical" else 1
                image = np.flip(image, axis=axis)
            save_image(dest, filename, extension, image, jpeg_quality)


def get_folder_name(folder_type: str):
    folder = ""
    while True:
        folder = path_fix(input("{0} folder: ".format(folder_type)))
        if not os.path.exists(folder):
            print("Notice: \"" + folder + "\"", "does not exist, try again.")
            continue
        break
    return folder


if __name__ == "__main__":
    mp.freeze_support()
    source = get_folder_name("Source")
    images = os.listdir(source)
    dest = get_folder_name("Target")
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

    func = partial(main_func, source=source, dest=dest,
                   jpeg_quality=jpeg_quality, direction=direction)
    with mp.Pool(processes=process_count) as pool:
        pool.map(func, task)

    print("\nDone.")
    input()
