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


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [random.choice([-1, 1]), -1]
        self.speed = 5
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super().__init__(canvas, item)

    def update(self, paddle, bricks, score_label, root):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Memantul dari dinding
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        elif coords[3] >= height:
            # Game Over
            self.canvas.create_text(width / 2, height / 2, text="Game Over",
                                    fill="red", font=("Arial", 24))
            self.canvas.after(2000, root.quit)  # Keluar setelah 2 detik
            return

        # Memantul dari paddle
        paddle_coords = paddle.get_position()
        if (coords[3] >= paddle_coords[1] and
                paddle_coords[0] <= coords[2] and
                paddle_coords[2] >= coords[0]):
            self.direction[1] *= -1

        # Memantul dari balok
        for brick in bricks:
            if self.collide(brick):
                bricks.remove(brick)
                brick.delete()
                self.direction[1] *= -1
                paddle.update_score(score_label)
                break

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, other):
        coords1 = self.get_position()
        coords2 = other.get_position()

        return not (coords1[2] < coords2[0] or
                    coords1[0] > coords2[2] or
                    coords1[3] < coords2[1] or
                    coords1[1] > coords2[3])


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 10
        self.score = 0
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill='orange')
        super().__init__(canvas, item)

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)

    def update_score(self, label):
        self.score += 10
        label.config(text=f"Score: {self.score}")


class Brick(GameObject):
    def __init__(self, canvas, x, y, color):
        self.width = 50
        self.height = 20
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=color, outline="white")
        super().__init__(canvas, item)


def main():
    root = tk.Tk()
    root.title("Brick Breaker")

    canvas = tk.Canvas(root, width=500, height=500, bg="black")
    canvas.pack()

    # Tambahkan skor
    score_label = tk.Label(root, text="Score: 0", font=("Arial", 14), bg="black", fg="white")
    score_label.pack()

    # Paddle
    paddle = Paddle(canvas, 250, 450)

    # Ball
    ball = Ball(canvas, 250, 300)

    # Balok
    bricks = []
    colors = ["red", "blue", "green", "yellow", "purple"]
    for row in range(5):
        for col in range(10):
            x = 50 + col * 50
            y = 50 + row * 20
            color = random.choice(colors)
            brick = Brick(canvas, x, y, color)
            bricks.append(brick)

    # Kontrol paddle
    def move_left(event):
        paddle.move(-20)

    def move_right(event):
        paddle.move(20)

    root.bind("<Left>", move_left)
    root.bind("<Right>", move_right)

    # Game loop
    def game_loop():
        if len(bricks) == 0:
            canvas.create_text(350, 350, text="You Win!", fill="green", font=("Arial", 24))
            return
        ball.update(paddle, bricks, score_label, root)
        root.after(50, game_loop)

    game_loop()
    root.mainloop()


if __name__ == "__main__":
    main()
