# Silnik zapytań SQL dla systemu plików - interpreter

Projekt zaliczeniowy z przedmiotu Teoria Kompilacji i Kompilatory.

## Autorki:
- Kaja Dragun - kdragun@student.agh.edu.pl
- Julia Dorobis - jdorobis@student.agh.edu.pl

## Założenia programu DirSQL- krótki opis


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


## Opis tokenów

Skaner został zaimplementowany przy użyciu generatora **Flex**. Rozpoznaje on poniższe tokeny, przy czym wielkość liter dla słów kluczowych jest ignorowana (case-insensitive).

| Kategoria | Token (Bison) | Wyrażenie Regularne (Flex) | Przykład |
| :--- | :--- | :--- | :--- |
| **Słowa kluczowe** | `TOKEN_SELECT` | `(?i:SELECT)` | `SELECT` |
| | `TOKEN_FROM` | `(?i:FROM)` | `FROM` |
| | `TOKEN_WHERE` | `(?i:WHERE)` | `WHERE` |
| | `TOKEN_AND` | `(?i:AND)` | `AND` |
| | `TOKEN_OR` | `(?i:OR)` | `OR` |
| **Operatory** | `TOKEN_OPERATOR` | `">="|"<="|"="|"!="|">"|"<"` | `>=`, `!=` |
| **Interpunkcja** | `TOKEN_COMMA` | `,` | `,` |
| | `TOKEN_SEMICOLON` | `;` | `;` |
| | `TOKEN_STAR` | `\*` | `*` |
| **Identyfikatory** | `TOKEN_ID` | `[a-zA-Z_][a-zA-Z0-9_]*` | `nazwa`, `rozmiar_b` |
| **Stałe** | `TOKEN_STRING` | `\"[^\"]*\"` | `"/home/user"`, `".pdf"` |
| | `TOKEN_NUMBER` | `[0-9]+` | `1024` |
| **Ignorowane** | *(Brak)* | `[ \t\n\r]+` | *(Spacje, entery)* |

---

## Gramatyka formatu

### Notacja standardowa (BNF)
Poniżej znajduje się gramatyka języka zapytań DirSQL:

```bnf
<program> ::= <query> ";"

<query> ::= "SELECT" <column_list> "FROM" <string_literal> <where_clause>

<column_list> ::= "*" 
                | <identifier_list>

<identifier_list> ::= <identifier> 
                    | <identifier> "," <identifier_list>

<where_clause> ::= /* puste */
                 | "WHERE" <condition_list>

<condition_list> ::= <condition>
                   | <condition> "AND" <condition_list>
                   | <condition> "OR" <condition_list>

<condition> ::= <identifier> <operator> <value>

<operator> ::= "=" | "!=" | ">" | "<" | ">=" | "<="

<value> ::= <string_literal> | <number_literal>