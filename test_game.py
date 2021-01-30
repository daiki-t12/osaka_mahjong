import copy

from mahjong_game import table
from mahjong_game import player
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter


table = table.Table()
wall = table.wall
print('山が用意されました')
print(f'ドラ表示牌：{wall[-5]}')

player1 = player.Player()
player1.get_hand(wall)
player1.sort_hand()
print('配牌')
print(player1.hand)
print('')

player2 = player.Player()
player2.get_hand(wall)
player2.sort_hand()

discarded_tile = ''

for i in range(21):
    print('%s順目'%(i + 1))

    # プレーヤーの手番
    print('手牌')
    player1.sort_hand()
    print(player1.hand)
    drawn_tile = player1.draw(wall)
    print('ツモ')
    print(drawn_tile)
    if player1.calculate_shanten_number() == -1:
        print('プレーヤー：自摸和')
        player1.calculate_score(win_tile_string=drawn_tile, wall=wall, is_tsumo=True)
        break
    # 打牌
    discarded_tile = player1.player_discard()

    player1.hand.remove(discarded_tile)
    player1.river.append(discarded_tile)

    if player2.ron(2, wall, discarded_tile):
        break

    # 相手の手番
    # discarded_tile = player2.act(2, wall)
    print('相手')
    player2.draw(wall)
    if player2.calculate_shanten_number() == -1:
        print('相手：自摸和')
        player2.calculate_score(win_tile_string=drawn_tile, wall=wall, is_tsumo=True)
        break

    discarded_tile = player2.discard()
    print(player2.river)
    if discarded_tile == 'win' or player1.ron(1, wall, discarded_tile):
        break

else:
    print('')
    print('流局')

print('相手手牌')
player2.sort_hand()
print(player2.hand)
print(f'ドラ表示牌：{wall[-5]}　裏ドラ表示牌：{wall[-6]}')

print('捨て牌')
print(player1.river)
print('')

print('山 最後')
print(wall)