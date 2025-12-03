# CONFIDEAINEW

## Metodologia integracji AI wspierającej szyfrowanie
Poniższa propozycja opisuje, jak krok po kroku dołączyć komponenty AI, które pomagają zdecydować o poziomie ochrony plików i wzmocnić proces szyfrowania.

### 1. Przygotowanie danych wejściowych
- **OCR i NER**: użyj istniejących funkcji `load_image` i `anonymize_image` do pozyskania tekstu oraz do wykrycia i zamazania wrażliwych fragmentów. W razie potrzeby podmień model spaCy w `anonymize_image` na dokładniejszy wariant (np. transformer) trenowany do detekcji danych osobowych.
- **Tekst z dokumentów**: dla PDF-ów wykorzystaj `pdfplumber`, a dla obrazów `pytesseract`, aby mieć spójny tekst wejściowy do dalszych decyzji.

### 2. Klasyfikacja wrażliwości (model NLP/LLM)
- Zbuduj lekki klasyfikator (spaCy TextCategorizer lub lokalny LLM) oceniający, czy dokument zawiera dane wrażliwe.
- Wynik klasyfikacji przechowuj jako flagę przekazywaną do `encrypt_file`, aby wymusić szyfrowanie lub wybrać silniejszy tryb.

### 3. Detekcja typu dokumentu (wizja komputerowa)
- Dodaj prosty model obrazu/układu dokumentu (np. ONNX z MobileNet/ViT) pracujący na miniaturze pliku.
- Dla wykrytych typów wysokiego ryzyka (dowód, umowa, dokument medyczny) ustaw politykę: obowiązkowe szyfrowanie, dłuższe klucze, ewentualnie dwuskładnikowa akceptacja użytkownika.

### 4. Asystent haseł i walidacja
- Rozszerz `validate_password_strength` o heurystyki (np. zxcvbn) lub model oceniający ryzyko odgadnięcia hasła.
- Generuj sugestie silnych haseł i wymuszaj minimalne progi złożoności przy rejestracji/logowaniu.

### 5. Decyzje o trybie szyfrowania
- Przed utworzeniem obiektu `Cipher` w `encrypt_file` zaimplementuj reguły lub model decyzyjny: wybór AES-CFB vs AES-GCM, długość klucza (np. zawsze 256 bitów), wymaganie HMAC lub tagu AEAD.
- Dodaj telemetrię: loguj, który wariant został wybrany i dlaczego (wynik klasyfikacji, typ dokumentu, poziom hasła).

### 6. Ścieżka audytu i usuwania
- Uzupełnij logi (`operations.log`) o informacje o decyzjach AI (klasyfikacja, rekomendacje haseł, wybór trybu szyfrowania).
- Po zakończeniu pracy oferuj automatyczne bezpieczne usunięcie plików tymczasowych i oryginałów przy włączonej opcji `delete_original`.

### 7. Walidacja i testy
- Przygotuj testy jednostkowe sprawdzające: poprawność klasyfikacji (na zbiorze etykietowanych dokumentów), jakość anonimizacji (brak wycieków PII), integralność szyfrowania/odszyfrowania i spójność logów.
- Zadbaj o scenariusze negatywne: brak modelu, błędy OCR, dokumenty nietekstowe, zbyt słabe hasła.

### 8. Operacjonalizacja
- Modele trzymaj w lokalnych zasobach lub w trybie offline, aby uniknąć wysyłania danych na zewnątrz.
- Dodaj mechanizm aktualizacji modeli (wersjonowanie) i możliwość szybkiego rollbacku w razie regresji jakości.

## Lokalizacja kluczowych funkcji
- **Anonimizacja/OCR**: `Cryptonet/Cryptonet.py` – funkcje `load_image`, `anonymize_image`.
- **Szyfrowanie/Odszyfrowanie**: `Cryptonet/Cryptonet.py` – funkcje `encrypt_file`, `decrypt_file`.
- **Walidacja haseł i logowanie**: `Cryptonet/Cryptonet.py` – sekcja walidacji haseł i autentykacji użytkownika.
