# Silnik zapytań SQL dla systemu plików 'DirSQL' - interpreter

## Autorki:
- Kaja Dragun - kdragun@student.agh.edu.pl
- Julia Dorobis - jdorobis@student.agh.edu.pl

## Założenia programu 

**Cele:** Celem projektu jest stworzenie natywnego silnika zapytań i manipulacji danymi (Query & DML Engine), który mapuje strukturę systemu operacyjnego na model relacyjnej bazy danych.
Program pozwala użytkownikowi nie tylko na zaawansowane przeszukiwanie informacji o plikach, ale również bezpieczną, masową automatyzacje operacji systemowych
(przenoszenie, usuwanie, kopiowanie) przy użyciu standardowej, deklaratywnej składni języka SQL. 
Silnik operuje bezpośrednio na metadanych pobieranych z dysku, traktując katalogi jako tabele, a pliki jako poszczególne rekordy.

**Rodzaj translatora:** Interpreter. Program wykonuje analizę i ewaluację kodu "w locie", w jednym przebiegu, bez generowania skompilowanych plików binarnych czy kodu pośredniego.

**Planowany wynik działania programu:** Interpreter stworzonego podzbioru języka SQL. Program wczytuje zapytanie od użytkownika, buduje jego logiczną strukturę w pamięci, a następnie dynamicznie przegląda system plików (na podstawie ścieżki z klauzuli `FROM`). Wynikiem działania jest wyrzucona na standardowe wyjście (konsolę) sformatowana tabela tekstowa, zawierająca atrybuty plików, które spełniły warunki zdefiniowane w klauzuli `WHERE`.

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

**Planowany język implementacji:** Python z wykorzystaniem biblioteki **PLY (Python Lex-Yacc)**, umożliwiającej implementację analizatora leksykalnego i składniowego w sposób zbliżony do klasycznych narzędzi typu Lex/Yacc.

## Sposób realizacji skanera/parsera:
Wykorzystanie biblioteki **PLY (Python Lex-Yacc)**, która implementuje mechanizmy znane z klasycznych generatorów parserów:

* **Skaner (Analizator leksykalny):** Zaimplementowany przy użyciu modułu `ply.lex`. Odpowiada za podział wejściowego strumienia znaków na tokeny (słowa kluczowe, identyfikatory, operatory, literały). Tokeny są definiowane za pomocą wyrażeń regularnych bezpośrednio w kodzie Pythona.

* **Parser (Analizator składniowy):** Zaimplementowany przy użyciu modułu `ply.yacc` (parser typu LALR). Odpowiada za analizę składniową zapytania na podstawie zdefiniowanej gramatyki oraz budowę struktury reprezentującej zapytanie (np. Abstrakcyjnego Drzewa Składniowego – AST), która jest następnie wykorzystywana do jego wykonania.

## Opis tokenów

Skaner języka używa modułu PLY. Wielkość liter dla słów kluczowych jest ignorowana.

**Tabela tokenów:**

| Kategoria | Nazwa | Wyrażenie Regularne |
| :--- | :--- | :--- |
| **Słowa kluczowe** | `SELECT`, `FROM`, `WHERE`, `AND`, `OR` | `r'(?i)SELECT'` itd. |
| **Operatory** | `OPERATOR` | `r'>=|<=|!=|=|>|<'` |
| **Interpunkcja** | `COMMA`, `SEMICOLON`, `STAR` | `r','`, `r';'`, `r'\*'` |
| **Identyfikatory** | `ID` | `r'[a-zA-Z_][a-zA-Z0-9_]*'` |
| **Dane (Zmienne)** | `STRING` | `r'\"[^\"]*\"'` |
| | `NUMBER` | `r'\d+'` |

**Notacja zastosowanego generatora skanerów (fragment dla PLY):**

```python
t_COMMA = r','
t_SEMICOLON = r';'
t_STAR = r'\*'
t_OPERATOR = r'>=|<=|!=|=|>|<'

def t_SELECT(t):
    r'(?i)SELECT'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t
```

## Gramatyka formatu

### Notacja standardowa (BNF)
Poniżej znajduje się gramatyka języka zapytań DirSQL:

```bnf
<program> ::= <query> ";"
<query> ::= "SELECT" <column_list> "FROM" <string> <where_clause>
<column_list> ::= "*" | <id_list>
<id_list> ::= <id> | <id> "," <id_list>
<where_clause> ::= /* puste */ | "WHERE" <condition_list>
<condition_list> ::= <condition> | <condition> "AND" <condition_list> | <condition> "OR" <condition_list>
<condition> ::= <id> <operator> <value>
<value> ::= <string> | <number>
```
### Notacja generatora parsera (PLY / Yacc)

``` 
program : query SEMICOLON
query : SELECT column_list FROM STRING where_clause
column_list : STAR
            | id_list
id_list : ID
        | ID COMMA id_list
where_clause :
            | WHERE condition
condition : condition AND condition
          | condition OR condition
          | ID OPERATOR value
value : STRING
      | NUMBER
```
