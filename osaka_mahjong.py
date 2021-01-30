import random
import pygame
from mahjong.agari import Agari
from mahjong.constants import WINDS
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules, HandConstants
from mahjong.meld import Meld
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
from pygame.locals import *
import sys


class Table:
    wall = []
    dead_wall = []
    dora = []
    uradora = []
    published_tile = []
    # 局をまたぐもの
    game_number = 1
    renchan = 0
    deposits = 0

    def reset(self):
        wall_tiles = list(
            ['1m', '1m', '1m', '1m', '5m', '5m', '5m', '5m', '9m', '9m', '9m', '9m',
             '1p', '1p', '1p', '1p', '2p', '2p', '2p', '2p', '3p', '3p', '3p', '3p',
             '4p', '4p', '4p', '4p', '5p', '5p', '5p', '5p', '6p', '6p', '6p', '6p',
             '7p', '7p', '7p', '7p', '8p', '8p', '8p', '8p', '9p', '9p', '9p', '9p',
             '1s', '1s', '1s', '1s', '2s', '2s', '2s', '2s', '3s', '3s', '3s', '3s',
             '4s', '4s', '4s', '4s', '5s', '5s', '5s', '5s', '6s', '6s', '6s', '6s',
             '7s', '7s', '7s', '7s', '8s', '8s', '8s', '8s', '9s', '9s', '9s', '9s',
             '1z', '1z', '1z', '1z', '2z', '2z', '2z', '2z', '3z', '3z', '3z', '3z',
             '4z', '4z', '4z', '4z', '5z', '5z', '5z', '5z', '6z', '6z', '6z', '6z', '7z', '7z', '7z', '7z'])
        random.shuffle(wall_tiles)
        self.wall = wall_tiles[:-10]
        self.dead_wall = wall_tiles[-10:]
        self.dead_wall.reverse()
        self.dora = [self.dead_wall[-2]]
        self.uradora = [self.dead_wall[-1]]
        self.published_tile = [self.dead_wall[-2]]

    def published_tile_34_array(self):
        return tiles_34_array(self.published_tile)


class Tile:
    TILE_IMAGE_DIC = {}
    ALL_TILE = ['1m', '', '', '', '5m', '', '', '', '9m',
                '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
                '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
                '1z', '2z', '3z', '4z', '5z', '6z', '7z']

    def __init__(self):
        for tile in self.ALL_TILE:
            self.TILE_IMAGE_DIC[tile] = f'{tile}-6690-1.png'

    @staticmethod
    def dora(tile):
        index = Tile.ALL_TILE.index(tile)
        if index == 0:
            index = 8
        elif index == 8:
            index = 0
        elif index == 17:
            index = 9
        elif index == 26:
            index = 18
        elif index == 30:
            index = 27
        elif index == 33:
            index = 31
        else:
            index += 1
        return Tile.ALL_TILE[index]


def tiles_34_array(tiles):
    tiles = sorted(tiles)
    manzu = [s for s in tiles if 'm' in s]
    pinzu = [s for s in tiles if 'p' in s]
    souzu = [s for s in tiles if 's' in s]
    zihai = [s for s in tiles if 'z' in s]
    tiles = manzu + pinzu + souzu + zihai
    return TilesConverter.one_line_string_to_34_array(''.join(tiles))


