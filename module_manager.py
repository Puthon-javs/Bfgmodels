import os
import re

MODULES_PATH = "/usr/home/Mara/kakabfg/modules/"

def extract_commands_from_file(filepath):
    commands = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            handlers = re.findall(r'@(?:dp|router)\.message_handler(.*?)', content, re.DOTALL)

            for handler in handlers:
                cmd_matches = re.findall(r'commands\s*=\s*([^]+)', handler)
                for match in cmd_matches:
                    cmds = [cmd.strip().strip("'\"") for cmd in match.split(",")]
                    commands.extend(cmds)

                text_matches = re.findall(r'text\s*=\s*([^]+)', handler)
                for match in text_matches:
                    texts = [txt.strip().strip("'\"") for txt in match.split(",")]
                    commands.extend(texts)
    except Exception as e:
        commands.append(f"[Ошибка: {e}]")
    return commands

def show_all_modules():
    if not os.path.exists(MODULES_PATH):
        print("❌ Папка модулей не найдена.")
        return

    print("📦 Найденные модули и их команды:\n")
    found = False

    for file in os.listdir(MODULES_PATH):
        if file.endswith(".py"):
            full_path = os.path.join(MODULES_PATH, file)
            commands = extract_commands_from_file(full_path)
            found = True
            print(f"🔹 {file}")
            if commands:
                for cmd in commands:
                    print(f"   └ 🟢 {cmd}")
            else:
                print("   └ ⚠ Команды не найдены.")
            print()

    if not found:
        print("❌ В папке нет модулей.")

if __name__ == "__main__":
    show_all_modules()