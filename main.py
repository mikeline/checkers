import pygame
import math


class Cell:
    def __init__(self, name, box, color, king):
        self.name = name
        self.box = box
        self.color = color
        self.king = king


class Rout:
    def __init__(self, track):
        self.track = track


class Counter:
    def __init__(self):
        self.value = 0


def draw_board(sc):
    for y in range(10):
        for x in range(10):
            if (x + y) % 2 == 0:
                pygame.draw.rect(sc, (0, 0, 0), (32 * x, 32 * y, 32, 32))
            else:
                pygame.draw.rect(sc, (255, 255, 255), (32 * x, 32 * y, 32, 32))


def draw_cells(sc, c, ch):
    for x in c:
        if x.color == 1:
            pygame.draw.circle(sc, (128, 128, 128), box_to_pos(x.box), 16)
            if x.king:
                sc.blit(crownImg, (box_to_pos(x.box)))
        elif x.color == 2:
            pygame.draw.circle(sc, (165, 42, 42), box_to_pos(x.box), 16)
            if x.king:
                sc.blit(crownImg, (box_to_pos(x.box)[0] - 16, box_to_pos(x.box)[1] - 16))
    if ch is not None:
        pygame.draw.circle(sc, (173, 216, 230), box_to_pos(index_to_box(ch)), 16, 2)


def benefit_ways(c, ch, wt):
    routs = []
    prev_index = 0
    index = 0
    next_index = 0
    count = 0
    no_ways = False
    if wt:
        enemy = 2
        direction = -1
    else:
        enemy = 1
        direction = 1
    # first step
    for i in range(-1, 2, 2):
        index = box_to_index((c[ch].box[0] + i, c[ch].box[1] + direction))
        if index is None:
            count += 1
            continue
        if c[index].color == 0:
            routs.append(Rout([index]))
        elif c[index].color == enemy:
            prev_index = index
            index = box_to_index((c[index].box[0] + i, c[index].box[1] + direction))
            if index is None or c[index].color != 0:
                count += 1
                continue
            if c[index].color == 0:
                routs.append(Rout([prev_index, index]))
    if count >= 2:
        return None
    # next steps
    i = 0
    while True:
        routs_to_add = []
        for r in routs[i:]:
            if len(r.track) < 2:
                continue
            prev_index = r.track[-1]
            for i in range(-1, 2, 2):
                for j in range(-1, 2, 2):
                    index = box_to_index((c[prev_index].box[0] + i, c[prev_index].box[1] + j))
                    if index is None or index == prev_index:
                        continue
                    else:
                        if c[index].color == enemy:
                            next_index = box_to_index((c[index].box[0] + i, c[index].box[1] + j))
                            if c[next_index].color == 0:
                                routs_to_add.append(Rout(r.track + [index, next_index]))
        if routs_to_add == []:
            break
        i += len(routs)
        routs = routs + routs_to_add
    max_ways = []
    maximum = 0
    for r in routs:
        if len(r.track) > maximum:
            maximum = len(r.track)
    for r in routs:
        if len(r.track) == maximum:
            t = []
            for index in r.track:
                if c[index].color == enemy:
                    pass
                else:
                    t.append(index)
            max_ways.append(t)
    return max_ways


def on_chosen(c, wt, pos, ch, w):
    touch_ind = box_to_index(pos_to_box(pos))
    if c[touch_ind].color == 1 and wt:
        ch = touch_ind
    elif c[touch_ind].color == 2 and not wt:
        ch = touch_ind
    if ch is not None:
        if not c[ch].king:
            w = benefit_ways(c, ch, wt)
    return ch, w


def on_way(c, wt, index, ch, w, mr):
    if c[ch].king:
        move_king(c, wt, ch, index)
        wt = not wt
        ch = None
        w = None
    else:
        mr.track.append(index)
        for x in w:
            if mr.track == x[:len(mr.track)]:
                move(c, wt, ch, index)
                ch = index
                if len(mr.track) == len(x):
                    if wt:
                        if index_to_box(index)[1] == 0:
                            c[index].king = True
                    else:
                        if index_to_box(index)[1] == 9:
                            c[index].king = True
                    wt = not wt
                    ch = None
                    w = None
                    mr.track = []
                break
        if ch != index and mr.track != []:
            mr.track.pop()
    return wt, ch, w


