import pprint  # Biblioteka do ładnego wyświetlania słowników
from dirsql_parser import parser  # Importujemy gotowy parser z Twojego pliku


def test_query(query_string):
    """Funkcja pomocnicza do ładnego wypisywania testów."""
    print("-" * 60)
    print(f"Wejście SQL : {query_string}")

    try:
        # Tu dzieje się magia – parser przetwarza tekst na AST
        result = parser.parse(query_string)

        print("Wynik (AST):")
        # pprint ładnie sformatuje słownik, żeby nie był w jednej długiej linii
        pprint.pprint(result, sort_dicts=False, indent=2)
    except Exception as e:
        print(f"Błąd podczas parsowania: {e}")
    print("-" * 60)


if __name__ == '__main__':
    print("=== START TESTÓW AUTOMATYCZNYCH ===")

    # Test 1: Klasyczny SELECT z zaawansowanym WHERE
    test1 = 'SELECT nazwa, rozmiar FROM "/home/user" WHERE rozmiar > 100 MB ORDER BY rozmiar DESC LIMIT 10;'
    test_query(test1)

    # Test 2: Tryb DRYRUN i polecenie MOVE
    test2 = 'DRYRUN MOVE FROM "/pobrane" TO "/archiwum" WHERE ext = "pdf";'
    test_query(test2)

    # Test 3: DELETE z logiką AND
    test3 = 'DELETE FROM "/tmp" WHERE name LIKE "%.tmp" AND size < 1 KB;'
    test_query(test3)

    print("\n=== TRYB INTERAKTYWNY ===")
    print("Wpisz swoje zapytanie SQL (pamiętaj o średniku na końcu!).")
    print("Wpisz 'exit', aby zakończyć.\n")

    while True:
        try:
            # Pobieramy tekst od użytkownika
            user_input = input("DirSQL > ")

            if user_input.lower() in ['exit', 'quit']:
                print("Zamykanie programu...")
                break

            if not user_input.strip():
                continue

            # Parsujemy i wyświetlamy wynik
            result = parser.parse(user_input)
            if result:
                pprint.pprint(result, sort_dicts=False, indent=2)

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nPrzerwano działanie (Ctrl+C).")
            break