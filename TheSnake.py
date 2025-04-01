import tkinter
import random
import os
import json
from tkinter import messagebox

ROWS = 25
COLS = 25
TILE_SIZE = 25

WINDOW_WIDTH = TILE_SIZE * COLS
WINDOW_HEIGHT = TILE_SIZE * ROWS

HIGH_SCORE_FILE = "highscore.txt"
SETTINGS_FILE = "settings.json"

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Game window
window = tkinter.Tk()
window.title("TheSnake")
window.resizable(False, False)

canvas = tkinter.Canvas(window, bg="black", width=WINDOW_WIDTH, height=WINDOW_HEIGHT, borderwidth=0, highlightthickness=0)
canvas.pack()

# Initialize game variables
snake = Tile(TILE_SIZE * 5, TILE_SIZE * 5)
food = Tile(TILE_SIZE * 10, TILE_SIZE * 10)
velocityX = 0
velocityY = 0
snake_body = []
game_over = False
score = 0
high_score = 0
game_speed = 100
timer_id = None
snake_color = 'lime green'
current_mode = 'dark'
in_settings = False
current_widgets = []

# Default key bindings
key_bindings = {
    'up': 'w',
    'down': 's',
    'left': 'a',
    'right': 'd'
}

def load_high_score():
    global high_score
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            high_score = int(file.read())
    else:
        high_score = 0

def save_high_score():
    global high_score
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(high_score))

def load_settings():
    global snake_color, key_bindings, current_mode
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            snake_color = settings.get("snake_color", "lime green")
            key_bindings = settings.get("key_bindings", key_bindings)
            current_mode = settings.get("current_mode", "dark")

def save_settings():
    settings = {
        "snake_color": snake_color,
        "key_bindings": key_bindings,
        "current_mode": current_mode
    }
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)

def reset_game():
    global snake, food, velocityX, velocityY, snake_body, game_over, score, timer_id
    if timer_id is not None:
        window.after_cancel(timer_id)
    snake = Tile(TILE_SIZE * 5, TILE_SIZE * 5)
    food = Tile(TILE_SIZE * 10, TILE_SIZE * 10)
    velocityX = 0
    velocityY = 0
    snake_body.clear()
    game_over = False
    score = 0
    draw()

def change_direction(e):
    global velocityX, velocityY, game_over
    if e.keysym == "r" and game_over:
        reset_game()
        return
    if e.keysym == "Escape":
        window.attributes("-fullscreen", False)
        return
    if game_over:
        return
    if e.keysym == key_bindings['up'] and velocityY != 1:
        velocityX = 0
        velocityY = -1
    elif e.keysym == key_bindings['down'] and velocityY != -1:
        velocityX = 0
        velocityY = 1
    elif e.keysym == key_bindings['left'] and velocityX != 1:
        velocityX = -1
        velocityY = 0
    elif e.keysym == key_bindings['right'] and velocityX != -1:
        velocityX = 1
        velocityY = 0

def move():
    global snake, food, snake_body, game_over, score, high_score
    if game_over or in_settings:
        return
    if snake.x < 0 or snake.x >= WINDOW_WIDTH or snake.y < 0 or snake.y >= WINDOW_HEIGHT:
        game_over = True
        if score > high_score:
            high_score = score
            save_high_score()
        return
    for tile in snake_body:
        if snake.x == tile.x and snake.y == tile.y:
            game_over = True
            if score > high_score:
                high_score = score
                save_high_score()
            return
    if snake.x == food.x and snake.y == food.y:
        snake_body.append(Tile(food.x, food.y))
        food.x = random.randint(0, COLS - 1) * TILE_SIZE
        food.y = random.randint(0, ROWS - 1) * TILE_SIZE
        score += 1
    for i in range(len(snake_body) - 1, -1, -1):
        tile = snake_body[i]
        if i == 0:
            tile.x = snake.x
            tile.y = snake.y
        else:
            prev_tile = snake_body[i - 1]
            tile.x = prev_tile.x
            tile.y = prev_tile.y
    snake.x += velocityX * TILE_SIZE
    snake.y += velocityY * TILE_SIZE