def move_king(c, wt, ch, index):
    if c[index].color == 0:
        ch_box = index_to_box(ch)
        ind_box = index_to_box(index)
        dx = ind_box[0] - ch_box[0]
        dy = ind_box[1] - ch_box[1]
        if wt:
            enemy = 2
        else:
            enemy = 1
        if math.fabs(dx) == math.fabs(dy):
            if dx > 0:
                i = 1
            else:
                i = -1
            if dy > 0:
                j = 1
            else:
                j = -1
            enemies_to_kill = []
            x = ch_box[0]
            y = ch_box[1]
            while x != ind_box[0]:
                x += i
                y += j
                if c[box_to_index((x, y))].color == enemy:
                    enemies_to_kill.append(box_to_index((x, y)))
            # check if there are two enemies in a row
            for k, en in enumerate(enemies_to_kill[1:]):
                if c[en].color == enemy and c[enemies_to_kill[k - 1]].color == enemy:
                    return
            # kill enemies
            for enemy in enemies_to_kill:
                c[enemy].color = 0
                if c[enemy].king:
                    c[enemy].king = False
            if wt:
                count_black.value += len(enemies_to_kill)
            else:
                count_white.value += len(enemies_to_kill)
            # move king
            c[index].color = c[ch].color
            c[index].king = True
            c[ch].color = 0
            c[ch].king = False


def move(c, wt, ch, index):
    # move the figure
    c[index].color = c[ch].color
    # clear the previous position
    c[ch].color = 0
    # remove an enemy if exists
    move_box = index_to_box(index)
    prev_box = index_to_box(ch)
    if math.fabs(move_box[0] - prev_box[0]) >= 2:
        if move_box[0] - prev_box[0] > 0:
            enemy_box0 = prev_box[0] + 1
        else:
            enemy_box0 = prev_box[0] - 1
        if move_box[1] - prev_box[1] > 0:
            enemy_box1 = prev_box[1] + 1
        else:
            enemy_box1 = prev_box[1] - 1
        c[box_to_index((enemy_box0, enemy_box1))].color = 0
        if wt:
            count_black.value += 1
        else:
            count_white.value += 1


def init_cells(c):
    for i in range(10):
        for j in range(10):
            # black
            if (i + j) % 2 == 0 and i < 4:
                c.append(Cell(chr(97 + j) + str(i), (j, i), 2, False))
            # white
            elif (i + j) % 2 == 0 and i > 5:
                c.append(Cell(chr(97 + j) + str(i), (j, i), 1, False))
            # empty
            else:
                c.append(Cell(chr(97 + j) + str(i), (j, i), 0, False))


def box_to_pos(b):
    return b[0] * 32 + 16, b[1] * 32 + 16


def pos_to_box(pos):
    return pos[0] // 32, pos[1] // 32


def box_to_index(b):
    if 10 * b[1] + b[0] < 0 or 10 * b[1] + b[0] > 99:
        return None
    return 10 * b[1] + b[0]


def index_to_box(ind):
    return ind % 10, ind // 10


def log(wt, ch):
    if wt:
        hero = 2
    else:
        hero = 1
    if ch is not None and cells[touch_index].color == hero:
        if wt:
            print("Black: " + cells[ch].name + '->' + cells[touch_index].name)
        else:
            print("White: " + cells[ch].name + '->' + cells[touch_index].name)
    if count_white.value == 20:
        print("Blacks have won")
        exit()
    elif count_black.value == 20:
        print("Whites have won")
        exit()


pygame.init()
screen = pygame.display.set_mode((320, 320))
global crownImg
crownImg = pygame.image.load('crown.png')
count_white = Counter()
count_black = Counter()
done = False
white_turn = True
cells = []
chosen = None
prev_chosen = None
way = []
my_rout = Rout([])
init_cells(cells)
clock = pygame.time.Clock()

while not done:
    draw_board(screen)
    draw_cells(screen, cells, chosen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONUP:
            touch_index = box_to_index(pos_to_box(event.pos))
            if my_rout.track == [] and cells[touch_index].color != 0:
                chosen, way = on_chosen(cells, white_turn, event.pos, chosen, way)
            elif chosen is not None:
                if way is not None or cells[chosen].king:
                    if touch_index is not None:
                        if cells[touch_index].color == 0:
                            prev_chosen = chosen
                            white_turn, chosen, way = on_way(cells, white_turn, touch_index, chosen, way, my_rout)
                            log(white_turn, prev_chosen)
    pygame.display.flip()
    clock.tick(60)



