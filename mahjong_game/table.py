import random


class Table:
    def __init__(self):
        self.wall = list(['1m', '1m', '1m', '1m', '9m', '9m', '9m', '9m', '1p', '1p', '1p', '1p', '2p', '2p', '2p', '2p', '3p', '3p', '3p', '3p', '4p', '4p', '4p', '4p', '5p', '5p', '5p', '5p', '6p', '6p', '6p', '6p', '7p', '7p', '7p', '7p', '8p', '8p', '8p', '8p', '9p', '9p', '9p', '9p', '1s', '1s', '1s', '1s', '2s', '2s', '2s', '2s', '3s', '3s', '3s', '3s', '4s', '4s', '4s', '4s', '5s', '5s', '5s', '5s', '6s', '6s', '6s', '6s', '7s', '7s', '7s', '7s', '8s', '8s', '8s', '8s', '9s', '9s', '9s', '9s', '1z', '1z', '1z', '1z', '2z', '2z', '2z', '2z', '3z', '3z', '3z', '3z', '4z', '4z', '4z', '4z', '5z', '5z', '5z', '5z', '6z', '6z', '6z', '6z', '7z', '7z', '7z', '7z'])
        random.shuffle(self.wall)


"""
import random

class Pai:
    MANZU = [f'{i}m' for i in '123456789']
    SOUZU = [f'{i}s' for i in '123456789']
    PINZU = [f'{i}p' for i in '123456789']
    ZIHAI = [f'{i}z' for i in '1234567']
    ALL = 4 * tuple(MANZU + SOUZU + PINZU + ZIHAI)

    def order(pai):
         number, kind = pai
         return 'mpsz'.index(kind), number

def riipai(tehai):
    return sorted(tehai, key=Pai.order)

yama = list(Pai.ALL)
random.shuffle(yama)
tehai = yama[:13]
print(tehai)
tehai = riipai(tehai)
print(tehai)
"""