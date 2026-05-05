# Silnik zapytań SQL dla systemu plików 'DirSQL'

## Autorki:
- Kaja Dragun - kdragun@student.agh.edu.pl
- Julia Dorobis - jdorobis@student.agh.edu.pl

## Założenia programu 

**Cele:** Celem projektu jest stworzenie natywnego silnika zapytań i manipulacji danymi (Query & DML Engine), który mapuje strukturę systemu operacyjnego na model relacyjnej bazy danych.
Program pozwala użytkownikowi nie tylko na zaawansowane przeszukiwanie informacji o plikach, ale również **bezpieczną (tryb dry-run), masową automatyzacje operacji systemowych**
(przenoszenie, usuwanie, kopiowanie) przy użyciu standardowej, deklaratywnej składni języka SQL. 
Silnik operuje bezpośrednio na metadanych pobieranych z dysku, traktując katalogi jako tabele, a pliki jako poszczególne rekordy.

**Rodzaj translatora:** Interpreter. Program wykonuje analizę i ewaluację kodu "w locie", w jednym przebiegu, bez generowania skompilowanych plików binarnych czy kodu pośredniego.

**Wynik działania programu:** Interpreter stworzonego podzbioru języka SQL obsługujący zapytania typu DQL i DML. Program wczytuje zapytanie od użytkownika, buduje jego logiczną strukturę w pamięci, a następnie przeszukuje system plików na podstawie ścieżki z klauzul `FROM` lub `TO`. 

Dla instrukcji `SELECT` wynikiem działania jest wyrzucona na standardowe wyjście (konsolę) sformatowana tabela tekstowa, zawierająca atrybuty plików, które spełniły warunki zdefiniowane w klauzuli `WHERE`.

Dla instrukcji `DELETE`, `MOVE TO`, `COPY TO` wynikiem jest szczegółowy raport z przebiegu operacji, zawierający liczbę przetworzonych plików, informację o powodzeniu akcji dla poszczególnych rekordów oraz sumaryczne podsumowanie zmian wprowadzonych w systemie plików.


## Przykład użycia programu

**Przykładowe zapytania wejściowe (kod SQL):**

1. Wyszukanie dużych plików archiwalnych, posortowanych malejąco według rozmiaru, z limitem do 5 wyników.

```sql
SELECT nazwa, rozmiar, rozszerzenie FROM "/home/user/pobrane" 
WHERE (rozszerzenie = "zip" OR rozszerzenie = "rar") AND rozmiar > 100 MB 
ORDER BY rozmiar DESC LIMIT 5; 
```

```text
Przeszukiwanie: /home/user/pobrane
--------------------------------------------------
nazwa         | rozmiar | rozszerzenie
--------------------------------------------------
wakacje_2.zip | 1.5 GB  | zip
backup.rar    | 800 MB  | rar
dane_ml.zip   | 250 MB  | zip
--------------------------------------------------
Znaleziono plików: 3 (Limit: 5)
```
2. Symulacja usuwania starych plików (Tryb DRYRUN):
Bezpieczne sprawdzenie, które pliki tymczasowe zostałyby usunięte z systemu, bez faktycznego kasowania danych z dysku. Zastosowano zaawansowane filtrowanie wzorcem (LIKE).

```sql
DRYRUN DELETE FROM "/tmp" WHERE nazwa LIKE "%.tmp" OR rozmiar = 0 B;
```

```text
[TRYB DRYRUN] Akcja: DELETE
Katalog: /tmp
--------------------------------------------------
Pliki przeznaczone do usunięcia:
1. cache_v1.tmp (12 KB)
2. empty_log.txt (0 B)
3. session.tmp (4 KB)
--------------------------------------------------
[SYMULACJA] Zmodyfikowano plików: 3. Zwolnione miejsce: 16 KB.
Żadne pliki nie zostały faktycznie usunięte.
```



**Planowany język implementacji:** Python z wykorzystaniem biblioteki **PLY (Python Lex-Yacc)**.

