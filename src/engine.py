import os
import shutil
import fnmatch


def parse_size(val):
    """Zamienia krotki np. (100, 'MB') na bajty, obsługuje też zwykłe liczby."""
    if isinstance(val, tuple):
        number, unit = val
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3}
        return number * multipliers.get(str(unit).upper(), 1)
    return val


def evaluate_condition(cond_ast, file_data):
    """Rekurencyjnie sprawdza, czy dany plik spełnia warunki z WHERE."""
    if not cond_ast:
        return True

    if 'logic_op' in cond_ast:
        op = cond_ast['logic_op']
        if op == 'AND':
            return evaluate_condition(cond_ast['left'], file_data) and evaluate_condition(cond_ast['right'], file_data)
        elif op == 'OR':
            return evaluate_condition(cond_ast['left'], file_data) or evaluate_condition(cond_ast['right'], file_data)
        elif op == 'NOT':
            return not evaluate_condition(cond_ast['val'], file_data)

    if 'rel_op' in cond_ast:
        col = cond_ast['column']
        op = cond_ast['rel_op']
        val = parse_size(cond_ast['value'])

        actual_val = file_data.get(col)
        if actual_val is None:
            return False

        if op == 'LIKE':
            # Rzutujemy na str, aby program nie crashował jeśli actual_val to liczba
            pattern = str(val).replace('%', '*')
            return fnmatch.fnmatch(str(actual_val), pattern)

        elif op == '=':
            return actual_val == val
        elif op == '!=':
            return actual_val != val
        elif op == '>':
            return actual_val > val
        elif op == '<':
            return actual_val < val
        elif op == '>=':
            return actual_val >= val
        elif op == '<=':
            return actual_val <= val

    return True


def get_files_data(path, where_ast):
    """Przeszukuje katalog i zwraca listę metadanych plików."""
    results = []
    if not os.path.exists(path):
        print(f"[BŁĄD] Ścieżka {path} nie istnieje!")
        return results

    try:
        for root, dirs, files in os.walk(path):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                stats = os.stat(full_path)
                file_ext = os.path.splitext(file_name)[1]

                file_data = {
                    'nazwa': file_name,
                    'rozszerzenie': file_ext,
                    'rozmiar_b': stats.st_size,
                    'sciezka': full_path
                }

                if evaluate_condition(where_ast, file_data):
                    results.append(file_data)
    except Exception as e:
        print(f"[BŁĄD] Odmowa dostępu lub błąd I/O: {e}")

    return results


def process_select(query):
    """Pomocnicza funkcja rekurencyjna dla zapytań SELECT (zwraca dane, nie wypisuje ich od razu)."""
    source = query.get('source')

    # KROK 1: SKĄD MAMY DANE?
    if isinstance(source, dict):
        # Źródłem jest podzapytanie! Wywołujemy się rekurencyjnie.
        files = process_select(source)
    else:
        # Źródłem jest ścieżka tekstowa na dysku.
        path = source.strip('"\'')
        # Ściągamy wszystkie pliki (wewnętrzne WHERE z pliku traktujemy też tu)
        files = get_files_data(path, None)

        # KROK 2: FILTROWANIE (WHERE)
    where_ast = query.get('where')
    if where_ast:
        files = [f for f in files if evaluate_condition(where_ast, f)]

    # KROK 3: SORTOWANIE (ORDER BY)
    order_clause = query.get('order')
    if order_clause:
        col = order_clause['column']
        is_reverse = (order_clause['dir'] == 'DESC')
        files.sort(key=lambda x: x.get(col, 0), reverse=is_reverse)

    # KROK 4: LIMIT
    limit_clause = query.get('limit')
    if limit_clause is not None:
        files = files[:limit_clause]

    return files


def execute_ast(ast):
    """Główna funkcja wykonująca zapytanie i wyświetlająca wynik."""
    is_dryrun = ast.get('dryrun', False)
    query = ast['query']
    action = query['action']

    print(f"\n[{'DRY-RUN' if is_dryrun else 'WYKONANIE'}] Akcja: {action}")
    print("-" * 60)

    # Jeśli to SELECT, używamy nowej,rekurencyjnej funkcji
    if action == 'SELECT':
        files = process_select(query)

        if not files:
            print("Brak plików spełniających kryteria.")
            return

        selected_cols = query['columns']
        if selected_cols == '*':
            selected_cols = ['nazwa', 'rozszerzenie', 'rozmiar_b', 'sciezka']

        header = " | ".join(selected_cols)
        print(header)
        print("-" * len(header))
        for f in files:
            row = [str(f.get(c, "N/A")) for c in selected_cols]
            print(" | ".join(row))

        print("-" * 60)
        print(f"Zwrócono rekordów: {len(files)}")

    # DML (DELETE, MOVE, COPY)
    elif action in ['DELETE', 'MOVE', 'COPY']:
        source_path = query.get('source').strip('"\'')
        files = get_files_data(source_path, query.get('where'))

        limit_clause = query.get('limit')
        if limit_clause is not None:
            files = files[:limit_clause]

        if not files:
            print("Brak plików spełniających kryteria.")
            return

        dest_path = query.get('destination', '').strip('"\'')
        if action in ['MOVE', 'COPY'] and not os.path.exists(dest_path) and not is_dryrun:
            os.makedirs(dest_path, exist_ok=True)

        for f in files:
            src = f['sciezka']
            if action == 'DELETE':
                print(f"Usuwanie: {src}")
                if not is_dryrun: os.remove(src)
            elif action == 'MOVE':
                dst = os.path.join(dest_path, f['nazwa'])
                print(f"Przenoszenie: {src} -> {dst}")
                if not is_dryrun: shutil.move(src, dst)
            elif action == 'COPY':
                dst = os.path.join(dest_path, f['nazwa'])
                print(f"Kopiowanie: {src} -> {dst}")
                if not is_dryrun: shutil.copy2(src, dst)

        print("-" * 60)
        print(f"Przetworzono rekordów: {len(files)}")