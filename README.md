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

**Planowany wynik działania programu:** Interpreter stworzonego podzbioru języka SQL obsługujący zapytania typu DQL i DML. Program wczytuje zapytanie od użytkownika, buduje jego logiczną strukturę w pamięci, a następnie przeszukuje system plików na podstawie ścieżki z klauzul `FROM` lub `TO`. 

Dla instrukcji `SELECT` wynikiem działania jest wyrzucona na standardowe wyjście (konsolę) sformatowana tabela tekstowa, zawierająca atrybuty plików, które spełniły warunki zdefiniowane w klauzuli `WHERE`.

Dla instrukcji `DELETE`, `MOVE FROM ... TO ...`, `COPY FROM ... TO ...` wynikiem jest szczegółowy raport z przebiegu operacji, zawierający liczbę przetworzonych plików, informację o powodzeniu akcji dla poszczególnych rekordów oraz sumaryczne podsumowanie zmian wprowadzonych w systemie plików.


## Przykład użycia programu

Poniżej znajduje się przykładowe, jednolinijkowe zapytanie weryfikujące działanie interpretera oraz jego spodziewany wynik wyrzucony na standardowe wyjście.

**Przykładowe zapytanie wejściowe (kod SQL):**
```sql
SELECT nazwa, rozmiar_b FROM "/home/user/dokumenty" WHERE rozmiar_b > 1024;
```
```text
Przeszukiwanie: /home/user/dokumenty
--------------------------------------------------
nazwa | rozmiar_b
--------------------------------------------------
raport.pdf | 2048
notatki.txt | 1536
prezentacja.pptx | 5120
--------------------------------------------------
Znaleziono plików: 3
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
| **Operatory relacyjne** | `OPERATOR`                                                 | ``r'>=|<=|!=|=|>|<'``                             |
| **Interpunkcja** | `COMMA`, `SEMICOLON`, `STAR`                               | `r','`, `r';'`, `r'\*'`                              |
| **Nawiasy (Priorytetyzacja)**| `LPAREN`, `RPAREN`                                         | `r'\('`, `r'\)'`                                     |
| **Jednostki wielkości** | `SIZE_UNIT`                                                | ``r'(?i)(GB|MB|KB|B)'``                             |
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
