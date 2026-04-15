# Silnik zapytań SQL dla systemu plików - DirSQL

Projekt zaliczeniowy z przedmiotu Teoria Kompilacji i Kompilatory.

## Autorki:
- Kaja Dragun - kdragun@student.agh.edu.pl
- Julia Dorobis - jdorobis@student.agh.edu.pl

## Założenia programu 

**Cele:** Celem projektu jest stworzenie natywnego silnika zapytań (Query Engine), który mapuje strukturę systemu operacyjnego na model relacyjnej bazy danych. Program pozwala użytkownikowi na zaawansowane przeszukiwanie i filtrowanie informacji o plikach (np. nazwa, rozmiar, rozszerzenie) przy użyciu standardowej, deklaratywnej składni języka SQL. Silnik operuje bezpośrednio na metadanych pobieranych z dysku, traktując katalogi jako tabele, a pliki jako poszczególne rekordy.

**Rodzaj translatora:** Interpreter. Program wykonuje analizę i ewaluację kodu "w locie", w jednym przebiegu, bez generowania skompilowanych plików binarnych czy kodu pośredniego.

**Planowany wynik działania programu:** Interpreter stworzonego podzbioru języka SQL. Program wczytuje zapytanie od użytkownika, buduje jego logiczną strukturę w pamięci, a następnie dynamicznie przegląda system plików (na podstawie ścieżki z klauzuli `FROM`). Wynikiem działania jest wyrzucona na standardowe wyjście (konsolę) sformatowana tabela tekstowa, zawierająca atrybuty plików, które spełniły warunki zdefiniowane w klauzuli `WHERE`.

**Planowany język implementacji:** C++ (
wymagany standard **C++17** lub nowszy ze względu
na wbudowaną bibliotekę `<filesystem>` 
służącą do nawigacji po dysku).

**Sposób realizacji skanera/parsera:** Wykorzystanie klasycznych generatorów z rodziny GNU dla języka C/C++:
* **Skaner (Analizator leksykalny):** Wygenerowany za pomocą narzędzia **Flex**. Odpowiada za podział strumienia znaków wejściowych na predefiniowane tokeny (słowa kluczowe, ciągi znaków, operatory).
* **Parser (Analizator składniowy):** Wygenerowany za pomocą narzędzia **Bison** (parser LALR). Odpowiada za walidację poprawności gramatycznej zapytania oraz zbudowanie Abstrakcyjnego Drzewa Składniowego (AST) opartego na obiektach języka C++.


## 2. Opis tokenów

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
