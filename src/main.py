from parser import parser

while True:
    try:
        data = input("DirSQL> ")
        if not data:
            continue

        result = parser.parse(data)
        print(result)

    except EOFError:
        break