import re

with open("text.txt", "r", encoding="utf-8") as file:  # заменить file_name на имя файла

    txt = file.read()

    txt = re.sub(r"\s", "", txt)

    out_txt = re.split(r"[()]", txt)

    print(out_txt)