class Player:
    # 局をまたぐもの
    points = 35000
    seating_order = None
    name = None
    chip = 0
    # 局ごとに変わるもの
    is_dealer = False
    hand = []
    hand_sprite = None
    pair_tile = []
    has_five_pairs = False
    melds = []
    melds_direction = []
    river = []
    is_nagashi_yakuman = True
    is_nagashi_tanyao = True
    hana = 0
    waiting = []
    is_riichi = False
    is_ippatsu = False
    declare_turn = 99
    shanten_number = None
    accepted_number = 0
    player_wind = None
    round_wind = None
    priority = ['1m', '9m', '3z', '2z', '1z', '4z', '5z', '6z', '7z',
                '1s', '9s', '9p', '1p', '2p', '8p', '8s', '2s',
                '3s', '7s', '7p', '3p', '4p', '6p', '6s', '4s', '5s', '5p']

    def __init__(self, seating_order, name):
        self.seating_order = seating_order
        self.name = name

    def start_game(self, table: Table):
        self._clear()
        round_wind = (table.game_number - 1) // 3
        player_wind = (7 - table.game_number + self.seating_order) % 3
        self.round_wind = WINDS[round_wind]
        self.player_wind = WINDS[player_wind]
        if player_wind == 0:
            self.is_dealer = True
        self._get_hand(table)
        self.sort_hand()
        self.update_hand_info()

        if table.dora[0] != '5m':
            self.priority.remove(Tile.dora(tile=table.dora[0]))
            if table.dora[0] == ('4p' or '4s'):
                self.priority.append(Tile.dora(tile=table.dora[0]))
            else:
                self.priority.insert(24, Tile.dora(tile=table.dora[0]))

    def _clear(self):
        self.is_dealer = False
        self.hand = []
        self.pair_tile = []
        self.has_five_pairs = False
        self.melds = []
        self.melds_direction = []
        self.river = []
        self.is_nagashi_yakuman = True
        self.is_nagashi_tanyao = True
        self.hana = 0
        self.waiting = []
        self.is_riichi = False
        self.is_ippatsu = False
        self.declare_turn = 99
        self.shanten_number = None
        self.accepted_number = 0
        self.player_wind = None
        self.round_wind = None
        self.priority = ['1m', '9m', '3z', '2z', '1z', '4z', '5z', '6z', '7z',
                         '1s', '9s', '9p', '1p', '2p', '8p', '8s', '2s',
                         '3s', '7s', '7p', '3p', '4p', '6p', '6s', '4s', '5s', '5p']

    def _get_hand(self, table: Table):
        self.hand = table.wall[0:13]
        del table.wall[0:13]
        self.shanten_number = self._calculate_shanten_number(hand=self.hand)
        return self.hand

    def update_hand_info(self):
        self.find_pair_tile()
        # 5対子以上＝七対子イーシャンテンになったら七対子を目指す
        if not self.has_five_pairs and len(self.pair_tile) == 5:
            self.has_five_pairs = True
        self.shanten_number = self._calculate_shanten_number()
        if self.shanten_number == 0 and len(self.hand) % 3 == 1:
            self.waiting = self.find_waiting()

    def sort_hand(self):
        self.hand = sorted(self.hand)
        manzu = [s for s in self.hand if 'm' in s]
        pinzu = [s for s in self.hand if 'p' in s]
        souzu = [s for s in self.hand if 's' in s]
        zihai = [s for s in self.hand if 'z' in s]
        self.hand = manzu + pinzu + souzu + zihai

    def find_pair_tile(self):
        hand_34_array = self.hand_34_array()
        pair_tile = []
        for x in range(0, 34):
            if hand_34_array[x] == 4:
                pair_tile.append(Tile.ALL_TILE[x])
                pair_tile.append(Tile.ALL_TILE[x])
            elif hand_34_array[x] >= 2:
                pair_tile.append(Tile.ALL_TILE[x])
        self.pair_tile = pair_tile

    def has_yakuhai_pon(self):
        hand_34_array = self.hand_34_array()
        if hand_34_array[-4:].__contains__(3):
            return True
        return hand_34_array[self.player_wind] == 3

    def has_hana(self):
        return '5m' in self.hand

    def can_riichi(self):
        return self.shanten_number == 0 and len(self.melds) == 0 and not self.is_riichi

    def hand_34_array(self):
        return tiles_34_array(self.hand)

    def melds_34_array(self):
        return [tiles_34_array(meld) for meld in self.melds]

    def open_sets_34(self):
        open_sets = []
        for meld in self.melds:
            index = Tile.ALL_TILE.index(meld[0])
            open_sets.append([index] * 3)
        return open_sets

    def draw(self, table: Table):
        drawn_tile = table.wall[0]
        del table.wall[0]
        self.hand.append(drawn_tile)
        # リーチ後は手牌情報の更新はしない、プレーヤー以外もこのタイミングでは更新しない
        if not self.is_riichi and self.seating_order == 0:
            self.update_hand_info()
        return drawn_tile

    def hana_draw(self, table: Table):
        if self.has_hana():
            self.hand.remove('5m')
            self.hana += 1
            self.sort_hand()
            self.update_hand_info()
            drawn_tile = table.dead_wall[0]
            del table.dead_wall[0]
            self.hand.append(table.dead_wall[0])
            # if not self.is_riichi:
            #     self.update_hand_info()
            return drawn_tile

    def declare_riichi(self):
        self.is_riichi = True
        self.declare_turn = len(self.river) + 1
        self.is_ippatsu = True

    def discard(self, published_tile_34_array):
        self.find_pair_tile()
        # 5対子以上＝七対子イーシャンテンになったら七対子を目指す
        if not self.has_five_pairs and len(self.pair_tile) == 5:
            self.has_five_pairs = True
        hand_34_array = self.hand_34_array()
        published_tile_all = [h + p for (h, p) in zip(hand_34_array, published_tile_34_array)]
        sutehai_kouho_final = self.hand[-1]
        accepted_number_final = self._count_accepted_tile(hand=self.hand[0:-1], published_tile=published_tile_all)
        for kouho in self.hand:
            if kouho == '5m':
                continue
            hand_copy = self.hand[:]
            hand_copy.remove(kouho)
            shanten_number = self._calculate_shanten_number(hand=hand_copy)
            if self.shanten_number > shanten_number:
                self.shanten_number = shanten_number
                sutehai_kouho_final = kouho
                accepted_number_final = self._count_accepted_tile(hand=hand_copy, published_tile=published_tile_all)
            elif self.shanten_number == shanten_number:
                accepted_number = self._count_accepted_tile(hand=hand_copy, published_tile=published_tile_all)
                if accepted_number_final < accepted_number:
                    sutehai_kouho_final = kouho
                    accepted_number_final = accepted_number
                elif accepted_number_final == accepted_number:
                    if self.priority.index(sutehai_kouho_final) > self.priority.index(kouho):
                        sutehai_kouho_final = kouho

        self.accepted_number = accepted_number_final
        self.hand.remove(sutehai_kouho_final)
        self.river.append(sutehai_kouho_final)
        self.update_hand_info()
        self.sort_hand()
        return sutehai_kouho_final

    def _count_accepted_tile(self, hand, published_tile, melds=None):
        unpublished_tile = [4 - num for num in published_tile]
        hand_34 = tiles_34_array(hand)
        if not melds:
            melds = self.melds[:]
        shanten_num = self._calculate_shanten_number(hand_34=hand_34, melds=melds)
        accepted = []
        accepted_tile_number = 0
        for index in range(34):
            if 1 <= index <= 7 or hand_34[index] == 4:
                continue
            hand_34 = tiles_34_array(hand)
            hand_34[index] += 1
            if self._calculate_shanten_number(hand_34=hand_34) < shanten_num:
                accepted.append(index)
            hand_34[index] -= 1
        for index in accepted:
            accepted_tile_number += unpublished_tile[index]
        return accepted_tile_number

    def _calculate_shanten_number(self, hand=None, melds=None, hand_34=None):
        if not hand and not hand_34:
            hand = self.hand[:]

        if not hand_34:
            hand_34 = tiles_34_array(hand)
        if not melds:
            melds = self.melds[:]

        open_sets = []
        for meld in melds:
            index = Tile.ALL_TILE.index(meld[0])
            hand_34[index] += 3
            open_sets.append([index] * 3)

        shanten = Shanten()
        shanten_number = shanten.calculate_shanten(tiles_34=hand_34,
                                                   open_sets_34=open_sets,
                                                   chiitoitsu=self.has_five_pairs,
                                                   kokushi=False)
        return shanten_number

    def find_waiting(self):
        if self.shanten_number == 0 and len(self.hand) % 3 == 1:
            hand_copy = self.hand[:]
            hand_34_array = tiles_34_array(hand_copy)
            if self.open_sets_34():
                for tiles in self.open_sets_34():
                    hand_34_array[tiles[0]] += 3
            agari = Agari()
            waiting = []
            for index in range(34):
                if 1 <= index <= 7 or hand_34_array[index] == 4:
                    continue
                hand_34_array[index] += 1
                if agari.is_agari(tiles_34=hand_34_array, open_sets_34=self.open_sets_34()):
                    waiting.append(index)
                hand_34_array[index] -= 1
            waiting_tile = [Tile.ALL_TILE[index] for index in waiting]
            return waiting_tile

    def calculate_score(self, win_tile_string, table: Table, is_tsumo,
                        is_ippatsu=False,
                        is_rinshan=False,
                        is_chankan=False,
                        is_haitei=False,
                        is_houtei=False,
                        is_daburu_riichi=False):

        hand_copy = self.hand[:]
        # 鳴き
        melds = []

        for meld in self.melds:
            # カン
            if len(meld) == 4:
                melds.append(Meld(Meld.KAN, TilesConverter.one_line_string_to_136_array(''.join(meld), False)))
                del meld[0]
            # ポン
            else:
                melds.append(Meld(Meld.PON, TilesConverter.one_line_string_to_136_array(''.join(meld))))

            hand_copy.extend(meld)

        if not is_tsumo:
            hand_copy.append(win_tile_string)

        hand_copy = sorted(hand_copy)
        manzu = [s for s in hand_copy if 'm' in s]
        pinzu = [s for s in hand_copy if 'p' in s]
        souzu = [s for s in hand_copy if 's' in s]
        zihai = [s for s in hand_copy if 'z' in s]
        hand_copy = manzu + pinzu + souzu + zihai
        # 手牌
        tiles = TilesConverter.one_line_string_to_136_array(''.join(hand_copy), has_aka_dora=True)
        # 和了牌
        win_tile = TilesConverter.one_line_string_to_136_array(win_tile_string)[0]

        # ドラ
        dora_hyouji = table.dora + table.uradora if self.is_riichi else table.dora
        dora_hana = dora_hyouji.count('5m')
        hana = self.hana * (dora_hana + 1)
        dora_indicators = [TilesConverter.one_line_string_to_136_array(tile)[0] for tile in dora_hyouji]

        # オプション(リーチ, 自風, 場風)
        config = HandConfig(is_tsumo=is_tsumo,
                            is_riichi=self.is_riichi,
                            is_ippatsu=self.is_ippatsu,
                            is_rinshan=is_rinshan,
                            is_chankan=is_chankan,
                            is_haitei=is_haitei,
                            is_houtei=is_houtei,
                            is_daburu_riichi=is_daburu_riichi,
                            is_nagashi_yakuman=False,
                            is_nagashi_tanyao=False,
                            is_tenhou=False,
                            is_renhou=False,
                            is_chiihou=False,
                            player_wind=self.player_wind,
                            round_wind=self.round_wind,
                            options=OptionalRules(
                                has_open_tanyao=False,
                                has_aka_dora=True,
                                has_double_yakuman=True,
                                kazoe_limit=HandConstants.KAZOE_LIMITED,
                                kiriage=True,
                                fu_for_open_pinfu=False,
                                fu_for_pinfu_tsumo=True,
                                renhou_as_yakuman=True,
                                has_daisharin=True,
                                has_daisharin_other_suits=True))

        # 計算
        calculator = HandCalculator()
        result = calculator.estimate_hand_value(tiles=tiles, win_tile=win_tile, hana=hana, melds=melds,
                                                dora_indicators=dora_indicators, config=config)
        return result

    def judge_tsumo(self):
        if self.hand[-1] in self.waiting:
            return True
        # 花牌は一発消えない
        if self.hand[-1] != '5m' and self.is_ippatsu:
            self.is_ippatsu = False
        return False

    def judge_ron(self, tile):
        return tile in self.waiting

    def judge_pon(self, tile):
        return tile in self.pair_tile and not self.is_riichi

    def judge(self, tile, table: Table):
        # ロン
        if self.waiting:
            if tile in self.waiting:
                direction = self.player_wind - WINDS[0]
                return direction, 'ron'

        # ポン(非聴牌時のみ)
        elif tile in self.pair_tile and not self.shanten_number == 0:
            pon_flag = False
            # 門前のときは役牌対子or役牌暗刻持ちのとき鳴く
            if not self.melds:
                if (tile in [Tile.ALL_TILE[self.player_wind], Tile.ALL_TILE[self.round_wind], '4z', '5z', '6z',
                             '7z'] and self.hand.count(tile) == 2) or self.has_yakuhai_pon():
                    pon_flag = True
            # 2枚目以降は鳴く
            else:
                pon_flag = True

            # シャンテン数が進むときor受け入れ枚数が増えるときに鳴く
            if pon_flag:
                hand_copy = self.hand[:]
                melds_copy = self.melds[:]
                hand_copy.remove(tile)
                hand_copy.remove(tile)
                melds_copy.append([tile] * 3)
                hand_34_array = tiles_34_array(hand_copy)
                published_tile_all = [h + p for (h, p) in zip(hand_34_array, table.published_tile_34_array())]
                shanten_num = self._calculate_shanten_number(hand=hand_copy, melds=melds_copy)
                accept_num = self._count_accepted_tile(hand=hand_copy,
                                                       published_tile=published_tile_all,
                                                       melds=melds_copy)
                if shanten_num < self.shanten_number \
                        or (shanten_num == self.shanten_number and accept_num > self.accepted_number):
                    self.accepted_number = accept_num
                    direction = self.player_wind - WINDS[0]
                    return direction, 'pon'

    def pon(self, tile, melds_direction):
        self.hand.remove(tile)
        self.hand.remove(tile)
        self.melds.append([tile] * 3)
        pon_dir = melds_direction * 1
        self.melds_direction.append(pon_dir)

    def act(self, table: Table):
        drawn_tile = self.hand[-1]

        # リーチor聴牌
        if self.is_riichi or self.shanten_number == 0:
            if drawn_tile in self.waiting:
                return True
            # リーチ時はツモ切り
            if self.is_riichi:
                del self.hand[-1]
                self.river.append(drawn_tile)
                if self.is_ippatsu:
                    self.is_ippatsu = False
                return
            # 鳴きの聴牌時は待ちの枚数が多くなるように待ち変え
            else:
                self.discard(published_tile_34_array=table.published_tile_34_array())
                return

        # イーシャンテン
        if self.shanten_number == 1:
            self.discard(published_tile_34_array=table.published_tile_34_array())
            if self.shanten_number == 0:
                self.waiting = self.find_waiting()
                if self.melds:
                    return
                self.is_riichi = True
                self.declare_turn = len(self.river)
                self.is_ippatsu = True
                return 'riichi'
            else:
                self.update_hand_info()
                return

        # その他
        else:
            self.discard(published_tile_34_array=table.published_tile_34_array())
            self.update_hand_info()

    def select_discard(self, num):
        discarded_tile = self.hand[num]
        del self.hand[num]
        self.river.append(discarded_tile)
        self.update_hand_info()
        return discarded_tile


