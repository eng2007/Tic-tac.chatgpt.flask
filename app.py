from flask import Flask, render_template, request, jsonify, redirect, url_for
import random

app = Flask(__name__)

# Переменная, которая будет хранить игровое поле
board = [[('', ''), ('', ''), ('', '')], 
         [('', ''), ('', ''), ('', '')], 
         [('', ''), ('', ''), ('', '')]]
difficulty = "easy"  # Уровень сложности по умолчанию

# Размеры фигур: 'S' - маленький, 'M' - средний, 'L' - большой
sizes = {'S': 1, 'M': 2, 'L': 3}

# Функция для проверки победителя
def check_winner(board):
    for row in board:
        if row[0][0] == row[1][0] == row[2][0] != '':
            return row[0][0]
    for col in range(3):
        if board[0][col][0] == board[1][col][0] == board[2][col][0] != '':
            return board[0][col][0]
    if board[0][0][0] == board[1][1][0] == board[2][2][0] != '':
        return board[0][0][0]
    if board[0][2][0] == board[1][1][0] == board[2][0][0] != '':
        return board[0][2][0]
    return None

# Функция для хода компьютера (простой уровень)
def easy_move(board):
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j][0] == '']
    if empty_cells:
        move = random.choice(empty_cells)
        board[move[0]][move[1]] = ('O', 'S')

# Функция для хода компьютера (нормальный уровень)
def normal_move(board):
    for i in range(3):
        for j in range(3):
            if board[i][j][0] == '':
                board[i][j] = ('O', 'S')
                if check_winner(board) == 'O':
                    return
                board[i][j] = ('X', 'S')
                if check_winner(board) == 'X':
                    board[i][j] = ('O', 'S')
                    return
                board[i][j] = ('', '')
    easy_move(board)

# Функция для хода компьютера (экспертный уровень)
def minimax(board, is_maximizing):
    winner = check_winner(board)
    if winner == 'X':
        return -1
    elif winner == 'O':
        return 1
    elif all(board[i][j][0] != '' for i in range(3) for j in range(3)):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j][0] == '':
                    board[i][j] = ('O', 'S')
                    score = minimax(board, False)
                    board[i][j] = ('', '')
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j][0] == '':
                    board[i][j] = ('X', 'S')
                    score = minimax(board, True)
                    board[i][j] = ('', '')
                    best_score = min(score, best_score)
        return best_score

def expert_move(board):
    best_score = -float('inf')
    best_move = None
    for i in range(3):
        for j in range(3):
            if board[i][j][0] == '':
                board[i][j] = ('O', 'S')
                score = minimax(board, False)
                board[i][j] = ('', '')
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    if best_move:
        board[best_move[0]][best_move[1]] = ('O', 'S')

# Функция для хода компьютера в зависимости от уровня сложности
def computer_move(board, difficulty):
    if difficulty == "easy":
        easy_move(board)
    elif difficulty == "normal":
        normal_move(board)
    elif difficulty == "expert":
        expert_move(board)

@app.route("/", methods=["GET", "POST"])
def index():
    global board, difficulty
    if request.method == "POST":
        if "level" in request.form:
            difficulty = request.form["level"]
        return redirect(url_for("index"))
    return render_template("index.html", board=board, difficulty=difficulty, enumerate=enumerate)

@app.route("/move", methods=["POST"])
def move():
    global board
    data = request.json
    row = data["row"]
    col = data["col"]
    size = data["size"]
    if board[row][col][0] == '' or sizes[size] > sizes[board[row][col][1]]:
        board[row][col] = ('X', size)
        winner = check_winner(board)
        if winner:
            return jsonify({"winner": winner})
        if all(board[i][j][0] != '' for i in range(3) for j in range(3)):
            return jsonify({"winner": "Draw"})
        # Ход компьютера
        computer_move(board, difficulty)
        winner = check_winner(board)
        if winner:
            return jsonify({"winner": winner})
        if all(board[i][j][0] != '' for i in range(3) for j in range(3)):
            return jsonify({"winner": "Draw"})
    return jsonify({"board": board})

@app.route("/reset")
def reset():
    global board
    board = [[('', ''), ('', ''), ('', '')], 
             [('', ''), ('', ''), ('', '')], 
             [('', ''), ('', ''), ('', '')]]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
