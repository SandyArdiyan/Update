import tkinter as tk
import random

class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.size = 10
        self.speed = 6
        self.direction = [random.choice([-1, 1]), -1]  # Moving diagonally up-right
        self.item = canvas.create_oval(x - self.size, y - self.size,
                                       x + self.size, y + self.size,
                                       fill='blue')
    
    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Bounce off the walls
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1

        # Ball falls below the screen
        if coords[3] >= height:
            return "Game Over"

        # Move the ball
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)
        return None

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, dx, dy):
        self.canvas.move(self.item, dx, dy)

    def collide(self, objects):
        for obj in objects:
            if isinstance(obj, Brick):
                obj.hit()
                self.direction[1] *= -1  # Bounce off the brick
            elif isinstance(obj, Paddle):
                self.direction[1] *= -1  # Bounce off the paddle


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.width = 100
        self.height = 20
        self.item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                             x + self.width / 2, y + self.height / 2,
                                             fill="green")

    def move(self, dx):
        coords = self.canvas.coords(self.item)
        if coords[0] + dx >= 0 and coords[2] + dx <= self.canvas.winfo_width():
            self.canvas.move(self.item, dx, 0)

    def set_ball(self, ball):
        self.ball = ball

    def get_position(self):
        return self.canvas.coords(self.item)


class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.canvas.delete(self.item)
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)


# Create the Tkinter window
root = tk.Tk()
game = Game(root)
game.mainloop()
