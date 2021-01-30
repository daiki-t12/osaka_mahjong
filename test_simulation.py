import copy

from mahjong_game import table
from mahjong_game import player
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter


table = table.Table()
wall = table.wall
print('山 最初')
print(wall)
print('')

player1 = player.Player()
player1.get_hand(wall)
print('手牌1')
print(player1.hand)
print('')

print('リー牌後 手牌1')
player1.sort_hand()
print(player1.hand)
print('')

player2 = player.Player()
player2.get_hand(wall)
print('手牌2')
print(player2.hand)
print('')

print('リー牌後 手牌2')
player2.sort_hand()
print(player2.hand)
print('')

discarded_tile = ''

for i in range(21):
    """
    print('%s順目'%(i + 1))
    tsumohai = player1.tsumo(stack)
    # print(player1.tehai)
    print('ツモ ' + tsumohai)
    if player1.shanten_keisan() == -1:
        print('和了')
        print(player1.tehai)
        player1.tensuu_keisan(win_tile_string=tsumohai, stack=stack)
        break
    player1.riipai()
    dahai = player1.dahai()
    print('打 ' + dahai)
    print('手牌1')
    print(player1.tehai)
    shantensuu = player1.shanten_keisan()
    print('シャンテン数 ' + str(shantensuu))
    print('')
"""

    print('%s順目'%(i + 1))
    discarded_tile = player1.act(1, wall)
    if discarded_tile == 'win' or player1.ron(2, wall, discarded_tile):
        break

    discarded_tile = player2.act(2, wall)
    if discarded_tile == 'win' or player2.ron(1, wall, discarded_tile):
        break
else:
    print('')
    print('流局')

print('ドラ表示牌：' + wall[-5] + '　裏ドラ表示牌：' + wall[-6])

print('捨て牌')
print(player1.river)
print('')

print('山 最後')
print(wall)