# スプライトアニメーションさせるクラス
class TileSprite(pygame.sprite.Sprite):
    # コンストラクタ
    def __init__(self, hand_position, river_position, tile):
        super(TileSprite, self).__init__()

        self.image = pygame.image.load(f'./static/pic/{tile}-5575-1.png').convert_alpha()
        self.image_before = pygame.image.load(f'./static/pic/{tile}-5575-1.png').convert_alpha()
        self.rect = hand_position

        self.width_rate = 0.8
        self.height_rate = 0.8
        self.goal = river_position

        self.image_angle = 0

    # 1フレーム事に実行される関数
    def update(self, i):
        self.change_image_scale(i)  # 画像サイズを変更
        self.change_image_position(i)

    # 画像のサイズを変更する関数
    def change_image_scale(self, i):
        x_size = self.image_before.get_width() * (1 - 0.02 * i)
        y_size = self.image_before.get_height() * (1 - 0.02 * i)
        self.image = pygame.transform.scale(self.image_before, (int(x_size), int(y_size)))

    # 画像の位置を変更する関数
    def change_image_position(self, i):
        x0 = self.rect[0]
        y0 = self.rect[1]
        dx = (self.goal[0] - self.rect[0]) / 10
        dy = (self.goal[1] - self.rect[1]) / 10
        self.rect = (x0 + dx * i, y0 + dy * i)


