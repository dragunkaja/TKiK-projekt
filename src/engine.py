import os
import shutil

class DirSQLEngine:
    def __init__(self):
        pass

    def execute_query(self, ast):
        # Sprawdzamy opcję bezpieczeństwa
        is_dryrun = ast.get('dryrun', False)
        query = ast.get('query', {})
        action = query.get('action')

        if action == 'SELECT':
            self._do_select(query)
        elif action == 'DELETE':
            self._do_delete(query, is_dryrun)
        elif action == 'MOVE':
            self._do_move(query, is_dryrun)

    def _do_select(self, query):
        sciezka = query['path']
        print(f"Otwieram katalog: {sciezka}...")
        # Tutaj w przyszłości będzie logika os.listdir() i rysowanie tabeli

    def _do_delete(self, query, is_dryrun):
        sciezka = query['path']
        # Logika szukania plików...
        if is_dryrun:
            print("[DRYRUN] Symulacja usuwania w katalogu", sciezka)
        else:
            print("[UWAGA] Faktyczne usuwanie w katalogu", sciezka)
            # os.remove(...)