## Sposób realizacji skanera/parsera:
Wykorzystanie biblioteki **PLY (Python Lex-Yacc)**, która implementuje mechanizmy znane z klasycznych generatorów parserów:

* **Skaner (Analizator leksykalny):** Zaimplementowany przy użyciu modułu `ply.lex`. Odpowiada za podział wejściowego strumienia znaków na tokeny (słowa kluczowe, identyfikatory, operatory, literały). Tokeny są definiowane za pomocą wyrażeń regularnych bezpośrednio w kodzie Pythona.

* **Parser (Analizator składniowy):** Zaimplementowany przy użyciu modułu `ply.yacc` (parser typu LALR). Odpowiada za analizę składniową zapytania na podstawie zdefiniowanej gramatyki oraz budowę struktury reprezentującej zapytanie (np. Abstrakcyjnego Drzewa Składniowego – AST), która jest następnie wykorzystywana do jego wykonania.

## Opis tokenów

Skaner języka używa modułu PLY. Wielkość liter dla słów kluczowych jest ignorowana.

**Tabela tokenów:**

| Kategoria | Nazwa                                                      | Wyrażenie Regularne                                  |
| :--- |:-----------------------------------------------------------|:-----------------------------------------------------|
| **Słowa kluczowe (DQL/DML)** | `SELECT`, `DELETE`, `MOVE`, `COPY`, `TO`, `FROM`, `DRYRUN` | `r'(?i)SELECT'`, `r'(?i)DELETE'` itd.                |
| **Słowa kluczowe (Klauzule)** | `WHERE`, `ORDER`, `BY`, `LIMIT`, `ASC`, `DESC`             | `r'(?i)WHERE'`, `r'(?i)ORDER'` itd.                  |
| **Słowa kluczowe (Logika)**| `AND`, `OR`, `NOT`, `LIKE`                                 | `r'(?i)AND'`, `r'(?i)LIKE'` itd.                     |
| **Operatory relacyjne** | `OPERATOR`                                                 | `r'>=\|<=\|!=\|=\|>\|<'`                             |
| **Interpunkcja** | `COMMA`, `SEMICOLON`, `STAR`                               | `r','`, `r';'`, `r'\*'`                              |
| **Nawiasy (Priorytetyzacja)**| `LPAREN`, `RPAREN`                                         | `r'\('`, `r'\)'`                                     |
| **Jednostki wielkości** | `SIZE_UNIT`                                                | `r'(?i)(GB\|MB\|KB\|B)'`                             |
| **Identyfikatory** | `ID`                                                       | `r'[a-zA-Z_][a-zA-Z0-9_]*'`                          |
| **Dane (Zmienne)** | `STRING`                                                   | `r'\"[^\"]*\"'` lub `r'\'[^\']*\''`                  |
| | `NUMBER`                                                   | `r'\d+'`                                             |


## Gramatyka formatu

### Notacja generatora parsera (PLY / Yacc)

```yacc

program : statement SEMICOLON
        | program statement SEMICOLON

statement : dryrun_opt query

dryrun_opt : 
           | DRYRUN

query : select_query
      | delete_query
      | move_query
      | copy_query

select_query : SELECT column_list FROM STRING where_clause order_clause limit_clause

delete_query : DELETE FROM STRING where_clause limit_clause

move_query : MOVE FROM STRING TO STRING where_clause limit_clause

copy_query : COPY FROM STRING TO STRING where_clause limit_clause

column_list : STAR
            | id_list

id_list : ID
        | ID COMMA id_list

where_clause :
             | WHERE condition

condition : condition AND condition
          | condition OR condition
          | NOT condition
          | LPAREN condition RPAREN
          | ID OPERATOR value
          | ID LIKE STRING

value : STRING
      | NUMBER
      | NUMBER SIZE_UNIT

order_clause :
             | ORDER BY ID
             | ORDER BY ID ASC
             | ORDER BY ID DESC

limit_clause :
             | LIMIT NUMBER
```
