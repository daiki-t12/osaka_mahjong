class Tile:
    TILE_IMAGE_DIC = {}
    ALL_TILE = ['1m', '9m',
                '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
                '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
                '1z', '2z', '3z', '4z', '5z', '6z', '7z']

    def __init__(self):
        for tile in self.ALL_TILE:
            # if tile[1] == 'm':
            self.TILE_IMAGE_DIC[tile] = f'{tile}-6690-1.png'
            # elif tile[1] == 'p':
            #     self.TILE_IMAGE[tile] = 'pin' + tile[0] + '-66-90-l-emb.png'
            # elif tile[1] == 's':
            #     self.TILE_IMAGE[tile] = 'sou' + tile[0] + '-66-90-l-emb.png'
            # elif tile[1] == 'z':
            #     self.TILE_IMAGE[tile] = 'ji' + tile[0] + '-66-90-l-emb.png'

    def name_from_pic(self, pic):
        name = [name for name, png in self.TILE_IMAGE_DIC.items() if png == pic]
        return name[0]
