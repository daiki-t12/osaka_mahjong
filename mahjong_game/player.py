import copy
#シャンテン数
from mahjong.shanten import Shanten
#計算
from mahjong.hand_calculating.hand import HandCalculator
#麻雀牌
from mahjong.tile import TilesConverter
#役, オプションルール
from mahjong.hand_calculating.hand_config import HandConfig
#鳴き
#風(場&自)
from mahjong.constants import EAST, SOUTH


class Player:

    PRIORITY = ('1m', '9m', '3z', '2z', '1z', '4z', '5z', '6z', '7z',
                '1s', '9s', '9p', '1p', '2p', '8p', '8s', '2s',
                '3s', '7s', '7p', '3p', '4p', '6p', '6s', '4s', '5s', '5p')

    def __init__(self):
        # self.hand = self.get_hand(wall)
        # self.sort_hand()
        self.hand = []
        self.river = []

    def get_hand(self, wall):
        self.hand = wall[0:13]
        del wall[0:13]
        return self.hand

    def sort_hand(self):
        self.hand = sorted(self.hand)
        manzu = [s for s in self.hand if 'm' in s]
        pinzu = [s for s in self.hand if 'p' in s]
        souzu = [s for s in self.hand if 's' in s]
        zihai = [s for s in self.hand if 'z' in s]
        self.hand = manzu + pinzu + souzu + zihai

    def draw(self, wall):
        hai = wall[0]
        del wall[0]
        self.hand.append(hai)
        return hai

    def discard(self):
        """
        tehai14 = copy.copy(self.hand)
        shanten = Shanten()
        sutehai_kouho = tehai14[0]
        tehai14.remove(sutehai_kouho)
        shan = shanten.calculate_shanten(TilesConverter.one_line_string_to_136_array(''.join(tehai14)))

        for kouho in self.hand:
            tehai_kouho = copy.copy(self.hand)
            tehai_kouho.remove(kouho)
            shanten_number = shanten.calculate_shanten(TilesConverter.one_line_string_to_136_array(''.join(tehai_kouho)))
            if shan > shanten_number:
                sutehai_kouho = kouho
                shan = shanten_number
            elif shan == shanten_number:
                if Player.PRIORITY.index(sutehai_kouho) > Player.PRIORITY.index(kouho):
                    sutehai_kouho = kouho
"""
        self.sort_hand()
        tehai14 = copy.copy(self.hand)
        shanten = Shanten()
        map = {}
        sutehai_kouho = ''
        shan = 10
        for kouho in tehai14:
            tehai_kouho = copy.copy(self.hand)
            tehai_kouho.remove(kouho)
            shanten_number = \
                shanten.calculate_shanten(TilesConverter.one_line_string_to_34_array(''.join(tehai_kouho)))
            map[kouho] = shanten_number
            if shan > shanten_number:
                sutehai_kouho = kouho
                shan = shanten_number
            elif shan == shanten_number:
                if Player.PRIORITY.index(sutehai_kouho) > Player.PRIORITY.index(kouho):
                    sutehai_kouho = kouho

        self.hand.remove(sutehai_kouho)
        self.river.append(sutehai_kouho)
        return sutehai_kouho

    def calculate_shanten_number(self):
        shanten = Shanten()
        shanten_number = shanten.calculate_shanten(TilesConverter.one_line_string_to_34_array(''.join(self.hand)))
        return shanten_number

    def calculate_score(self, win_tile_string, wall, is_tsumo):

        # 結果出力用
        def _print_hand_result(hand_result):
            # 翻数, 符数
            print(str(hand_result.fu) + '符' + ' ' + str(hand_result.han) + '飜')
            # 点数(ツモアガリの場合[左：親失点, 右:子失点], ロンアガリの場合[左:放銃者失点, 右:0])
            print(hand_result.cost['main'], result.cost['additional'])
            # 役
            print(hand_result.yaku)
            #符数の詳細
            for fu_item in hand_result.fu_details:
                print(fu_item)
            print('')

        # agari = self.tehai.append(win_tile)
        if not is_tsumo:
            self.hand.append(win_tile_string)

        self.sort_hand()
        tiles = TilesConverter.one_line_string_to_136_array(''.join(self.hand))

        win_tile = TilesConverter.one_line_string_to_136_array(win_tile_string)[0]

        # 鳴き
        melds = None

        # ドラ
        dora_indicators = [
            TilesConverter.one_line_string_to_136_array(wall[-6])[0],
            TilesConverter.one_line_string_to_136_array(wall[-5])[0],
        ]

        # オプション(リーチ, 自風, 場風)
        config = HandConfig(is_tsumo=is_tsumo, is_riichi=True, player_wind=SOUTH, round_wind=EAST)

        # 計算
        calculator = HandCalculator()
        result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
        # print(self.hand)
        # _print_hand_result(result)
        return result

    def ron(self, num, wall, discarded_tile):
        if self.calculate_shanten_number() == 0:
            hand_copy = copy.copy(self.hand)
            hand_copy.append(discarded_tile)
            shanten = Shanten()
            if -1 == shanten.calculate_shanten(TilesConverter.one_line_string_to_34_array(''.join(hand_copy))):
                print('雀士' + str(num) + '：栄和')
                self.sort_hand()
                print(self.hand)
                self.calculate_score(win_tile_string=discarded_tile, wall=wall, is_tsumo=False)
                return True

    def act(self, num, wall):
        drawn_tile = self.draw(wall)
        # print(player.tehai)
        print('ツモ ' + drawn_tile)
        if self.calculate_shanten_number() == -1:
            print('雀士' + str(num) + '：自摸和')
            self.calculate_score(win_tile_string=drawn_tile, wall=wall, is_tsumo=True)
            return 'win'
        else:
            self.sort_hand()
            discarded_tile = self.discard()
            print('打 ' + discarded_tile)
            print('手牌' + str(num))
            print(self.hand)
            shanten_number = self.calculate_shanten_number()
            print('シャンテン数 ' + str(shanten_number))
            print('')
            return discarded_tile

    def player_discard(self):
        while True:
            discarded_tile = input('打：　')
            if discarded_tile == '':
                return self.hand[13]
                break
            if discarded_tile in self.hand:
                return discarded_tile
                break
            print('正しい値を入力してください')

    def select_discard(self, num):
        discarded_tile = self.hand[num]
        del self.hand[num]
        self.river.append(discarded_tile)
        return discarded_tile
