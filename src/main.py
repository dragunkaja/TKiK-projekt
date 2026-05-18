import pprint
from dirsql_parser import parser
from engine import execute_ast


def print_welcome():
    print("=" * 60)
    print(" DirSQL - System Plików jako Baza Danych (Wersja Beta)")
    print("=" * 60)
    print("Dostępne polecenia: SELECT, DELETE, MOVE TO, COPY TO.")
    print("Dodaj prefiks DRYRUN, aby przetestować bez zmian na dysku.")
    print("Wpisz 'exit' lub 'quit' aby wyjść.")
    print("Pamiętaj o średniku (;) na końcu zapytania!\n")


if __name__ == '__main__':
    print_welcome()

    while True:
        try:
            user_input = input("DirSQL > ")

            if user_input.lower().strip() in ['exit', 'quit', 'exit;', 'quit;']:
                print("Zamykanie programu...")
                break

            if not user_input.strip():
                continue

            # Krok 1: Parsowanie (Lexer + Yacc)
            result = parser.parse(user_input)

            # Krok 2: Wykonanie w silniku
            if result:
                execute_ast(result)

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nPrzerwano działanie (Ctrl+C).")
            break
        except Exception as e:
            print(f"[BŁĄD KRYTYCZNY] {e}")