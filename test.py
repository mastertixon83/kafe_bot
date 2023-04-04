import os
from utils.db_api.db_commands import DBCommands
db = DBCommands()

folders = ["temp", "media/mailings"]

for folder_name in folders:
    try:
        if folder_name == "media/mailings":
            acive_tasks = db.get_all_active_tasks()
            file_list = []
            for task in acive_tasks:
                file_list.append(f"{task['picture']}.jpg")
            print(file_list)
        else:
            for filename in os.listdir(folder_name):
                file_path = os.path.join(folder_name, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as _ex:
        pass