(w, h) = (1200, 800)  # 画面サイズ
INTERVAL = 300

# hand
hand0 = [(200 + 55 * num, 725) for num in range(14)]
hand1 = [(1125, 745 - 55 * num) for num in range(14)]
hand2 = [(0, 55 * num) for num in range(14)]

hand_location_list = [[hand0, hand1, hand2],
                      [hand1, hand2, hand0],
                      [hand2, hand0, hand1]]

# river
river0 = [(446 + 44 * (num % 7), 475 + 60 * (num // 7)) for num in range(26)]
river1 = [(756 + 60 * (num // 7), 431 - 44 * (num % 7)) for num in range(26)]
river2 = [(386 - 60 * (num // 7), 167 + 44 * (num % 7)) for num in range(26)]

river_location_list = [[river0, river1, river2],
                       [river1, river2, river0],
                       [river2, river0, river1]]

# meld
meld_start0 = [(852 - 148 * num, 740) for num in range(4)]
meld_start1 = [(1140, 148 * num) for num in range(4)]
meld_start2 = [(0, 652 - 148 * num) for num in range(4)]

meld_start_list = [[meld_start0, meld_start1, meld_start2],
                   [meld_start1, meld_start2, meld_start0],
                   [meld_start2, meld_start0, meld_start1]]

# hana
hana_start0 = [(956 - 44 * num, 660) for num in range(4)]
hana_start1 = [(1060, 44 * num) for num in range(4)]
hana_start2 = [(80, 756 - 44 * num) for num in range(4)]

hana_location_list = [[hana_start0, hana_start1, hana_start2],
                      [hana_start1, hana_start2, hana_start0],
                      [hana_start2, hana_start0, hana_start1]]

# declare
declare0 = (530, 630)
declare1 = (940, 250)
declare2 = (190, 250)
declare_location_list = [[declare0, declare1, declare2],
                         [declare1, declare2, declare0],
                         [declare2, declare0, declare1]]

# angle
angle_list = [[0, 90, 270],
              [90, 270, 0],
              [270, 0, 90]]

WIND_KANJI = ['東', '南', '西']
ZAN = (590, 280)


def main():
    pygame.init()  # pygame初期化
    screen = pygame.display.set_mode((w, h))  # 画面設定
    back_image = pygame.image.load('./static/pic/tableimage.png').convert_alpha()
    window = pygame.image.load('./static/pic/black.png').convert_alpha()
    font = pygame.font.Font('mgenplus-1c-light.ttf', 44)

    # tableの作成
    table = Table()
    # playerの作成（席順指定）
    player_a = Player(seating_order=0, name='下の人')
    player_b = Player(seating_order=1, name='右の人')
    player_c = Player(seating_order=2, name='左の人')

    # 東風戦（3局）で終了
    while table.game_number != 4:
        table.reset()
        player_list = []
        player_wind = None
        hand_location = []
        river_location = []
        meld_start = []
        hana_location = []
        declare_location = []
        angle = []
        player_a.start_game(table=table)
        player_b.start_game(table=table)
        player_c.start_game(table=table)
        if table.game_number % 3 == 1:
            player_list = [player_a, player_b, player_c]
            player_wind = 0
            hand_location = hand_location_list[0]
            river_location = river_location_list[0]
            meld_start = meld_start_list[0]
            hana_location = hana_location_list[0]
            declare_location = declare_location_list[0]
            angle = angle_list[0]
        elif table.game_number % 3 == 2:
            player_list = [player_b, player_c, player_a]
            player_wind = 2
            hand_location = hand_location_list[1]
            river_location = river_location_list[1]
            meld_start = meld_start_list[1]
            hana_location = hana_location_list[1]
            declare_location = declare_location_list[1]
            angle = angle_list[1]
        elif table.game_number % 3 == 0:
            player_list = [player_c, player_a, player_b]
            player_wind = 1
            hand_location = hand_location_list[2]
            river_location = river_location_list[2]
            meld_start = meld_start_list[2]
            hana_location = hana_location_list[2]
            declare_location = declare_location_list[2]
            angle = angle_list[2]

        # table初期表示
        table_wind = (table.game_number - 1) // 3
        table_num = 3 if table.game_number % 3 == 0 else table.game_number % 3
        text_list = {(534, 160): f'{WIND_KANJI[table_wind]}',
                     (584, 160): f'{table_num}',
                     (540, 220): f'{table.renchan}',
                     (604, 348): f'{table.deposits // 1000}',
                     (508, 416): f'{WIND_KANJI[player_a.player_wind - 27]}',
                     (558, 416): f'{player_a.points}',
                     (694, 360): f'{WIND_KANJI[player_b.player_wind - 27]}',
                     (694, 220): f'{player_b.points}',
                     (440, 220): f'{WIND_KANJI[player_c.player_wind - 27]}',
                     (440, 270): f'{player_c.points}',
                     ZAN: f'{len(table.wall)}'}
        hyouji = {k: font.render(v, True, (255, 255, 255)) for (k, v) in text_list.items()}
        hyouji[(694, 360)] = pygame.transform.rotate(hyouji[(694, 360)], 90)
        hyouji[(694, 220)] = pygame.transform.rotate(hyouji[(694, 220)], 90)
        hyouji[(440, 220)] = pygame.transform.rotate(hyouji[(440, 220)], 270)
        hyouji[(440, 270)] = pygame.transform.rotate(hyouji[(440, 270)], 270)
        hyouji[(467, 80)] = pygame.image.load(f'./static/pic/{table.dora[0]}-5575-1.png').convert_alpha()

        result = None
        win_player = None
        lose_player = None
        double_ron = None
        end_game_flg = False
        clock = pygame.time.Clock()

        reset_screen(angle, back_image, font, hana_location, hand_location, hyouji, meld_start, player_list,
                     river_location, screen, table)

        # 1局
        while table.wall and not end_game_flg:

            # イベント処理
            for event in pygame.event.get():
                if event.type == QUIT:  # 閉じるボタンが押されたら終了
                    pygame.quit()  # Pygameの終了(画面閉じられる)
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        sys.exit()

                if event.type == MOUSEBUTTONUP and event.button == 1:
                    num = 0

                    # 1打
                    while table.wall and not end_game_flg:
                        reset_screen(angle, back_image, font, hana_location, hand_location, hyouji, meld_start,
                                     player_list,
                                     river_location, screen, table)
                        # プレーヤー
                        if num == player_wind:
                            drawn_tile = table.wall[0]
                            img = pygame.image.load(f'./static/pic/{drawn_tile}-5575-1.png').convert_alpha()
                            img = pygame.transform.rotate(img, angle[num])
                            screen.blit(img, hand_location[num][len(player_list[num].hand)])
                            pygame.display.update()
                            player_list[num].draw(table=table)
                            has_button = display_button(screen,
                                                        nuki=player_list[num].has_hana(),
                                                        riichi=player_list[num].can_riichi(),
                                                        hora=player_list[num].judge_tsumo())
                            pygame.time.wait(INTERVAL)
                            pygame.display.update()
                            select = wait_player_select(has_button=has_button,
                                                        nuki=player_list[num].has_hana(),
                                                        riichi=player_list[num].can_riichi(),
                                                        hora=player_list[num].judge_tsumo(),
                                                        is_riichi=player_list[num].is_riichi)
                            # ツモ
                            if player_list[num].judge_tsumo() and select == 'hora':
                                end_game_flg = True
                                win_player = num
                                break

                            # 打牌選択されるまでのループ
                            while select not in [i for i in range(14)]:
                                # 和了判定
                                if player_list[num].judge_tsumo() and select == 'hora':
                                    end_game_flg = True
                                    win_player = num
                                    break
                                # 抜き
                                elif select == 'nuki':
                                    player_list[num].hana_draw(table=table)
                                    drawn_tile = table.dead_wall[0]
                                    img = pygame.image.load('./static/pic/5m-4460-1.png').convert_alpha()
                                    img = pygame.transform.rotate(img, angle[num])
                                    screen.blit(img, hana_location[num][player_list[num].hana - 1])
                                    pygame.display.update()
                                    pygame.time.wait(INTERVAL)
                                    reset_screen(angle, back_image, font, hana_location, hand_location, hyouji,
                                                 meld_start,
                                                 player_list,
                                                 river_location, screen, table)
                                    has_button = display_button(screen,
                                                                nuki=player_list[num].has_hana(),
                                                                riichi=player_list[num].can_riichi(),
                                                                hora=player_list[num].judge_tsumo())
                                    pygame.time.wait(INTERVAL)
                                    select = wait_player_select(has_button=has_button,
                                                                nuki=player_list[num].has_hana(),
                                                                riichi=player_list[num].can_riichi(),
                                                                hora=player_list[num].judge_tsumo(),
                                                                is_riichi=player_list[num].is_riichi)
                                    continue
                                # リーチ宣言
                                elif select == 'riichi':
                                    player_list[num].declare_riichi()
                                    player_list[num].points -= 1000
                                    table.deposits += 1000
                                    declare(screen, font, declare_location, angle,
                                            declare_player_wind=num, type='リーチ')
                                    select = wait_player_select()

                            # ツモならメインループから抜ける
                            if end_game_flg:
                                break

                            # 打牌
                            fps = 50
                            for i in range(1, 11):
                                reset_screen(angle, back_image, font, hana_location, hand_location, hyouji,
                                             meld_start,
                                             player_list,
                                             river_location, screen, table, select=select)
                                player_a.hand_sprite.update(i=i)
                                player_a.hand_sprite.draw(screen)
                                pygame.display.update()
                                clock.tick(fps)
                            pygame.time.wait(400)
                            discarded_tile = player_list[num].select_discard(num=select)

                        # プレーヤー以外は自動
                        else:
                            drawn_tile = table.wall[0]
                            img = pygame.image.load(f'./static/pic/left-4455.png').convert_alpha()
                            img = pygame.transform.rotate(img, angle[num] + 90)
                            screen.blit(img, hand_location[num][len(player_list[num].hand)])
                            pygame.display.update()
                            pygame.time.wait(INTERVAL)
                            player_list[num].draw(table=table)
                            # 和了判定
                            while '5m' in player_list[num].hand:
                                player_list[num].hana_draw(table=table)
                                drawn_tile = table.dead_wall[0]
                                img = pygame.image.load('./static/pic/5m-4460-1.png').convert_alpha()
                                img = pygame.transform.rotate(img, angle[num])
                                screen.blit(img, hana_location[num][player_list[num].hana - 1])
                                pygame.display.update()
                                pygame.time.wait(INTERVAL)
                                reset_screen(angle, back_image, font, hana_location, hand_location, hyouji, meld_start,
                                             player_list,
                                             river_location, screen, table)
                            result = player_list[num].act(table=table)
                            if result == 'riichi':
                                player_list[num].points -= 1000
                                table.deposits += 1000
                                declare(screen, font, declare_location, angle,
                                        declare_player_wind=num, type='リーチ')
                            elif result:
                                end_game_flg = True
                                win_player = num
                                break
                            discarded_tile = player_list[num].river[-1]

                        player_list[num].sort_hand()
                        table.published_tile.append(discarded_tile)

                        reset_screen(angle, back_image, font, hana_location, hand_location, hyouji, meld_start,
                                     player_list,
                                     river_location, screen, table)
                        pygame.time.wait(INTERVAL)

                        while True:
                            # ジャッジ
                            judge = None
                            judge_list = []
                            for i in range(3):
                                # 自分は除く
                                if i == num:
                                    continue
                                # プレーヤー
                                elif i == player_wind:
                                    pon_judge = player_list[i].judge_pon(tile=discarded_tile)
                                    ron_judge = player_list[i].judge_ron(tile=discarded_tile)
                                    has_button = display_button(screen,
                                                                pon=pon_judge,
                                                                hora=ron_judge)
                                    if has_button:
                                        action = push_button(pon=pon_judge, hora=ron_judge)
                                        judge = (i, action) if action else None
                                # プレーヤー以外
                                else:
                                    judge = player_list[i].judge(tile=discarded_tile, table=table)

                                if judge:
                                    judge_list.append(judge)
                            if judge_list:
                                # ポンロンorダブロン
                                if len(judge_list) == 2:
                                    win_player_list = [j[0] for j in judge_list if j[1] == 'ron']
                                    if len(win_player_list) == 2:
                                        double_ron = win_player_list
                                    elif len(win_player_list) == 1:
                                        win_player = win_player_list[0]
                                    end_game_flg = True
                                    break
                                # ロン
                                elif judge_list[0][1] == 'ron':
                                    win_player = judge_list[0][0]
                                    lose_player = num
                                    end_game_flg = True
                                    break
                                # ポン
                                elif judge_list[0][1] == 'pon':
                                    # ラスト１巡は鳴けない
                                    if not table.wall:
                                        end_game_flg = True
                                        break

                                    declare(screen, font, declare_location, angle,
                                            declare_player_wind=judge_list[0][0], type='ポン')

                                    del player_list[num].river[-1]
                                    # 3枚見える
                                    table.published_tile.append(discarded_tile)
                                    table.published_tile.append(discarded_tile)
                                    melds_direction = (judge_list[0][0] - num + 3) % 3
                                    num = judge_list[0][0]
                                    player_list[num].pon(tile=discarded_tile, melds_direction=melds_direction)
                                    reset_screen(angle, back_image, font, hana_location, hand_location, hyouji,
                                                 meld_start, player_list,
                                                 river_location, screen, table)
                                    pygame.time.wait(INTERVAL)

                                    # プレーヤー
                                    if num == player_wind:
                                        select = wait_player_select()
                                        # 打牌
                                        fps = 50
                                        for i in range(1, 11):
                                            reset_screen(angle, back_image, font, hana_location, hand_location, hyouji,
                                                         meld_start,
                                                         player_list,
                                                         river_location, screen, table, select=select)
                                            player_a.hand_sprite.update(i=i)
                                            player_a.hand_sprite.draw(screen)
                                            pygame.display.update()
                                            clock.tick(fps)
                                        pygame.time.wait(400)
                                        discarded_tile = player_list[num].select_discard(num=select)

                                    # プレーヤー以外
                                    else:
                                        discarded_tile = player_list[num].discard(table.published_tile_34_array())

                                    reset_screen(angle, back_image, font, hana_location, hand_location, hyouji,
                                                 meld_start, player_list,
                                                 river_location, screen, table)
                                    pygame.time.wait(INTERVAL)
                                    continue
                            else:
                                num = num + 1 if num != 2 else 0
                                break

        # ダブロン
        if double_ron is not None:
            lose_player = [lose for lose in range(3) if lose not in double_ron][0]
            result0 = player_list[double_ron[0]].calculate_score(win_tile_string=discarded_tile,
                                                                 table=table,
                                                                 is_tsumo=False)
            result1 = player_list[double_ron[1]].calculate_score(win_tile_string=discarded_tile,
                                                                 table=table,
                                                                 is_tsumo=False)
            player_list[double_ron[0]].points += result0.cost['main'] + table.renchan * 1000
            player_list[double_ron[1]].points += result1.cost['main']
            player_list[lose_player].points -= result0.cost['main'] + result1.cost['main'] + table.renchan * 1000
            player_list[double_ron[0]].points += table.deposits
            table.deposits = 0

            # 1人目
            for (tile, hand) in zip(player_list[double_ron[0]].hand, hand_location[double_ron[0]]):
                img_path = f'./static/pic/{tile}-5575-1.png'
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.rotate(img, angle[double_ron[0]])
                screen.blit(img, hand)
            declare(screen, font, declare_location, angle,
                    declare_player_wind=double_ron[0], type='ロン')

            # 2人目
            for (tile, hand) in zip(player_list[double_ron[1]].hand, hand_location[double_ron[1]]):
                img_path = f'./static/pic/{tile}-5575-1.png'
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.rotate(img, angle[double_ron[1]])
                screen.blit(img, hand)
            declare(screen, font, declare_location, angle,
                    declare_player_wind=double_ron[1], type='ロン')
            pygame.display.update()
            pygame.time.wait(1000)
            display_result(font, player_list, window, screen, table, result=result0, win_player=double_ron[0])
            display_result(font, player_list, window, screen, table, result=result1, win_player=double_ron[1])

            if double_ron[0] == 0:
                table.renchan += 1
            else:
                table.renchan = 0
                table.game_number += 1

        # win_playerだけだと0が和了ったときにバグる
        elif win_player is not None:
            result = move_points(discarded_tile, drawn_tile, lose_player, player_list, table, win_player)
            reset_screen(angle, back_image, font, hana_location, hand_location, hyouji, meld_start, player_list,
                         river_location, screen, table)

            for (tile, hand) in zip(player_list[win_player].hand, hand_location[win_player]):
                img_path = f'./static/pic/{tile}-5575-1.png'
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.rotate(img, angle[win_player])
                screen.blit(img, hand)
            declare(screen, font, declare_location, angle,
                    declare_player_wind=win_player, type='和了')
            pygame.display.update()
            pygame.time.wait(1000)

            display_result(font, player_list, window, screen, table, result, win_player)
            if win_player == 0:
                table.renchan += 1
            else:
                table.renchan = 0
                table.game_number += 1

        # 流局
        else:
            if player_list[0].shanten_number == 0:
                table.renchan += 1
            else:
                table.renchan += 1
                table.game_number += 1

            screen.blit(window, (250, 163))
            text1 = font.render('流局', True, (255, 255, 255))
            screen.blit(text1, [270, 180])
            pygame.time.wait(3000)
            pygame.display.update()
            pygame.time.wait(10000)

    return player_list


def display_result(font, player_list, window, screen, table, result, win_player):
    screen.blit(window, (250, 163))
    # 裏ドラ
    uradora = pygame.image.load(f'./static/pic/{table.uradora[0]}-5575-1.png').convert_alpha()
    screen.blit(uradora, (467, 5))
    text1 = font.render(f'{player_list[win_player].name} win!', True, (255, 255, 255))
    text2 = font.render(f'{result.fu}符 {result.han}飜', True, (255, 255, 255))
    text3 = font.render(f'{result.yaku}', True, (255, 255, 255))
    text4 = font.render(f'{result.cost["main"]} - {result.cost["additional"]}', True, (255, 255, 255))
    screen.blit(text1, [270, 180])
    screen.blit(text2, [270, 250])
    screen.blit(text3, [270, 320])
    screen.blit(text4, [270, 390])
    pygame.time.wait(3000)
    pygame.display.update()
    pygame.time.wait(10000)


def move_points(discarded_tile, drawn_tile, lose_player, player_list, table, win_player):
    # ツモ
    if lose_player is not None:
        result = player_list[win_player].calculate_score(win_tile_string=discarded_tile,
                                                         table=table,
                                                         is_tsumo=False)
        player_list[win_player].points += result.cost['main'] + table.renchan * 1000
        player_list[lose_player].points -= result.cost['main'] + table.renchan * 1000

    # ロン
    else:
        result = player_list[win_player].calculate_score(win_tile_string=drawn_tile,
                                                         table=table,
                                                         is_tsumo=True)
        if win_player == 0:
            player_list[win_player].points += result.cost['main'] * 2 + table.renchan * 1000 * 2
            player_list[1].points -= result.cost['main'] + table.renchan * 1000
            player_list[2].points -= result.cost['main'] + table.renchan * 1000
        elif win_player == 1:
            player_list[win_player].points += \
                result.cost['main'] + result.cost['additional'] + table.renchan * 1000 * 2
            player_list[0].points -= result.cost['main'] + table.renchan * 1000
            player_list[2].points -= result.cost['additional'] + table.renchan * 1000
        elif win_player == 2:
            player_list[win_player].points += \
                result.cost['main'] + result.cost['additional'] + table.renchan * 1000 * 2
            player_list[0].points -= result.cost['main'] + table.renchan * 1000
            player_list[1].points -= result.cost['additional'] + table.renchan * 1000

    player_list[win_player].points += table.deposits
    table.deposits = 0
    return result


def reset_screen(angle, back_image, font, hana_location, hand_location, hyouji, meld_start, player_list, river_location,
                 screen, table, select=None):
    screen.blit(back_image, [0, 0])
    hyouji[ZAN] = font.render(f'{len(table.wall)}', True, (255, 255, 255))
    for k, v in hyouji.items():
        screen.blit(v, k)
    # 初期表示
    for player, num in zip(player_list, range(3)):
        # river
        for (tile, river, turn_num) in zip(player.river, river_location[num], range(1, 22)):
            img_path = f'./static/pic/{tile}-4460-1.png'
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.rotate(img, angle[num])
            # リーチ宣言牌
            dx, dy = 0, 0
            if player.is_riichi:
                if player.declare_turn == turn_num:
                    img = pygame.transform.rotate(img, 90)
                    if player.seating_order == 1:
                        dy = -16
                    if player.seating_order == 2:
                        dx = 16
                elif player.declare_turn < turn_num and (player.declare_turn - 1) // 7 == (turn_num - 1) // 7:
                    if player.seating_order == 0:
                        dx, dy = 16, 0
                    if player.seating_order == 1:
                        dx, dy = 0, -16
                    if player.seating_order == 2:
                        dx, dy = 0, 16

            screen.blit(img, (river[0] + dx, river[1] + dy))

        # hand
        if player.seating_order == 0:
            player.hand_sprite = None
            for (tile, hand, hand_num) in zip(player.hand, hand_location[num], range(14)):
                if hand_num == select:
                    hand_tile = pygame.sprite.Group(TileSprite(hand_position=hand,
                                                               river_position=river_location[num][len(player.river)],
                                                               tile=tile))
                    hand_tile.draw(screen)
                    player.hand_sprite = hand_tile
                else:
                    img_path = f'./static/pic/{tile}-5575-1.png'
                    img = pygame.image.load(img_path).convert_alpha()
                    screen.blit(img, hand)

        else:
            for (tile, hand) in zip(player.hand, hand_location[num]):
                # img_path = f'./static/pic/{tile}-5575-1.png'
                img_path = './static/pic/left-4455.png'
                img = pygame.image.load(img_path).convert_alpha()
                # img = pygame.transform.rotate(img, angle[num])
                img = pygame.transform.rotate(img, angle[num] + 90)
                screen.blit(img, hand)

        # melds
        if player.melds:
            for meld, direction, start in zip(player.melds, player.melds_direction, meld_start[num]):
                img = pygame.image.load(f'./static/pic/{meld[0]}-4460-1.png').convert_alpha()
                img = pygame.transform.rotate(img, angle[num])
                img_flip = pygame.transform.rotate(img, 90)
                if player_list[num].seating_order == 0:
                    if direction == 1:
                        screen.blit(img_flip, (start[0], start[1] + 16))
                        screen.blit(img, (start[0] + 60, start[1]))
                        screen.blit(img, (start[0] + 104, start[1]))
                    if direction == 2:
                        screen.blit(img, (start[0], start[1]))
                        screen.blit(img, (start[0] + 44, start[1]))
                        screen.blit(img_flip, (start[0] + 88, start[1] + 16))
                if player_list[num].seating_order == 1:
                    if direction == 1:
                        screen.blit(img_flip, (start[0] + 16, start[1] + 88))
                        screen.blit(img, (start[0], start[1] + 44))
                        screen.blit(img, (start[0], start[1]))
                    if direction == 2:
                        screen.blit(img, (start[0], start[1] + 104))
                        screen.blit(img, (start[0], start[1] + 60))
                        screen.blit(img_flip, (start[0] + 16, start[1]))
                if player_list[num].seating_order == 2:
                    if direction == 1:
                        screen.blit(img_flip, (start[0], start[1]))
                        screen.blit(img, (start[0], start[1] + 60))
                        screen.blit(img, (start[0], start[1] + 104))
                    if direction == 2:
                        screen.blit(img, (start[0], start[1]))
                        screen.blit(img, (start[0], start[1] + 44))
                        screen.blit(img_flip, (start[0], start[1] + 88))

        # hana
        if player.hana:
            for hana_num in range(player.hana):
                img = pygame.image.load('./static/pic/5m-4460-1.png').convert_alpha()
                img = pygame.transform.rotate(img, angle[num])
                screen.blit(img, hana_location[num][hana_num])
    pygame.display.update()


def declare(screen, font, declare_location, angle, declare_player_wind, type):
    text = font.render(type, True, (0, 0, 0))
    text = pygame.transform.rotate(text, angle[declare_player_wind])
    screen.blit(text, declare_location[declare_player_wind])
    pygame.display.update()
    pygame.time.wait(1000)


def display_button(screen, kan=False, pon=False, nuki=False, riichi=False, hora=False):
    img_path = None
    if kan:
        img_path = './static/pic/button_kan.png'
        img = pygame.image.load(img_path).convert_alpha()
        img.set_alpha(128)
        screen.blit(img, (700, 500))
    if pon:
        img_path = './static/pic/button_pon.png'
        img = pygame.image.load(img_path).convert_alpha()
        img.set_alpha(128)
        screen.blit(img, (800, 500))
    if nuki:
        img_path = './static/pic/button_nuki.png'
        img = pygame.image.load(img_path).convert_alpha()
        img.set_alpha(128)
        screen.blit(img, (900, 500))
    if riichi:
        img_path = './static/pic/button_riichi.png'
        img = pygame.image.load(img_path).convert_alpha()
        img.set_alpha(128)
        screen.blit(img, (800, 570))
    if hora:
        img_path = './static/pic/button_hora.png'
        img = pygame.image.load(img_path).convert_alpha()
        img.set_alpha(128)
        screen.blit(img, (900, 570))

    # 何かしらのボタンが有る場合のみキャンセルボタンを表示
    if img_path:
        img_path = './static/pic/button_cancel.png'
        img = pygame.image.load(img_path).convert_alpha()
        img.set_alpha(128)
        screen.blit(img, (700, 570))
        pygame.display.update()
        return True


def push_button(kan=False, pon=False, hora=False):
    while True:
        for e in pygame.event.get():
            if e.type == MOUSEBUTTONUP and e.button == 1:
                x, y = e.pos
                if 700 <= x <= 800 and 500 <= y <= 570 and kan:
                    return 'kan'
                elif 800 <= x <= 900 and 500 <= y <= 570 and pon:
                    return 'pon'
                # Xボタン
                elif 700 <= x <= 800 and 570 <= y <= 640:
                    return False
                elif 900 <= x <= 1000 and 570 <= y <= 640 and hora:
                    return 'ron'


def wait_player_select(has_button=False, kan=False, nuki=False, riichi=False, hora=False, is_riichi=False):
    # リーチ後かつ抜きドラ、和了がない場合はツモ切り
    if not has_button and is_riichi:
        return 13
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:  # 閉じるボタンが押されたら終了
                pygame.quit()  # Pygameの終了(画面閉じられる)
                sys.exit()

            if e.type == MOUSEBUTTONUP and e.button == 1:
                x, y = e.pos
                if hand0[0][1] <= y <= hand0[0][1] + 75:
                    selected_order = (x - hand0[0][0]) // 55
                    return selected_order
                elif has_button:
                    if 700 <= x <= 800 and 500 <= y <= 570 and kan:
                        return 'kan'
                    elif 900 <= x <= 1000 and 500 <= y <= 570 and nuki:
                        return 'nuki'
                    elif 800 <= x <= 900 and 570 <= y <= 640 and riichi:
                        return 'riichi'
                    elif 900 <= x <= 1000 and 570 <= y <= 640 and hora:
                        return 'hora'


if __name__ == "__main__":
    player_list_result = main()
    for p in player_list_result:
        print(p.name + ':' + str(p.points))
