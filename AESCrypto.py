import os

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


def get_key_pbkdf2(key):
    salt = os.urandom(8)  # 64-bit salt
    return PBKDF2(key, salt, 32)  # 256-bit key


def encrypt_image(message, key):
    message += b"\0" * (AES.block_size - len(message) % AES.block_size)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)


def decrypt_image(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")


##########
def encrypt_image_and_save(file_name, key):
    with open(file_name, 'rb') as fo:
        plaintext = fo.read()
    enc = encrypt(plaintext, key)
    with open(file_name + ".enc", 'wb') as fo:
        fo.write(enc)


def decrypt_image_and_save(self, file_name, key):
    with open(file_name, 'rb') as fo:
        ciphertext = fo.read()
    dec = self.decrypt(ciphertext, key)
    with open(file_name + "decr", 'wb') as fo:
        fo.write(dec)


def clear(self):
    lambda: os.system('cls')
