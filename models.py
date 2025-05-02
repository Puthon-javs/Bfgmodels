import random
from datetime import datetime

class BotModule:
    def __init__(self):
        self.notes = {}  # {user_id: [note1, note2]}
        self.duels = {}  # {chat_id: {"players": [user1, user2], "scores": {user1: 0, user2: 0}}}
        self.bot_info = {
            "language": "Python",
            "creator": "Ваше имя",
            "version": "1.0",
            "creation_date": "2023-11-15",
            "features": ["Заметки", "Дуэли", "Информация о боте"]
        }
    
    # ===== Система заметок =====
    def add_note(self, user_id, note_text):
        if user_id not in self.notes:
            self.notes[user_id] = []
        self.notes[user_id].append({
            "text": note_text,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return "Заметка успешно добавлена!"
    
    def get_notes(self, user_id):
        if user_id not in self.notes or not self.notes[user_id]:
            return "У вас нет заметок."
        
        notes_list = ["Ваши заметки:"]
        for i, note in enumerate(self.notes[user_id], 1):
            notes_list.append(f"{i}. {note['text']} (создано: {note['date']})")
        
        return "\n".join(notes_list)
    
    def delete_note(self, user_id, note_index):
        if user_id not in self.notes:
            return "У вас нет заметок для удаления."
        
        try:
            note_index = int(note_index) - 1
            if 0 <= note_index < len(self.notes[user_id]):
                deleted_note = self.notes[user_id].pop(note_index)
                return f"Заметка удалена: {deleted_note['text']}"
            else:
                return "Неверный номер заметки."
        except ValueError:
            return "Пожалуйста, укажите номер заметки цифрой."
    
    # ===== Система дуэлей =====
    def start_duel(self, chat_id, player1_id, player2_id):
        if chat_id in self.duels:
            return "В этом чате уже идет дуэль!"
        
        self.duels[chat_id] = {
            "players": [player1_id, player2_id],
            "scores": {player1_id: 0, player2_id: 0},
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return f"Дуэль началась! Игрок 1 vs Игрок 2. Используйте команду /duel_attack для атаки!"
    
    def duel_attack(self, chat_id, attacker_id):
        if chat_id not in self.duels:
            return "В этом чате нет активной дуэли."
        
        duel = self.duels[chat_id]
        if attacker_id not in duel["players"]:
            return "Вы не участник этой дуэли!"
        
        # Определяем кто атакует, а кто защищается
        players = duel["players"]
        defender_id = players[1] if attacker_id == players[0] else players[0]
        
        # Симуляция атаки (рандомный урон 1-10)
        damage = random.randint(1, 10)
        duel["scores"][attacker_id] += damage
        
        # Проверка на победу (первый набравший 30 очков побеждает)
        if duel["scores"][attacker_id] >= 30:
            winner = attacker_id
            loser = defender_id
            del self.duels[chat_id]
            return (f"Игрок {winner} нанес решающий удар ({damage} урона) и побеждает в дуэли!\n"
                    f"Финальный счет: {winner}: 30 vs {loser}: {duel['scores'][loser]}")
        
        return (f"Игрок {attacker_id} наносит удар ({damage} урона)!\n"
                f"Текущий счет: {attacker_id}: {duel['scores'][attacker_id]} vs "
                f"{defender_id}: {duel['scores'][defender_id]}")
    
    def duel_status(self, chat_id):
        if chat_id not in self.duels:
            return "В этом чате нет активной дуэли."
        
        duel = self.duels[chat_id]
        players = duel["players"]
        return (f"Текущий статус дуэли (начата в {duel['start_time']}):\n"
                f"{players[0]}: {duel['scores'][players[0]]} очков\n"
                f"{players[1]}: {duel['scores'][players[1]]} очков\n"
                f"До победы нужно {30 - max(duel['scores'].values())} очков.")
    
    # ===== Информация о боте =====
    def get_bot_info(self):
        info_lines = [f"🤖 Информация о боте:"]
        for key, value in self.bot_info.items():
            if isinstance(value, list):
                info_lines.append(f"{key.capitalize()}: {', '.join(value)}")
            else:
                info_lines.append(f"{key.capitalize()}: {value}")
        return "\n".join(info_lines)