import io
import sys

from PIL import Image, ImageDraw

import AESCrypto
import utils


def expand_image(small_image):
    factor = 2
    # small_image.show()
    px = small_image.load()

    img = Image.new('RGB', (width * factor + 2, height * factor + 2), 'Black')
    pixels = img.load()
    for i in range(width):
        for j in range(height):
            pixels[factor * i, factor * j] = px[i, j]
            pixels[factor * i + 1, factor * j] = px[i, j]
            pixels[factor * i + 2, factor * j] = px[i, j]

            pixels[factor * i, factor * j + 1] = px[i, j]
            pixels[factor * i + 1, factor * j + 1] = px[i, j]
            pixels[factor * i + 2, factor * j + 1] = px[i, j]

            pixels[factor * i, factor * j + 2] = px[i, j]
            pixels[factor * i + 1, factor * j + 2] = px[i, j]
            pixels[factor * i + 2, factor * j + 2] = px[i, j]
    img = img.crop((0, 0, fragment_width, fragment_height))
    img.show()
    img.save("expand_image.jpg", "JPEG")
    return img


def steganography_process(encrypted_fragment):
    conv = image.convert("RGBA").getdata()
    max_size = width * height * 3.0 / 8 / 1024

    v = utils.decompose(encrypted_fragment)
    while len(v) % 3:
        v.append(0)

    payload_size = len(v) / 8 / 1024.0
    print("Encrypted payload size: %.3f KB " % payload_size)
    print("Max payload size: %.3f KB " % max_size)
    print("Коэффициент эффективного использования: %.3f " % float(
        100 * fragment_height * fragment_width / (width * height)))
    if payload_size > max_size - 4:
        print("Cannot embed. File too large")
        sys.exit()

    steg_image = Image.new('RGBA', (width, height))
    data_img = steg_image.getdata()

    idx = 0
    for h in range(height):
        for w in range(width):
            (r, g, b, a) = conv.getpixel((w, h))
            if idx < len(v):
                r = utils.set_bit(r, 0, v[idx])
                g = utils.set_bit(g, 0, v[idx + 1])
                b = utils.set_bit(b, 0, v[idx + 2])
            data_img.putpixel((w, h), (r, g, b, a))
            idx = idx + 3

    steg_image.save("images/steg_image.png", "PNG")
    return steg_image


def get_image_from_buffer(decrypted_fragment):
    image_stream = io.BytesIO(decrypted_fragment)
    final_image = Image.open(image_stream)
    final_image.show()

    final_image = expand_image(final_image)

    x_start = int((width - fragment_width) / 2)
    y_start = int((height - fragment_height) / 2)

    image.show()
    image_copy = image.copy()
    position = (x_start, y_start)
    image_copy.paste(final_image, position)
    image_copy.save('pasted_image.jpg')
    image_copy.show()

    return final_image


def get_encrypted_data(crypto_key, fragment_image):
    buf = io.BytesIO()
    fragment_image.save(buf, format='JPEG')
    byte_im = buf.getvalue()

    encrypt_fragment = AESCrypto.encrypt_image(byte_im, crypto_key)

    # сохраняем зашифрованное изображение
    with open("encrypt_image.enc", 'wb') as fo:
        fo.write(encrypt_fragment)

    return encrypt_fragment


def get_decrypted_data(cryptographic_key, extracting_data):
    decrypted_fragment = AESCrypto.decrypt_image(extracting_data, cryptographic_key)
    # сохраняем дешифрованное изображение
    with open("decrypt_image.dec", 'wb') as fo:
        fo.write(decrypted_fragment)

    return decrypted_fragment


def get_fragment_image():
    #  Шаг 1: выбор фрагмента
    # координаты на оригинальном изображении
    x_start = int((width - fragment_width) / 2)
    y_start = int((height - fragment_height) / 2)
    x_stop = x_start + fragment_width
    y_stop = y_start + fragment_height

    # достаем фрагмент
    fragment_image = image.crop((x_start, y_start, x_stop, y_stop))
    fragment_image.show()

    # Шаг 2: искажение объекта
    draw = ImageDraw.Draw(image)
    for x in range(x_start, x_stop):
        for y in range(y_start, y_stop):
            draw.point((x, y), (0, 0, 0))
    image.show()

    # Шаг 3: сжатие объекта
    max_size = (fragment_width / 2, fragment_height / 2)
    fragment_image.thumbnail(max_size, Image.ANTIALIAS)
    fragment_image.show()
    # fragment_image.save("thumbnail_image.jpg", "JPEG")

    return fragment_image


def main_function():

    compressed_fragment = get_fragment_image()

    key_pbkdf2 = AESCrypto.get_key_pbkdf2(key)

    encrypted_fragment = get_encrypted_data(key_pbkdf2, compressed_fragment)

    steg_image = steganography_process(encrypted_fragment)
    extracting_data = utils.extract(steg_image)
    # дешифруем
    decrypted_fragment = get_decrypted_data(key_pbkdf2, extracting_data)
    # получаем картинку из дешифрованного фрагмента
    decrypted_image = get_image_from_buffer(decrypted_fragment)
    decrypted_image.show()


if __name__ == '__main__':
    # оригинальное изображение
    image_path = "./images/original_squirrel.jpg"
    image = Image.open(image_path)
    image.show()
    # криптографический ключ
    key = "p@$$w0rd"

    # рассчет размера фрагмента
    width, height = image.size
    d = 4  # делитель
    fragment_width = int(width / d)
    fragment_height = int(height / d)

    # Основная часть
    main_function()
