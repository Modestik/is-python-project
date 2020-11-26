import math

from PIL import Image

import myimagehash
import image_slicer
from stegano import lsb


def hamming_distance(string1, string2):
    distance = 0
    length = len(string1)
    for i in range(length):
        if string1[i] != string2[i]:
            distance += 1
    return distance


def main_function(original_image_filename, deformed_image_filename):
    original_image = Image.open(original_image_filename)
    deformed_image = Image.open(deformed_image_filename)
    # расчет количества блоков
    n = 64
    width, height = original_image.size
    col = math.ceil(width / n)
    row = math.ceil(height / n)

    # пороговая величина
    hash_length = 64
    threshold = hash_length * 0.1

    # разбитие изображений на блоки
    orig_img_tiles = image_slicer.slice(original_image_filename, col=col, row=row, save=False)
    deform_img_tiles = image_slicer.slice(deformed_image_filename, col=col, row=row, save=False)

    for orig_block, deform_block in zip(orig_img_tiles, deform_img_tiles):
        # getting block hash
        orig_hash = myimagehash.phash_simple(orig_block.image)
        deform_hash = myimagehash.phash_simple(deform_block.image)

        # hide a message(hash) in images with the LSB
        orig_block.image = lsb.hide(orig_block.image, str(orig_hash))
        deform_block.image = lsb.hide(deform_block.image, str(deform_hash))

        # Find a message(hash) in images with the LSB
        decoded_orig_hash = lsb.reveal(orig_block.image.copy())
        decoded_deform_hash = lsb.reveal(deform_block.image.copy())

        if hamming_distance(decoded_orig_hash, decoded_deform_hash) > threshold:
            deform_block.image = deform_block.image.convert("L")

    result_image = image_slicer.join(deform_img_tiles, width, height)
    result_image.save("./images/result.png")

    original_image.show()
    deformed_image.show()
    result_image.show()


if __name__ == '__main__':
    original_image_path = "./images/original_racoon.jpg"
    deformed_image_path = "./images/deformed_racoon.jpg"
    # original_image_path = "./images/original_squirrel.jpg"
    # deformed_image_path = "./images/deformed_squirrel.jpg"
    main_function(original_image_path, deformed_image_path)
