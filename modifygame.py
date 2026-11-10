#Implementasi OOP di GUI programming

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
    def __init__(self, canvas, x, y, speed=5):
        self.radius = 9

        # Menentukan arah awal bola secara acak
        self.dx = random.choice([-1, 1]) * speed * 0.7
        self.dy = -speed * 0.7
        self.speed = speed

        item = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill="#ffffff",
            outline=""
        )

        super().__init__(canvas, item)

    def update(self):
        self.move(self.dx, self.dy)

        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] <= 0 and self.dx < 0:
            self.dx *= -1

        if coords[2] >= width and self.dx > 0:
            self.dx *= -1

        if coords[1] <= 0 and self.dy < 0:
            self.dy *= -1

    def bounce(self):
        self.dy *= -1

    # Mengatur arah pantulan bola berdasarkan posisi benturan paddle
    def hit_paddle(self, paddle):
        ball = self.get_position()
        pad = paddle.get_position()

        ball_center = (ball[0] + ball[2]) / 2
        paddle_center = (pad[0] + pad[2]) / 2

        offset = (ball_center - paddle_center) / (paddle.width / 2)

        self.dx = offset * self.speed
        self.dy = -abs(self.dy)

    # meningkatkan kecepatan bola
    def increase_speed(self):
        self.speed += 0.5

        current = (self.dx ** 2 + self.dy ** 2) ** 0.5

        if current:
            self.dx = self.dx / current * self.speed
            self.dy = self.dy / current * self.speed


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 12

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill="#00e5ff",
            outline=""
        )

        super().__init__(canvas, item)

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        # Mencegah paddle keluar dari area permainan
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)

class Brick(GameObject):

    # warna bata dibedakan berdasarkan jumlah ketahanannya
    COLORS = {
        1: "#00e676",
        2: "#ffca28",
        3: "#ff5252",
        4: "#ab47bc"
    }

    def __init__(self, canvas, x, y, hits):
        self.width = 65
        self.height = 20
        self.hits = hits

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=self.COLORS[hits],
            outline="#171c2c",
            width=2,
            tags="brick"
        )

        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1

        # Bata dihapus jika ketahanannya sudah habis
        if self.hits <= 0:
            self.delete()
            return True

        # Mengubah warna bata sesuai sisa ketahanan
        self.canvas.itemconfig(
            self.item,
            fill=self.COLORS[self.hits]
        )

        return False

