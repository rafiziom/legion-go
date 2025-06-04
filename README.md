# Mowa na tekst – Rozpoznawanie mowy dla Linux (Bazzite/KDE)

Aplikacja umożliwia rozpoznawanie mowy w języku polskim i automatyczne wpisywanie tekstu do aktywnego okna systemu Linux. Obsługuje interpunkcję głosową (np. „kropka”, „przecinek”, „enter”) oraz szybkie uruchamianie przez skrót klawiszowy ALT+C.

## Funkcje

- Rozpoznawanie mowy w języku polskim (Vosk)
- Automatyczne wpisywanie rozpoznanego tekstu do aktywnego okna (xdotool)
- Obsługa polskich znaków i interpunkcji głosowej
- Obsługa komendy „enter” (nowa linia)
- Szybkie uruchamianie przez skrót klawiszowy ALT+C (KDE/Bazzite)
- Prosta instalacja i konfiguracja

## Wymagania

- System Linux (Bazzite, Fedora Atomic, KDE Plasma)
- Python 3
- Dostęp do mikrofonu

## Instalacja

1. **Pobierz repozytorium:**
   ```sh
   git clone https://github.com/rafiziom/legion-go.git
   cd legion-go
   ```

2. **Uruchom skrypt instalacyjny:**
   ```sh
   bash install_mowa_na_tekst.sh
   ```
   Skrypt:
   - Zainstaluje wymagane pakiety (`xdotool`, biblioteki Python)
   - Pobierze model językowy Vosk (PL small)
   - Utworzy skrót aplikacji w menu systemowym

3. **Ustaw skrót klawiszowy ALT+C (KDE):**
   - Otwórz: Ustawienia systemowe > Skróty > Niestandardowe skróty
   - Dodaj nowy skrót > Uruchom polecenie
   - W polu polecenie wpisz:
     ```
     python3 /home/bazzite/Dokumenty/mowa_na_tekst.py
     ```
   - Ustaw skrót na ALT+C i zapisz

## Uruchamianie

- Uruchom aplikację z menu systemowego lub użyj skrótu ALT+C.
- Mów do mikrofonu – rozpoznany tekst pojawi się w aktywnym oknie.
- Wypowiadaj komendy interpunkcyjne („kropka”, „przecinek”, „enter” itd.), aby wstawić odpowiednie znaki.

## Aktualizacja

Aby zaktualizować aplikację do najnowszej wersji:
```sh
cd legion-go
git pull
```

## Autor

- [rafiziom](https://github.com/rafiziom)
