# TODO add player turn in-game
# TODO fix rebuild of interface every damn turn
# TODO won screen + stats
# TODO interface not responding if i dont move cursor on it -> maybe insert FPS?
# TODO reorder functions files

# import numpy as np
import sys
import pygame
from pygame.locals import *
import random
from engine import *
from engine_2 import *
from gui import *
import time
import gamer
import  cnn


def main():
    # 初始化 Pygame
    pygame.init()

    # 创建窗口
    window_width, window_height = 800, 600
    window = pygame.display.set_mode((window_width, window_height))

    # 设置窗口标题
    pygame.display.set_caption("跳棋游戏")

    # 加载背景图像
    background_image1 = pygame.image.load("ChineseChekersAI-master/ChineseChekersAI-master/跳棋.jpg")
    background_image1 = pygame.transform.scale(background_image1,(800,600))

    # 设置欢迎文字
    font = pygame.font.Font(None, 80)
    text = font.render("Chinese"
                       " Checker's game!", True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.center = (window_width // 2, window_height // 2)
    # 设置转场动画时长
    transition_duration = 3.0  # 单位：秒

    # 淡入效果
    transition_alpha = 0
    transition_start_time = time.time()
    while transition_alpha < 255:
        # 计算透明度
        elapsed_time = time.time() - transition_start_time
        transition_alpha = int((elapsed_time / transition_duration) * 255)
        if transition_alpha > 255:
            transition_alpha = 255

        window.fill((0,0,0))
        # 绘制欢迎窗口和过渡效果
        window.blit(background_image1, (0, 0))
        text.set_alpha(transition_alpha)
        background_image1.set_alpha(transition_alpha)  # 设置背景图像透明度
        window.blit(background_image1, (0, 0))
        window.blit(text, text_rect)
        pygame.display.flip()

    # 切换到目录窗口
    # TODO: 编写目录窗口的代码

    pygame.display.set_caption("Game Menu")

    # 设置背景颜色
    background_color = (233, 255, 255)

    background_image = pygame.image.load("ChineseChekersAI-master/ChineseChekersAI-master/跳棋背景图.png")
    background_image = pygame.transform.scale(background_image, (window_width, window_height))
    # 设置字体和字号
    font = pygame.font.SysFont(None, 80)

    # 创建文字对象
    text1 = font.render("Click to start the game!!", True, (30,0,0))

    # 获取文字对象的矩形
    text_rect1 = text1.get_rect()

    # 设置文字位置
    text_rect1.center = (window_width // 2, window_height*2 // 6)

    # 设置按钮的位置和大小
    button_width = 270
    button_height = 70
    button_x = window_width // 2 - button_width // 2
    button_y = window_height // 2 - button_height // 2

    # 设置按钮文本和颜色
    button_texts = ['level 1', 'level 2', 'level 3','level 4']
    button_colors = [(187,255,255),(188,255,133), (255, 233, 122), (255, 150, 150),]

    # 淡出效果
    transition_alpha = 255
    transition_start_time = time.time()
    while transition_alpha > 0:
        # 计算透明度
        elapsed_time = time.time() - transition_start_time
        transition_alpha = int(255 - (elapsed_time / transition_duration) * 255)
        if transition_alpha < 0:
            transition_alpha = 0
        window.blit(background_image1, (0, 0))
        text.set_alpha(transition_alpha)
        background_image1.set_alpha(transition_alpha)  # 设置背景图像透明度
        window.blit(background_image1, (0, 0))
        window.blit(text, text_rect)
        pygame.display.flip()



        # 绘制目录窗口和过渡效果
        window.blit(background_image,(0,0))  # 绘制黑色背景

    # 游戏主循环
    while True:
        # 绘制背景图像
        window.blit(background_image, (0, 0))

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键按下
                    mouse_x, mouse_y = event.pos
                    for i in range(len(button_texts)):
                        if button_x <= mouse_x <= button_x + button_width and \
                                button_y + i * button_height <= mouse_y <= button_y + (i + 1) * button_height:
                            # 根据按钮索引跳转到不同的游戏界面
                            difficulty = button_texts[i]
                            print("Start game with difficulty:", difficulty)
                            if difficulty =='level 1':
                                algorithm = cnn
                            if difficulty=='level 2':
                                algorithm = alphabeta
                            if difficulty =='level 3':
                                algorithm = greedy
                            if difficulty =='level 4':
                                algorithm = minimax
                            # 在这里添加相应的跳转逻辑
                            gameboard(algorithm)
                            # 更新窗口显示
                            pygame.display.flip()

        # 在窗口上绘制文字
        window.blit(text1, text_rect1)
        # 绘制按钮
        for i in range(len(button_texts)):
            button_rect = pygame.Rect(button_x, button_y + i * button_height, button_width, button_height)
            pygame.draw.rect(window, button_colors[i], button_rect)
            font = pygame.font.Font(None, 36)
            text = font.render(button_texts[i], True, (0, 0, 0))
            text_rect = text.get_rect(center=button_rect.center)
            window.blit(text, text_rect)

        # 更新屏幕显示
        pygame.display.flip()

def gameboard(algorithm):
    # win counters
    p1_win = 0
    p2_win = 0
    p3_win = 0
    p4_win = 0
    p5_win = 0
    p6_win = 0
    times = 0

    # stuck counter
    stuck_counter = 0

    # times
    restart_time = 5000
    move_time = 100

    board = build_board()
    player1_set, player2_set, player3_set, player4_set, player5_set, player6_set = build_sets()
    player1_obj, player2_obj, player3_obj, player4_obj, player5_obj, player6_obj = build_obj_sets()
    player1_invalid_home, player2_invalid_home, player3_invalid_home, player4_invalid_home, player5_invalid_home, \
    player6_invalid_home = build_invalid_homes_sets(player1_set, player2_set, player3_set, player4_set,
                                                    player5_set, player6_set, player1_obj, player2_obj,
                                                    player3_obj, player4_obj, player5_obj, player6_obj)

    display_surface = init_board()

    # player decision
    player_turn = 1

    # game start
    game_over = False
    first_turn = True
    first_round = True
    save_first_p = 1

    #x_coord = (0,0)
    #y_coord = (0,0)

    next_move = USEREVENT + 1
    restart_game = USEREVENT + 2

    event = pg.event.Event(next_move)
    pg.event.post(event)

    # event = pg.event.EventType
    # event.type = pg.KEYDOWN
    # event.key = ord("a")

    while True:

        draw_board(board, display_surface)

        for event in pg.event.get():
            # consider the pieces of the player of this turn
            set_pieces = assign_set(player_turn, player1_set, player2_set, player3_set, player4_set,
                                    player5_set, player6_set)

            # identify homes of the player of this turn
            invalid_homes_set = assign_invalid_homes_set(player_turn, player1_invalid_home,
                                                         player2_invalid_home, player3_invalid_home,
                                                         player4_invalid_home, player5_invalid_home,
                                                         player6_invalid_home)

            # assign objective set of positions
            obj_set = assign_obj_set(player_turn, player1_obj, player2_obj, player3_obj, player4_obj,
                                     player5_obj, player6_obj)
            # find all legal moves given a piece set of a player
            # all_legal_moves = find_all_legal_moves(board, set_pieces, obj_set, invalid_set, invalid_homes_set)
            all_legal_moves = find_all_legal_moves(board, set_pieces, obj_set, invalid_homes_set)

            if event.type == QUIT:
                pg.quit()
                sys.exit()

            if event.type == restart_game:
                pg.time.wait(restart_time)

                board = build_board()
                player1_set, player2_set, player3_set, player4_set, player5_set, player6_set = build_sets()
                player1_obj, player2_obj, player3_obj, player4_obj, player5_obj, player6_obj = build_obj_sets()
                player1_invalid_home, player2_invalid_home, player3_invalid_home, player4_invalid_home, \
                player5_invalid_home, player6_invalid_home = build_invalid_homes_sets(
                    player1_set, player2_set, player3_set, player4_set, player5_set, player6_set, player1_obj,
                    player2_obj, player3_obj, player4_obj, player5_obj, player6_obj)
                display_surface = init_board()

                # player decision
                player_turn = 1

                draw_board(board, display_surface)
                pg.display.update()

                # game restart
                game_over = False
                first_turn = True
                first_round = True
                save_first_p = 1

                event = pg.event.Event(next_move)
                pg.event.post(event)

                break

            # ...

            if event.type == next_move and not game_over:
                pg.time.wait(move_time)

                if player_turn == 2:
                    valid_move = False
                    click_count = 0
                    while not valid_move:
                        for event in pg.event.get():  # 获取所有当前的事件
                            if event.type == pg.QUIT:
                                pg.quit()
                                sys.exit()

                            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
                                if click_count == 0:
                                    click_count += 1
                                    best_move = []
                                    # 获取鼠标点击位置
                                    mouse_pos = pg.mouse.get_pos()
                                    x_coord, y_coord = get_clicked_cell(mouse_pos[0], mouse_pos[1])
                                    best_move.append([int(x_coord), int(y_coord*2)])
                                    '''
                                    if best_move[0] in set_pieces:
                                        
                                    else:
                                        continue
                                    '''
                                    # highlight_move(best_move,display_surface)
                                    highlight_move(best_move, display_surface, 0)
                                    pg.display.update()
                                    print(best_move)
                                    print(set_pieces)

                                elif click_count == 1:
                                    click_count = 0
                                    mouse_pos1 = pg.mouse.get_pos()
                                    x_coord, y_coord = get_clicked_cell(mouse_pos1[0], mouse_pos1[1])
                                    best_move.append([int(x_coord), int(y_coord*2)])
                                    print(best_move)
                                    # print('yes',find_all_legal_moves(board, set_pieces, obj_set, invalid_homes_set))
                                    second_elements = [sublist[1] for sublist in
                                                       find_all_legal_moves(board, set_pieces, obj_set,
                                                                            invalid_homes_set)]
                                    print('y', second_elements)
                                    #if best_move[1] in second_elements:
                                    print(best_move, 'y')
                                    valid_move = True
                                    highlight_move(best_move, display_surface, 1)
                                    # 刷新显示界面
                                    pg.display.flip()
                                    time.sleep(0.5)
                                    board, set_pieces = do_moves(board, best_move, set_pieces)
                                    # update set
                                    player1_set, player2_set, player3_set, player4_set, player5_set, player6_set = \
                                        update_player_set(set_pieces, player_turn, player1_set, player2_set,
                                                          player3_set, player4_set,
                                                          player5_set, player6_set)
                                    # 调用 draw_board 函数重新绘制棋盘和棋子位置
                                    draw_board(board, display_surface)
                                    # 刷新显示界面
                                    pg.display.flip()
                                    # print('y')


                                else:
                                    continue

                    '''
                        else:
                            # 获取鼠标位置
                            if event.type == pygame.MOUSEMOTION:
                                move = []
                                mouse_pos = pygame.mouse.get_pos()
                                #print(mouse_pos)
                                
                                for row in range(0, 17):
                                    for col in range(0, 13):
                                        # 计算棋盘位置的矩形区域
                                        rect = pg.Rect(H_MARGIN_DISTANCE + col * (CIRCLE_DIAMETER + H_SPACING),
                                                       V_MARGIN_DISTANCE + row * (CIRCLE_DIAMETER + V_SPACING),
                                                       CIRCLE_DIAMETER, CIRCLE_DIAMETER)
                                        # 获取棋盘位置的行列索引
                                        row_index = (row - V_MARGIN_DISTANCE) // (CIRCLE_DIAMETER + V_SPACING)
                                        col_index = (col - H_MARGIN_DISTANCE) // (CIRCLE_DIAMETER + H_SPACING)

                                        # 获取旗子位置
                                        piece_pos = (row_index, col_index)
                                        # 判断鼠标是否悬停在棋盘位置上
                                        if rect.collidepoint(mouse_pos) and piece_pos in set_pieces:
                                            # 绘制亮起效果，例如改变颜色或绘制边框
                                            highlight_best_move(piece_pos, display_surface)
                                            # 更新显示
                                            pg.display.update()
                                
                                # mouse_pos = pygame.mouse.get_pos()
                                x, y = get_clicked_cell(mouse_pos[0], mouse_pos[1])
                                move.append([int(x), int(y) + 10])
                                #print(move)
                                if move[0] in set_pieces:
                                    # highlight_move(best_move,display_surface)
                                    highlight_move(move, display_surface, 0)
                                    pg.display.update()
                                    #time.sleep(0.1)
                                    pg.display.flip()
                                    #pg.display.update()
                                else:
                                    continue
                            '''

                if player_turn == 7:
                    player_turn = 1

                # choose the best move
                '''if player_turn == 2:
                    # best_move_index = random.randint(0, len(all_legal_moves) - 1)
                    # best_move = all_legal_moves[best_move_index]
                    best_move = (x_coord, y_coord)
                    '''
                if player_turn !=2:
                    best_move = find_best_move(board, all_legal_moves, obj_set, player_turn, set_pieces,
                                               player1_set, player2_set, player3_set, player4_set, player5_set,
                                               player6_set,algorithm)
                # print("player:", player_turn, "best move:", best_move)

                # randomize first move
                if player_turn == save_first_p:
                    first_round = False
                if first_turn:
                    save_first_p = player_turn
                    first_turn = False


                # print("Player", player_turn)


                if best_move is None:
                    game_over = True
                    stuck_counter = stuck_counter + 1
                    print('Game stuck counter:', stuck_counter)
                    print('[]------------------[]')

                    event = pg.event.Event(restart_game)
                    pg.event.post(event)

                    break

                # highlight the move chosen
                if player_turn != 2:
                    highlight_best_move(best_move, display_surface)
                    pg.display.update()

                # do the best move
                if player_turn != 2:
                    board, set_pieces = do_move(board, best_move, set_pieces)
                    #print('yes')

                # update set
                player1_set, player2_set, player3_set, player4_set, player5_set, player6_set = \
                    update_player_set(set_pieces, player_turn, player1_set, player2_set, player3_set, player4_set,
                                      player5_set, player6_set)
                # 调用 draw_board 函数重新绘制棋盘和棋子位置
                draw_board(board, display_surface)

                # 刷新显示界面
                pg.display.flip()
                # remove highlighted move
                # remove_highlight(best_move, display_surface)

                # update the board

                # change player turn
                player_turn = player_turn + 1

                # check if the player has won
                game_over = check_win(set_pieces, obj_set)

                if game_over:

                    if player_turn == 1:
                        p1_win = p1_win + 1
                        times += 1
                    if player_turn == 2:
                        p2_win = p2_win + 1
                        times += 1
                    if player_turn == 3:
                        p3_win = p3_win + 1
                        times += 1
                    if player_turn == 4:
                        p4_win = p4_win + 1
                        times += 1
                    if player_turn == 5:
                        p5_win = p5_win + 1
                        times += 1
                    if player_turn == 6:
                        p6_win = p6_win + 1
                        times += 1

                    print('time:', times)
                    print('Player 1 wins:', p1_win)
                    print('Player 2 wins:', p2_win)
                    print('Player 3 wins:', p3_win)
                    print('Player 4 wins:', p4_win)
                    print('Player 5 wins:', p5_win)
                    print('Player 6 wins:', p6_win)
                    print('[]------------------[]')
                    run_game()
                    main()

                    event = pg.event.Event(restart_game)
                    pg.event.post(event)

                else:

                    event = pg.event.Event(next_move)
                    pg.event.post(event)

                    # pg.display.update()

def get_clicked_cell(mouse_x, mouse_y):
    # 计算行数
    row = int((mouse_y - V_MARGIN_DISTANCE) // (CIRCLE_DIAMETER + V_SPACING))

    # 计算列数
    if row % 2 == 0:
        col = int((mouse_x - H_MARGIN_DISTANCE) // (CIRCLE_DIAMETER + H_SPACING))
    else:
        col = int((mouse_x - H_MARGIN_DISTANCE - (CIRCLE_DIAMETER+ H_SPACING) / 2) // (CIRCLE_DIAMETER + H_SPACING))

    return row, col

def run_game():
    pygame.init()#初始化背景设置
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption('跳棋游戏')
    bg_color = (135,206,235)#设置背景色，天青蓝
    background = pygame.image.load('death.jpg')
    background = pygame.transform.scale(background,(800,600))

    while True:
        screen.blit(background,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:#检测玩家单击游戏窗口关闭按钮
                sys.exit()#退出游戏

        #每次循环时都重绘屏幕
        #screen.fill(bg_color)
        #让最近绘制的屏幕可见
        pygame.display.flip()

if __name__ == '__main__':
    main()
