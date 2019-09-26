from game import *
import pygame

## Beginning concrete code

DIRS = L, R, U, D = range(4)


# Grid position
class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def top_left():
        return Pos(0, 0)

class Grid:
    def __init__(self, n):
        self.n = n

class Snake:
    def __init__(self, start_pos = Pos.top_left(), start_len = 3 ):
        self.pos = start_pos
        self.len = start_len

    def move(self, dir):
        if dir == L:
            self.pos.x -= 1
        elif dir == R:
            self.pos.x += 1
        elif dir == U:
            self.pos.y -= 1
        elif dir == D:
            self.pos.y += 1


class SnakeModel(Model):
    def __init__(self, n):
        self.n = n
        self.grid = Grid(n)
        self.snake = Snake()

    def move_snake(self, dir):
        if dir not in DIRS:
            raise Exception('Direction not valid')

        self.snake.move(dir)

    def is_snake_out(self):
        return self.snake.pos.x >= self.n or self.snake.pos.x < 0 \
            or  self.snake.pos.y >= self.n or self.snake.pos.y < 0

    def lower_snake(self):
        self.snake.pos.x = 0
        self.snake.pos.y += 1
        self.snake.pos.y %= self.n

class SnakeView(View):
    BLOCK_SZ = 10
    LINE_SZ = 1

    BLOCK_COLOR = (30,30,30) # very dark
    LINE_COLOR = (0, 128, 255) # blue
    SNAKE_COLOR = (255, 100, 0) # orange?
    BKGRND_COLOR = (0,0,0)

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
        self.draw_block(snake.pos, self.SNAKE_COLOR)

    def update_from_model(self, model):
        mylog("Calling update_from_model")

        self.screen.fill(self.BKGRND_COLOR)
        self.draw_snake(model.snake)

        pygame.display.flip()




# helper for pygame trigger functions
def pygame_trigger(type, key = None):
    checker_fn = None
    if key is None:
        checker_fn = lambda e: e.type == type
    else:
        checker_fn = lambda e: e.type == type and e.key == key

    return lambda ctx: any([checker_fn(e) for e in ctx["pygame_events"]])

def always_in_game(game):
    return lambda ignored: not game.is_over

class SnakeGame(Game):
    N = 20
    def __init__(self):
        # super.init?
        Game.__init__(self)
        self.model = SnakeModel(self.N)
        self.view = SnakeView(self.N)

        # Quit event
        self.add_action(
            pygame_trigger(pygame.KEYDOWN, pygame.K_SPACE),
            lambda ignored: self.quit())

        # move snake towards the right
        self.add_event(
            always_in_game(self),
            lambda mdl: mdl.move_snake(R)
        )

        self.add_event(
            lambda mdl: mdl.is_snake_out(),
            lambda mdl: mdl.lower_snake()
        )

    def get_actions_ctx(self):
        return {
        "pygame_events" : pygame.event.get(),
        "pressed" : pygame.key.get_pressed()
        }
