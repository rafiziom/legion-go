#!/bin/bash
# Instalator dla mowa_na_tekst.py na Bazzite/Linux (KDE/Atomic)
# Instalacja zależności i instrukcja skrótu klawiszowego ALT+C

set -e

# 1. Instalacja zależności systemowych (rpm-ostree dla Bazzite)
echo "Instalowanie xdotool (wymaga restartu systemu po pierwszej instalacji rpm-ostree!)"
if ! rpm -q xdotool >/dev/null 2>&1; then
    sudo rpm-ostree install --allow-inactive xdotool
else
    echo "xdotool już zainstalowany, pomijam."
fi

echo "Instalowanie bibliotek Pythona (w katalogu użytkownika)"
pip3 install --user sounddevice vosk numpy

# 2. Utworzenie katalogu na model Vosk (jeśli nie istnieje)
mkdir -p ~/.local/share/vosk/

# 3. Pobranie modelu językowego (jeśli nie istnieje)
MODEL_PATH="$HOME/.local/share/vosk/vosk-model-small-pl-0.22"
if [ ! -d "$MODEL_PATH" ]; then
    echo "Pobieranie modelu językowego Vosk (PL small)..."
    wget -O /tmp/vosk-model-small-pl-0.22.zip https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip
    unzip /tmp/vosk-model-small-pl-0.22.zip -d ~/.local/share/vosk/
    rm /tmp/vosk-model-small-pl-0.22.zip
fi

# 4. Tworzenie desktop entry (skrót na pulpit i do menu)
cat > ~/.local/share/applications/mowa_na_tekst.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Mowa na tekst
Exec=python3 /home/bazzite/Dokumenty/mowa_na_tekst.py
Icon=utilities-terminal
Terminal=true
Categories=Utility;
EOF
chmod +x ~/.local/share/applications/mowa_na_tekst.desktop

echo "\nInstalacja zakończona!"
echo "Aby ustawić skrót klawiszowy ALT+C w KDE Plasma (Bazzite):"
echo "1. Otwórz Ustawienia systemowe > Skróty > Niestandardowe skróty."
echo "2. Dodaj nowy skrót > Uruchom polecenie."
echo "3. W polu polecenie wpisz: python3 /home/bazzite/Dokumenty/mowa_na_tekst.py"
echo "4. Ustaw skrót na ALT+C."
echo "5. Zapisz i ciesz się szybkim uruchamianiem!"
