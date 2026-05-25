# Automatyzacja kampanii reklamowych (Ads) na Facebooku

## Opis
Aplikacja desktopowa służąca do aktualizacji kampanii reklamowych (ads) na Facebooku za pomocą szablonu Excel.

## Gotowa aplikacja w katalogu "output"

W katalogu `output` znajdziesz gotową aplikację do uruchomienia. Wystarczy skonfigurować plik `config.json`, umieścić go w tym samym katalogu, a następnie uruchomić plik `Auto FB Boost v3.0.exe`.

## Wymagania
- Python 3.12 lub nowszy
- Biblioteki:
  - facebook_business==25.0.1
  - pandas==2.2.2
  - PyQt6==6.7.0
  - PyQt6-sip==13.6.0
  - python-dateutil==2.9.0.post0
  - requests==2.31.0 
  - certifi~=2024.2.2

## Konfiguracja
Skonfiguruj plik config.json . W katalogu projektu znajduje się szablon `.config.json`, który należy uzupełnić.
    
Przykładowy `config.json`:

    {
      "app-id": "APP ID",
      "app-secret": "APP SECRET",
      "access-token": "ACCESS TOKEN",
      "version": "v25.0"
    }

## Instalacja
Aby zainstalować aplikację, wykonaj następujące kroki:

1. Sklonuj repozytorium:
    ```sh
    git clone https://github.com/fmatusiak/fb-ads-campaign-updater.git
    ```
2. Przejdź do katalogu projektu:
    ```sh
    cd katalog-projektu
    ```
3. Zainstaluj wymagane biblioteki:
    ```sh
    pip install -r requirements.txt
    ```

## Użycie
Aby uruchomić aplikację, wykonaj:
```sh
python main.py
```

## Szablon Excel
W katalogu `template` znajduje się przykładowy plik Excel `ads template.xlsx` do aktualizacji kampanii.

### Kolumny do podmiany właściwości kampanii:
- `campaign_name`: Nazwa kampanii
- `daily_budget`: Budżet dzienny
- `latitude`: Szerokość geograficzna dla lokalizacji
- `longitude`: Długość geograficzna dla lokalizacji
- `radius`: Promień lokalizacji w kilometrach
- `end_time`: Data zakończenia kampanii

### Kolumny z klamrami `{$}` do podmiany tekstu dla danej kampanii:
Np. `{$pozdrowienia}`, `{$header_1}`, `{$header_description_1}`. `{$description}`
   
   

