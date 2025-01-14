from engine_2 import *
import copy

player1_set, player2_set, player3_set, player4_set, player5_set, player6_set = build_sets()
player1_obj, player2_obj, player3_obj, player4_obj, player5_obj, player6_obj = build_obj_sets()
player1_inv_homes, player2_inv_homes, player3_inv_homes, player4_inv_homes, player5_inv_homes, player6_inv_homes = \
    build_invalid_homes_sets(player1_set, player2_set, player3_set, player4_set, player5_set, player6_set, player1_obj,
                             player2_obj, player3_obj, player4_obj, player5_obj, player6_obj)


def player_move(move,board, player, player1_set, player2_set, player3_set, player4_set, player5_set, player6_set):
    # 获取玩家的棋子集合
    set_pieces = assign_set(player, player1_set, player2_set, player3_set, player4_set, player5_set, player6_set)

    # 获取玩家的目标位置集合
    obj_set = assign_obj_set(player, player1_obj, player2_obj, player3_obj, player4_obj, player5_obj, player6_obj)

    # 获取玩家的无效起始位置集合
    inv_homes_set = assign_invalid_homes_set(player, player1_inv_homes, player2_inv_homes, player3_inv_homes,
                                             player4_inv_homes, player5_inv_homes, player6_inv_homes)

    # 获取规则允许的合法移动步骤
    valid_moves = find_all_legal_moves(board, set_pieces, obj_set, inv_homes_set)

    if len(valid_moves) == 0:
        print("No valid moves for the player.")
        return board

    # 通过用户输入获取玩家的移动选择
    # 这里以简单的示例方式，假设玩家选择第一个合法移动步骤
    selected_move = valid_moves[0]

    # 更新棋盘状态和玩家的棋子集合
    #update_board(board, set_pieces, selected_move)

    # 计算移动的得分
    #move_score = calculate_board_score(selected_move)

    # 输出移动位置和得分
    #print("Player moved to position:", selected_move)
    #print("Move score:", move_score)

    return selected_move
