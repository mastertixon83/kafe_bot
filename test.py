import json
import os

ass = {"sdasdasd":"asdasdasdasd"}

with open("temp/temp1.json", "w") as file:
    json.dump(ass, file, indent=4, ensure_ascii=False)
folders = ["temp", "media/mailings"]
for folder_name in folders:
    try:
        for filename in os.listdir(folder_name):
            file_path = os.path.join(folder_name, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            print(file_path)
    except Exception as _ex:
        print(_ex)
