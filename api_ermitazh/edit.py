import re

with open("text.txt", "r", encoding="utf-8") as file: 

    txt = file.read()

    txt = re.sub(r"\s", "", txt)

    out_txt = re.split(r"[()]", txt)

    