class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.width = 700
        self.height = 500

        # menambahkan sistem skor, nyawa, dan level
        self.score = 0
        self.lives = 3
        self.level = 1

        self.running = False
        self.state = "menu"

        # Mengubah tampilan area permainan menjadi lebih modern
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#111827",
            highlightthickness=0
        )

        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = None

        # Kontrol paddle menggunakan tombol panah kiri dan kanan
        self.canvas.bind(
            "<Left>",
            lambda event: self.paddle.move(-25)
            if self.paddle and self.state == "playing" else None
        )

        self.canvas.bind(
            "<Right>",
            lambda event: self.paddle.move(25)
            if self.paddle and self.state == "playing" else None
        )

        # Memulai permainan menggunakan tombol Space
        self.canvas.bind(
            "<space>",
            lambda event: self.start_game()
            if self.state == "menu" else None
        )

        self.canvas.bind("<Button-1>", self.handle_click)

        self.canvas.focus_set()

        # Menampilkan menu utama ketika program dijalankan
        self.show_menu()

    def clear_screen(self):
        self.running = False
        self.canvas.delete("all")
        self.items.clear()

    # Menu utama permainan
    def show_menu(self):
        self.clear_screen()
        self.state = "menu"

        self.canvas.create_text(
            350, 120,
            text="BREAKOUT",
            fill="#00e5ff",
            font=("Arial", 42, "bold")
        )

        self.canvas.create_text(
            350, 185,
            text="Destroy all the bricks!",
            fill="white",
            font=("Arial", 16)
        )

        # Membuat tombol Start Game
        self.canvas.create_rectangle(
            245, 250, 455, 315,
            fill="#00bcd4",
            outline="",
            tags="start_button"
        )

        self.canvas.create_text(
            350, 282,
            text="START GAME",
            fill="white",
            font=("Arial", 20, "bold"),
            tags="start_button"
        )

        self.canvas.create_text(
            350, 370,
            text="Use LEFT and RIGHT arrows to move",
            fill="#aaaaaa",
            font=("Arial", 13)
        )

        self.canvas.create_text(
            350, 400,
            text="Press SPACE to start",
            fill="#aaaaaa",
            font=("Arial", 12)
        )

    # Mengatur fungsi tombol yang diklik menggunakan mouse
    def handle_click(self, event):
        if self.state == "menu":

            items = self.canvas.find_overlapping(
                event.x, event.y, event.x, event.y
            )

            if any("start_button" in self.canvas.gettags(item)
                   for item in items):
                self.start_game()

        elif self.state in ("gameover", "win"):

            items = self.canvas.find_overlapping(
                event.x, event.y, event.x, event.y
            )

            if any("restart_button" in self.canvas.gettags(item)
                   for item in items):
                self.restart_game()

    def start_game(self):
        if self.state != "menu":
            return

        self.score = 0
        self.lives = 3
        self.level = 1

        self.start_level()

    # Membuat objek permainan pada setiap level
    def start_level(self):
        self.clear_screen()
        self.state = "playing"

        self.paddle = Paddle(
            self.canvas,
            self.width / 2,
            455
        )

        self.ball = Ball(
            self.canvas,
            self.width / 2,
            430,
            speed=5 + self.level * 0.7
        )

        self.create_bricks()
        self.update_hud()

        self.running = True
        self.game_loop()

    # Sistem bata bertingkat berdasarkan level
    def create_bricks(self):
        rows = min(3 + self.level, 7)
        columns = 9

        for row in range(rows):
            for col in range(columns):
                x = 70 + col * 70
                y = 65 + row * 28

                # Ketahanan bata meningkat pada level tertentu
                hits = min(
                    1 + row // 2 + self.level // 3,
                    4
                )

                brick = Brick(self.canvas, x, y, hits)
                self.items[brick.item] = brick

    # Menampilkan skor, level, dan jumlah nyawa
    def update_hud(self):
        self.canvas.create_text(
            80, 20,
            text=f"Score: {self.score}",
            fill="white",
            font=("Arial", 14, "bold"),
            tags="hud"
        )

        self.canvas.create_text(
            350, 20,
            text=f"LEVEL: {self.level}",
            fill="#00e5ff",
            font=("Arial", 14, "bold"),
            tags="hud"
        )

        self.canvas.create_text(
            610, 20,
            text=f"Lives: {self.lives}",
            fill="#ffca28",
            font=("Arial", 14, "bold"),
            tags="hud"
        )

    def refresh_hud(self):
        self.canvas.delete("hud")
        self.update_hud()

    # Memeriksa tabrakan antara bola, bata, dan paddle
    def check_collisions(self):
        ball_coords = self.ball.get_position()

        overlapping = self.canvas.find_overlapping(
            *ball_coords
        )

        objects = [
            self.items[item]
            for item in overlapping
            if item in self.items
        ]

        # Memeriksa tabrakan dengan paddle
        if self.paddle.item in overlapping:
            paddle_coords = self.paddle.get_position()

            if self.ball.dy > 0:
                ball_bottom = ball_coords[3]

                if ball_bottom >= paddle_coords[1]:
                    self.ball.hit_paddle(self.paddle)

        # Memeriksa tabrakan dengan bata
        for obj in objects:
            if isinstance(obj, Brick):

                destroyed = obj.hit()

                # Menambahkan 10 poin setiap kali bata terkena bola
                self.score += 10

                # Bonus 20 poin jika bata berhasil dihancurkan
                if destroyed:
                    self.score += 20

                self.ball.bounce()
                self.refresh_hud()
                break

    # Mengatur jalannya permainan secara berulang
    def game_loop(self):
        if not self.running:
            return

        self.ball.update()
        self.check_collisions()

        # Memeriksa apakah seluruh bata sudah dihancurkan
        if len(self.canvas.find_withtag("brick")) == 0:
            self.next_level()
            return

        # Mengurangi nyawa jika bola jatuh
        if self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            self.refresh_hud()

            if self.lives <= 0:
                self.game_over()
            else:
                self.reset_ball()

            return

        # Mengulang game loop setiap 20 milidetik
        self.after(20, self.game_loop)

    # Membuat bola baru jika bola sebelumnya jatuh
    def reset_ball(self):
        if self.ball:
            self.ball.delete()

        self.ball = Ball(
            self.canvas,
            self.width / 2,
            430,
            speed=5 + self.level * 0.7
        )

        self.after(1000, self.game_loop)

    # Sistem perpindahan ke level berikutnya
    def next_level(self):
        self.running = False
        self.level += 1

        # Pemain menang jika berhasil menyelesaikan level 5
        if self.level > 5:
            self.win_game()
            return

        self.canvas.create_text(
            350, 250,
            text=f"LEVEL {self.level - 1} COMPLETE!",
            fill="#00e676",
            font=("Arial", 28, "bold")
        )

        self.after(1500, self.start_level)

    # Menampilkan layar Game Over
    def game_over(self):
        self.running = False
        self.state = "gameover"

        self.canvas.create_rectangle(
            100, 150, 600, 350,
            fill="#1f2937",
            outline="#ff5252",
            width=3
        )

        self.canvas.create_text(
            350, 205,
            text="GAME OVER",
            fill="#ff5252",
            font=("Arial", 35, "bold")
        )

        self.canvas.create_text(
            350, 255,
            text=f"Final Score: {self.score}",
            fill="white",
            font=("Arial", 18)
        )

        self.draw_restart_button()

    # Menampilkan layar kemenangan
    def win_game(self):
        self.running = False
        self.state = "win"

        self.canvas.create_rectangle(
            100, 150, 600, 350,
            fill="#1f2937",
            outline="#00e676",
            width=3
        )

        self.canvas.create_text(
            350, 205,
            text="YOU WIN!",
            fill="#00e676",
            font=("Arial", 35, "bold")
        )

        self.canvas.create_text(
            350, 255,
            text=f"Final Score: {self.score}",
            fill="white",
            font=("Arial", 18)
        )

        self.draw_restart_button()

    # Membuat tombol untuk mengulang permainan
    def draw_restart_button(self):
        self.canvas.create_rectangle(
            240, 290, 460, 330,
            fill="#00bcd4",
            outline="",
            tags="restart_button"
        )

        self.canvas.create_text(
            350, 310,
            text="PLAY AGAIN",
            fill="white",
            font=("Arial", 16, "bold"),
            tags="restart_button"
        )

    # Mengembalikan skor, nyawa, dan level ke kondisi awal
    def restart_game(self):
        self.score = 0
        self.lives = 3
        self.level = 1

        self.start_level()

# Program utama
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Breakout - Modified Edition")
    root.resizable(False, False)

    game = Game(root)

    root.mainloop()
