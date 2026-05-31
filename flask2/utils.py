import os
import json


def load_json(folder_name, file_name):
    # Создаём папку, если нет (безопаснее чем os.mkdir)
    os.makedirs(folder_name, exist_ok=True)
    filename = os.path.join(folder_name, file_name)

    # Если файла нет или он пустой/битый, возвращаем пустой dict
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return {}

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️ Файл {filename} повреждён. Начинаем с пустой базы.")
        return {}


def save_json(folder_name, file_name, save_dct):
    os.makedirs(folder_name, exist_ok=True)
    filename = os.path.join(folder_name, file_name)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_dct, f, ensure_ascii=False, indent=4)