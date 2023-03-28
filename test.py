import json

from data import config

with open("temp.json", "r") as file:
    msg_id_list = json.load(file)

msg_id_dict = {}
for item in msg_id_list:
    msg_id_dict.update(item)


print(config.admins[0])
print(msg_id_dict['553603641'])