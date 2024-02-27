import sqlite3


def send(sender: int, recipient: int, amount: int):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, sender))
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, recipient))
    conn.commit()
    conn.close()


def add(user: int, amount: int):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user,))
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user))
    conn.commit()
    conn.close()


def create_user(user: int):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)', (user, 200))
    conn.commit()
    conn.close()


def balance(user: int):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user,)).fetchone()[0]
    conn.close()
    return balance


def create_ticket(user_id):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tickets (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()


def get_tickets(user: int = None):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    if user is not None:
        tickets = cursor.execute("SELECT * FROM tickets WHERE user_id = ?", (user,)).fetchall()
    else:
        tickets = cursor.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    return tickets


def get_ticket(num: int):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()

    user = cursor.execute("SELECT user_id FROM tickets WHERE num = ?", (num,)).fetchone()[0]
    conn.close()
    return user


def get_bets(roll: int):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()

    bets = cursor.execute("SELECT * FROM bets WHERE roll_id = ?", (roll,)).fetchall()
    conn.close()
    return bets


def bet_color(roll: int, user: int, amount: int, color: str):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bets (roll_id, user_id, amount, color) VALUES (?, ?, ?, ?)",
                   (roll, user, amount, color))
    conn.commit()
    conn.close()


def bet_number(roll: int, user: int, amount: int, number: int):
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO bets (roll_id, user_id, amount, num) VALUES (?, ?, ?, ?)", (roll, user, amount, number))
    conn.commit()
    conn.close()


def get_stats():
    conn = sqlite3.connect('economy.db')
    cursor = conn.cursor()
    all_money = sum(i[0] for i in cursor.execute('SELECT balance FROM users').fetchall())
    stats = cursor.execute('SELECT * FROM users ORDER BY balance DESC LIMIT 10').fetchall()
    conn.close()
    return all_money, stats[0], stats[1:]
