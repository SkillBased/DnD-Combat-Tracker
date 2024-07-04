from os import path, makedirs
if not path.exists("./tmp/logs"):
    makedirs("./tmp/logs")
with open("./tmp/logs/logfile.txt", "a+") as file:
    file.write("lol")