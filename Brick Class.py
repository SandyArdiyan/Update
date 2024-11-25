import tkinter as tk
import random

class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [random.choice([-1, 1]), -1]
        self.speed = 5
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Pantulan bola di dinding
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1

        # Jika bola keluar dari bawah (Game Over)
        if coords[3] >= height:
            return "Game Over"

        # Pergerakan bola
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)
        return None

    def collide(self, game_object):
        coords = self.get_position()
        obj_coords = game_object.get_position()

        if (coords[2] >= obj_coords[0] and coords[0] <= obj_coords[2] and
                coords[3] >= obj_coords[1] and coords[1] <= obj_coords[3]):
            self.direction[1] *= -1
            return True
        return False


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 10
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill='orange')
        super().__init__(canvas, item)

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)


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
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class BrickBreakerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Brick Breaker")
        self.canvas = tk.Canvas(root, width=500, height=400, bg="black")
        self.canvas.pack()

        self.paddle = Paddle(self.canvas, 250, 350)
        self.ball = Ball(self.canvas, 250, 340)
        self.bricks = []
        self.score = 0
        self.level = 1

        self.create_bricks()
        self.bind_controls()
        self.update_speed = 50

    def create_bricks(self):
        colors = ['red', 'blue', 'green', 'yellow']
        for i in range(5 + self.level):  # Increase number of rows based on level
            for j in range(7):
                x = 50 + j * 70
                y = 30 + i * 30
                brick = Brick(self.canvas, x, y, random.choice([1, 2, 3]))
                self.bricks.append(brick)

    def bind_controls(self):
        self.root.bind("<Left>", lambda event: self.paddle.move(-20))
        self.root.bind("<Right>", lambda event: self.paddle.move(20))

    def game_loop(self):
        result = self.ball.update()

        if result == "Game Over":
            self.canvas.create_text(250, 200, text="GAME OVER", fill="red", font=("Arial", 24))
            return

        # Deteksi tabrakan dengan paddle
        if self.ball.collide(self.paddle):
            self.ball.speed += 0.1

        # Deteksi tabrakan dengan balok
        for brick in self.bricks:
            if self.ball.collide(brick):
                brick.hit()  # Decrease hit on brick and update color
                self.score += 10
                break

        # Tampilkan skor
        self.canvas.delete("score")
        self.canvas.create_text(50, 10, text=f"Score: {self.score}", fill="white", font=("Arial", 14), tag="score")

        # Menang jika semua balok hancur
        if not self.bricks:
            self.level += 1  # Move to next level
            self.canvas.create_text(250, 200, text="LEVEL UP!", fill="green", font=("Arial", 24))
            self.canvas.after(1000, self.next_level)

        # Lanjutkan game loop
        self.root.after(self.update_speed, self.game_loop)

    def next_level(self):
        self.create_bricks()  # Create new bricks for the next level
        self.ball = Ball(self.canvas, 250, 340)  # Reset the ball position
        self.canvas.delete("level_up")  # Remove level up text


def main():
    root = tk.Tk()
    game = BrickBreakerGame(root)
    game.game_loop()
    root.mainloop()


if __name__ == "__main__":
    main()
