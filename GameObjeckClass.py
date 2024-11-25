import tkinter as tk
import random

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 15
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2, x + self.width / 2, y + self.height / 2, fill="#FF6347")
        super().__init__(canvas, item)

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)


class Ball(GameObject):
    def __init__(self, canvas, x, y, speed=5):
        self.radius = 15
        self.direction = [random.choice([-1, 1]), -1]  # Ball direction
        self.speed = speed
        item = canvas.create_oval(x - self.radius, y - self.radius, x + self.radius, y + self.radius, fill="white")
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1  # Bounce off walls

        if coords[1] <= 0:
            self.direction[1] *= -1  # Bounce off top wall

        if coords[3] >= height:
            # Game over logic
            self.canvas.create_text(width / 2, height / 2, text="Game Over", fill="red", font=("Arial", 24))
            self.canvas.after(1000, self.canvas.quit)  # Quit game after 1 second
            return

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)


class Brick(GameObject):
    def __init__(self, canvas, x, y, width=60, height=20):
        self.width = width
        self.height = height
        item = canvas.create_rectangle(x, y, x + width, y + height, fill="lightgreen")
        super().__init__(canvas, item)


class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=500, height=500, bg="black")
        self.canvas.pack()

        self.paddle = Paddle(self.canvas, 250, 480)
        self.ball = Ball(self.canvas, 250, 250)

        self.bricks = []
        self.create_bricks()

        self.level = 1
        self.score = 0

        self.root.bind("<Left>", lambda event: self.paddle.move(-20))
        self.root.bind("<Right>", lambda event: self.paddle.move(20))

        self.game_loop()

    def create_bricks(self):
        self.bricks.clear()
        for i in range(6):  # Increase number of rows
            for j in range(8):  # Increase number of columns
                self.bricks.append(Brick(self.canvas, 60 * j + 10, 30 * i + 10))

    def game_loop(self):
        self.ball.update()

        # Check for collisions with paddle
        ball_coords = self.ball.get_position()
        paddle_coords = self.paddle.get_position()

        if ball_coords[2] > paddle_coords[0] and ball_coords[0] < paddle_coords[2]:
            if ball_coords[3] > paddle_coords[1] and ball_coords[1] < paddle_coords[3]:
                self.ball.direction[1] *= -1  # Bounce ball off paddle

        # Check for collisions with bricks
        for brick in self.bricks[:]:
            brick_coords = brick.get_position()
            if ball_coords[2] > brick_coords[0] and ball_coords[0] < brick_coords[2]:
                if ball_coords[3] > brick_coords[1] and ball_coords[1] < brick_coords[3]:
                    self.canvas.delete(brick.item)
                    self.bricks.remove(brick)
                    self.score += 10  # Increase score when brick is hit
                    self.ball.direction[1] *= -1  # Bounce ball off brick

        # Check if all bricks are destroyed, move to next level
        if not self.bricks:
            self.level += 1
            self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2,
                                    text="Level " + str(self.level), fill="yellow", font=("Arial", 24))
            self.canvas.after(1000, self.next_level)

        # Update score
        self.canvas.delete("score")
        self.canvas.create_text(10, 10, text="Score: " + str(self.score), fill="white", font=("Arial", 14), anchor="nw", tags="score")

        self.root.after(10, self.game_loop)  # Keep updating the game loop

    def next_level(self):
        self.create_bricks()  # Create new bricks for the next level
        self.ball = Ball(self.canvas, 250, 250, speed=self.ball.speed + 1)  # Increase ball speed
        self.canvas.delete("level_text")  # Remove level text


def main():
    root = tk.Tk()
    root.title("Brick Breaker Game")
    game = Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
