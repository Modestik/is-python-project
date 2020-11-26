from __future__ import (absolute_import, division, print_function)

from PIL import Image
import numpy


def _binary_array_to_hex(arr):
    bit_string = ''.join(str(b) for b in 1 * arr.flatten())
    return bit_string


class ImageHash(object):

    def __init__(self, binary_array):
        self.hash = binary_array

    def __str__(self):
        return _binary_array_to_hex(self.hash.flatten())


def phash_simple(image, hash_size=8, highfreq_factor=4):

    import scipy.fftpack
    img_size = hash_size * highfreq_factor
    image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)
    pixels = numpy.asarray(image)
    dct = scipy.fftpack.dct(pixels)
    dctlowfreq = dct[:hash_size, 1:hash_size + 1]
    avg = dctlowfreq.mean()
    diff = dctlowfreq > avg
    return ImageHash(diff)
