from game import *
import pygame
from copy import copy, deepcopy

## Beginning concrete code

DIRS = L, R, U, D = range(4)
DIR_KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

def opp_dir(d):
    mapping = [R, L, D, U]
    return mapping[d]

def dir_str(d):
    mapping = ["L", "R", "U", "D"]
    return mapping[d]

# Grid position
class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def pos_in_dir(self, dir):
            ret = deepcopy(self)
            if dir == L:
                ret.x -= 1
            elif dir == R:
                ret.x += 1
            elif dir == U:
                ret.y -= 1
            elif dir == D:
                ret.y += 1
            return ret

    @staticmethod
    def top_left(x_offset = 0):
        return Pos(x_offset, 0)

class Grid:
    def __init__(self, n):
        self.n = n

class Snake:
    def __init__(self, start_pos = Pos.top_left(5), start_len = 5, start_dir = R):
        # XXX: There should be some check of boundaries for this
        self.len = start_len
        self.pos = self.orient_head(start_pos, start_dir)
        self.print_pos()
        self.dir = start_dir

    def orient_head(self, head_pos, dir):
        ret = [None for i in range(self.len)]
        # set head position
        ret[0] = head_pos
        opp_d = opp_dir(dir)
        for i in range(1, self.len):
            ret[i] = ret[i-1].pos_in_dir(opp_d)
            print ret[i].x, ret[i].y
        return ret

    def print_pos(self):
        print [(p.x, p.y) for p in self.pos]

    def grow(self):
        ### XXX: I can see already bugs coming up when there is not enough space to grow
        self.len +=1
        after_tail_pos = self.pos[self.len-2].pos_in_dir(opp_dir(self.dir))
        self.pos.append(after_tail_pos)


    def move(self, dir):
        # This function assumes it can move in the next pos
        prev_blk_pos = self.pos[0]
        self.pos[0] = prev_blk_pos.pos_in_dir(dir)
        for i in range(1, self.len):
            # swap
            self.pos[i], prev_blk_pos = prev_blk_pos, self.pos[i]

class SnakeModel(Model):
    def __init__(self, n):
        self.n = n
        self.grid = Grid(n)
        self.snake = Snake()

        self.food = None

    def move_snake(self, dir):
        if dir not in DIRS:
            raise Exception('Direction not valid')

        self.snake.move(dir)

    def keep_moving_snake(self):
        self.move_snake(self.snake.dir)

    def steer_snake(self, dir):
        mylog("Steering snake towards " + dir_str(dir))
        self.snake.dir = dir

    def mk_food_at_pos(self, x, y):
        self.food = Pos(x,y)

    def is_snake_out(self):
        return self.snake.pos[0].x >= self.n or self.snake.pos[0].x < 0 \
            or  self.snake.pos[0].y >= self.n or self.snake.pos[0].y < 0

    def let_snake_cross(self):
        if self.snake.dir == R:
            self.snake.pos[0].x = 0
        if self.snake.dir == L:
            self.snake.pos[0].x = self.n-1
        if self.snake.dir == U:
            self.snake.pos[0].y = self.n-1
        if self.snake.dir == D:
            self.snake.pos[0].y = 0
        #self.snake.pos[0].y += 1
        #self.snake.pos[0].y %= self.n

    def snake_on_food(self):
        if self.food is None: return False
        print "SNAKE AND FOOD: ", self.snake.pos[0].x, self.snake.pos[0].y, self.food.x, self.food.y
        return self.snake.pos[0] == self.food

    def snake_eats_food(self):
        self.food = None
        self.snake.grow()

