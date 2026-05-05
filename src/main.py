from dirsql_parser import parser
from rich.tree import Tree
from rich import print as rprint


def build_rich_tree(node, tree=None, root_name="Zapytanie SQL"):
    """
    Rekurencyjna funkcja, która zamienia nasz słownik AST na graficzne drzewo z biblioteki rich.
    """
    if tree is None:
        tree = Tree(f"[bold yellow] {root_name}[/bold yellow]")

    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                # Tworzymy nową gałąź dla zagnieżdżonych słowników/list
                branch = tree.add(f"[bold cyan]{key}[/bold cyan]")
                build_rich_tree(value, branch)
            else:
                # Wypisujemy ostateczną wartość (liść)
                tree.add(f"[bold cyan]{key}[/bold cyan]: [bold green]{value}[/bold green]")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            if isinstance(item, (dict, list)):
                branch = tree.add(f"[magenta]Element {i + 1}[/magenta]")
                build_rich_tree(item, branch)
            else:
                tree.add(f"[bold green]{item}[/bold green]")
    else:
        tree.add(f"[bold green]{node}[/bold green]")

    return tree


def test_query(query_string):
    print("-" * 60)
    print(f"Wejście SQL : {query_string}")
    try:
        result = parser.parse(query_string)
        if result:
            # Tworzymy i wypisujemy graficzne drzewo
            ast_tree = build_rich_tree(result)
            rprint(ast_tree)
    except Exception as e:
        print(f"Błąd podczas parsowania: {e}")
    print("-" * 60)


if __name__ == '__main__':
    print("=== START TESTÓW AUTOMATYCZNYCH ===")

    test1 = 'SELECT nazwa, rozmiar FROM "/home/user" WHERE rozmiar > 100 MB ORDER BY rozmiar DESC LIMIT 10;'
    test_query(test1)

    print("\n=== TRYB INTERAKTYWNY ===")
    print("Wpisz swoje zapytanie SQL (pamiętaj o średniku na końcu!). Wpisz 'exit', aby zakończyć.\n")

    while True:
        try:
            user_input = input("DirSQL > ")
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue

            result = parser.parse(user_input)
            if result:
                ast_tree = build_rich_tree(result)
                rprint(ast_tree)

        except EOFError:
            break
        except KeyboardInterrupt:
            break