def draw():
    global snake, food, snake_body, game_over, score, timer_id, snake_color
    if in_settings:
        return

    move()
    canvas.delete("all")

    # Draw food
    canvas.create_rectangle(food.x, food.y, food.x + TILE_SIZE, food.y + TILE_SIZE, fill='red')

    # Draw snake head with eyes and tongue based on direction
    canvas.create_rectangle(snake.x, snake.y, snake.x + TILE_SIZE, snake.y + TILE_SIZE, fill=snake_color)

    eye_size = TILE_SIZE // 5
    tongue_size = TILE_SIZE // 4
    eye_offset = TILE_SIZE // 4
    tongue_offset = TILE_SIZE // 8

    if velocityX == 1:
        left_eye = (snake.x + eye_offset, snake.y + eye_offset)
        right_eye = (snake.x + eye_offset, snake.y + TILE_SIZE - eye_offset - eye_size)
        tongue = (snake.x + TILE_SIZE, snake.y + TILE_SIZE // 2, snake.x + TILE_SIZE + tongue_size, snake.y + TILE_SIZE // 2)
    elif velocityX == -1:
        left_eye = (snake.x + TILE_SIZE - eye_offset - eye_size, snake.y + eye_offset)
        right_eye = (snake.x + TILE_SIZE - eye_offset - eye_size, snake.y + TILE_SIZE - eye_offset - eye_size)
        tongue = (snake.x, snake.y + TILE_SIZE // 2, snake.x - tongue_size, snake.y + TILE_SIZE // 2)
    elif velocityY == 1:
        left_eye = (snake.x + eye_offset, snake.y + eye_offset)
        right_eye = (snake.x + TILE_SIZE - eye_offset - eye_size, snake.y + eye_offset)
        tongue = (snake.x + TILE_SIZE // 2, snake.y + TILE_SIZE, snake.x + TILE_SIZE // 2, snake.y + TILE_SIZE + tongue_size)
    else:
        left_eye = (snake.x + eye_offset, snake.y + TILE_SIZE - eye_offset - eye_size)
        right_eye = (snake.x + TILE_SIZE - eye_offset - eye_size, snake.y + TILE_SIZE - eye_offset - eye_size)
        tongue = (snake.x + TILE_SIZE // 2, snake.y, snake.x + TILE_SIZE // 2, snake.y - tongue_size)

    canvas.create_oval(left_eye[0], left_eye[1], left_eye[0] + eye_size, left_eye[1] + eye_size, fill='white')
    canvas.create_oval(right_eye[0], right_eye[1], right_eye[0] + eye_size, right_eye[1] + eye_size, fill='white')
    canvas.create_line(tongue[0], tongue[1], tongue[2], tongue[3], fill='red', width=2)

    for tile in snake_body:
        canvas.create_rectangle(tile.x, tile.y, tile.x + TILE_SIZE, tile.y + TILE_SIZE, fill=snake_color)

    if game_over:
        canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, font="Arial 20", text=f"Game Over: {score}", fill="grey")
        canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 30, font="Arial 12", text="Press 'R' to Restart", fill="grey")
    else:
        canvas.create_text(30, 20, font="Arial 10", text=f"Score: {score}", fill="grey")

    canvas.create_text(100, 20, font="Arial 10", text=f"High Score: {high_score}", fill="grey")
    canvas.create_text(WINDOW_WIDTH - 150, 30, font="Arial 18", text="𝕸𝖆𝖉𝖊 𝕭𝖞 𝕽𝖊𝖛𝖔𝖑𝖙 𝕽𝖊𝖆𝖑𝖒", fill="grey")

    timer_id = window.after(game_speed, draw)

def change_snake_color(color):
    global snake_color
    snake_color = color
    save_settings()
    draw()

def create_color_buttons(frame):
    button_white = tkinter.Button(frame, text="White", command=lambda: change_snake_color("white"), fg="black", bg="white")
    button_white.grid(row=0, column=0)

    button_blue = tkinter.Button(frame, text="Blue", command=lambda: change_snake_color("blue"), fg="black", bg="blue")
    button_blue.grid(row=0, column=1)

    button_pink = tkinter.Button(frame, text="Pink", command=lambda: change_snake_color("pink"), fg="black", bg="pink")
    button_pink.grid(row=0, column=2)

    button_green = tkinter.Button(frame, text="Green", command=lambda: change_snake_color("lime green"), fg="black", bg="green")
    button_green.grid(row=0, column=3)

    button_gray = tkinter.Button(frame, text="Grey", command=lambda: change_snake_color("gray"), fg="black", bg="gray")
    button_gray.grid(row=0, column=4)

    button_black = tkinter.Button(frame, text="Black", command=lambda: change_snake_color("black"), fg="white", bg="black")
    button_black.grid(row=0, column=5)

def toggle_mode():
    global current_mode
    if current_mode == 'dark':
        current_mode = 'light'
        canvas.config(bg='white')
    else:
        current_mode = 'dark'
        canvas.config(bg='black')
    save_settings()

def create_toggle_button(frame):
    mode_button = tkinter.Button(frame, text="Toggle Dark/Light Mode", command=toggle_mode)
    mode_button.grid(row=0, column=6)

def clear_widgets():
    global current_widgets
    for widget in current_widgets:
        widget.destroy()
    current_widgets.clear()

def update_key_bindings(up_key, down_key, left_key, right_key):
    global key_bindings
    key_bindings['up'] = up_key.get()
    key_bindings['down'] = down_key.get()
    key_bindings['left'] = left_key.get()
    key_bindings['right'] = right_key.get()
    save_settings()

def show_settings():
    global in_settings
    clear_widgets()
    canvas.delete("all")
    canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30, font="Arial 20", text="Settings", fill="grey")

    frame = tkinter.Frame(window, bg="black")
    frame.pack(side="bottom", pady=10)
    create_color_buttons(frame)
    create_toggle_button(frame)
    current_widgets.append(frame)

    key_frame = tkinter.Frame(window)
    key_frame.pack(side="bottom", pady=10)

    up_key_label = tkinter.Label(key_frame, text="Up Key: ")
    up_key_label.grid(row=0, column=0)
    up_key_entry = tkinter.Entry(key_frame)
    up_key_entry.insert(0, key_bindings['up'])
    up_key_entry.grid(row=0, column=1)

    down_key_label = tkinter.Label(key_frame, text="Down Key: ")
    down_key_label.grid(row=1, column=0)
    down_key_entry = tkinter.Entry(key_frame)
    down_key_entry.insert(0, key_bindings['down'])
    down_key_entry.grid(row=1, column=1)

    left_key_label = tkinter.Label(key_frame, text="Left Key: ")
    left_key_label.grid(row=2, column=0)
    left_key_entry = tkinter.Entry(key_frame)
    left_key_entry.insert(0, key_bindings['left'])
    left_key_entry.grid(row=2, column=1)

    right_key_label = tkinter.Label(key_frame, text="Right Key: ")
    right_key_label.grid(row=3, column=0)
    right_key_entry = tkinter.Entry(key_frame)
    right_key_entry.insert(0, key_bindings['right'])
    right_key_entry.grid(row=3, column=1)

    update_button = tkinter.Button(window, text="Update Keys", command=lambda: update_key_bindings(up_key_entry, down_key_entry, left_key_entry, right_key_entry))
    update_button.pack(side="bottom", pady=5)

    current_widgets.append(key_frame)
    current_widgets.append(update_button)

    back_button = tkinter.Button(window, text="Back", command=quit_settings)
    back_button.pack(side="top", pady=5)
    current_widgets.append(back_button)

    in_settings = True

def quit_settings():
    global in_settings
    in_settings = False
    clear_widgets()
    reset_game()

def show_support_message():
    messagebox.showinfo("Support Us", "We would greatly appreciate your support. If you'd like to make a contribution, please send Bitcoin to the following address: bc1qv7g893pqw327ahg53zfzzk9yfumdkxqt6y2n47. Thank you for your generosity!")

load_high_score()
load_settings()
window.bind("<Key>", change_direction)
window.protocol("WM_DELETE_WINDOW", lambda: (save_high_score(), save_settings(), window.destroy()))

settings_button = tkinter.Button(window, text="Settings", command=show_settings)
settings_button.pack(side="top", pady=5)

support_button = tkinter.Button(window, text="Support Us", command=show_support_message)
support_button.pack(side="top", pady=5)

reset_game()
window.mainloop()