class SnakeView(View):
    BLOCK_SZ = 8
    LINE_SZ = 2

    BLOCK_COLOR = (30,30,30) # very dark
    LINE_COLOR = (0, 128, 255) # blue
    SNAKE_COLOR = (255, 100, 0) # orange?
    BKGRND_COLOR = (0,0,0)

    FOOD_COLOR = (57, 255, 20)

    def __init__(self, n):
        # |-|-|...|-|
        # TOT_SZ = BLOCK_interiors + lines
        # TOT_SZ = BLOCK_SZ*n + (n + 1)
        self.real_size = self.BLOCK_SZ*n + self.LINE_SZ*(n+1)
        self.n = n
        self.screen = \
            pygame.display.set_mode((self.real_size, self.real_size))



    # interior top-left corner of block
    def top_left_block(self, pos):
        x = self.BLOCK_SZ*pos.x + self.LINE_SZ*(pos.x+1)
        y = self.BLOCK_SZ*pos.y + self.LINE_SZ*(pos.y+1)
        return (x, y)

    def draw_block(self, pos, color):
        x, y = self.top_left_block(pos)
        pygame.draw.rect(self.screen, color,
            pygame.Rect(x, y, self.BLOCK_SZ, self.BLOCK_SZ))

    def draw_snake(self, snake):
        for p in snake.pos:
            self.draw_block(p, self.SNAKE_COLOR)

    def draw_hline(self, y):
        pygame.draw.line(self.screen, self.LINE_COLOR,
            (0, y), (self.real_size-1, y), self.LINE_SZ )

    def draw_vline(self, x):
        pygame.draw.line(self.screen, self.LINE_COLOR,
            (x,0), (x, self.real_size-1), self.LINE_SZ )

    def draw_grid(self):
        # hlines
        y = 0
        while y < self.real_size:
            self.draw_hline(y)
            y += self.BLOCK_SZ+self.LINE_SZ

        # vlines
        x = 0
        while x < self.real_size:
            self.draw_vline(x)
            x += self.BLOCK_SZ+self.LINE_SZ

    def draw_food(self, fd):
        if fd is not None:
            self.draw_block(fd, self.FOOD_COLOR)

    def update_from_model(self, model):
        #mylog("Calling update_from_model")
        model.snake.print_pos()
        self.screen.fill(self.BKGRND_COLOR)
        self.draw_grid()
        self.draw_snake(model.snake)
        self.draw_food(model.food)

        pygame.display.flip()




# helper for pygame trigger functions
def pygame_trigger_e(type, key = None):
    checker_fn = None
    if key is None:
        checker_fn = lambda e: e.type == type
    else:
        checker_fn = lambda e: e.type == type and e.key == key

    return lambda ctx: any([checker_fn(e) for e in ctx["pygame_events"]])

def pygame_trigger_kp(key):
    return lambda ctx: ctx["pressed"][key]

def always_in_game(game):
    return lambda ignored: not game.is_over

class SnakeGame(Game):
    N = 20

    def __init__(self):
        # super.init?
        Game.__init__(self)
        self.model = SnakeModel(self.N)
        self.view = SnakeView(self.N)

        # Quit action
        self.add_action(
            pygame_trigger_e(pygame.KEYDOWN, pygame.K_SPACE),
            lambda ignored: self.quit())

        mk_steerer = lambda steer_dir: lambda mdl: mdl.steer_snake(steer_dir)
        # make snake move in the right direction
        for d in DIRS:
            self.add_action(
                pygame_trigger_e(pygame.KEYDOWN, DIR_KEYS[d]),
                mk_steerer(d),
                "action trigger for " + dir_str(d)
            )

        # move snake wherever it is going
        self.add_event(
            always_in_game(self),
            lambda mdl: mdl.keep_moving_snake()
        )

        # make snake go overboard
        self.add_event(
            lambda mdl: mdl.is_snake_out(),
            lambda mdl: mdl.let_snake_cross()
        )

        # make food
        self.add_event(
            lambda mdl: mdl.is_snake_out() and mdl.food is None,
            lambda mdl: mdl.mk_food_at_pos(4, 4)
        )

        self.add_event(
            lambda mdl: mdl.snake_on_food(),
            lambda mdl: mdl.snake_eats_food()
        )




    def get_actions_ctx(self):
        return {
        "pygame_events" : pygame.event.get(),
        "pressed" : pygame.key.get_pressed()
        }
