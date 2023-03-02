import re

string = "ConfigAdmins:config_admins_list"
pattern = r"ConfigAdmins:config_admins_"
result = re.search(pattern, string)

if re.search(r"ConfigAdmins:config_admins_", current_state):
    print("Строка содержит подстроку.")
else:
    print("Строка не содержит подстроку.")
