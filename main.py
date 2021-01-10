from __future__ import division
import datetime
import hashlib
import time

from dateutil import rrule
from Crypto.Cipher import AES
import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm
import numpy as np
import sys


def int_overflow(val):
    if not -sys.maxsize - 1 <= val <= sys.maxsize:
        val = (val + (sys.maxsize + 1)) % (2 * (sys.maxsize + 1)) - sys.maxsize - 1
    return val


def rand():
    global next_int
    next_int = int_overflow(next_int * 1103515245 + 12345)
    return np.int_((next_int / 65536) % 32768)


def s_rand(seed):
    global next_int
    next_int = seed


def seed_iteration(seed):
    unite = int(time.mktime(seed.timetuple()))
    s_rand(unite)
    rand_1 = rand()
    rand_2 = rand()
    preKey = abs(rand_1 << 16) | rand_2

    hashing = hashlib.md5(str(preKey).encode('utf-8'))

    key = hashing.digest()
    cipher = AES.new(key, AES.MODE_CBC, saltHashing)

    tmp = cipher.decrypt(encrypted).hex()
    if tmp.startswith('ffd8ffe0'):
        data = bytes.fromhex(tmp)
        open('image.jpg', 'wb').write(data)

        print('\nKey is: ' + str(key.hex()))
        print('Encryption date is: ' + str(seed))
        print("Assembling time: {:.2f}s".format(time.time() - start_time))

        sys.exit()


if __name__ == '__main__':
    seed_min = datetime.datetime.strptime(str('2020-Nov-01 00:00:00'), '%Y-%b-%d %H:%M:%S')
    seed_max = datetime.datetime.strptime(str('2020-Dec-01 00:00:00'), '%Y-%b-%d %H:%M:%S')

    encrypted = open('./encrypted', 'rb').read()
    inputs = tqdm(rrule.rrule(rrule.SECONDLY, dtstart=seed_min, until=seed_max))

    start_time = time.time()
    saltHashing = hashlib.md5(b' ').digest()
    next_int = np.int_(1)
    Parallel(n_jobs=multiprocessing.cpu_count())(delayed(seed_iteration)(i) for i in inputs)
