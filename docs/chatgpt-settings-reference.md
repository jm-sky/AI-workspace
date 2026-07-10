# Referencja UX — Ustawienia aplikacji AI (na podstawie ChatGPT + najlepszych praktyk)

> Dokument referencyjny do projektowania ustawień aplikacji AI.

# Ustawienia

## 1. Profil

Dane użytkownika oraz podstawowe informacje o koncie.

### Dane profilu
- Imię / nazwa wyświetlana
- Zdjęcie profilowe
- E-mail

**Cel**
Identyfikacja użytkownika.

---

## 2. Konto i plan

Zarządzanie kontem oraz subskrypcją.

### Plan

Wyświetlenie aktualnego planu.

**Feature**
- aktualny plan
- limity
- porównanie planów
- upgrade

---

### Rozliczenia

Płatności i subskrypcje.

**Feature**
- historia płatności
- faktury
- anulowanie subskrypcji

---

## 3. Personalizacja

Ustawienia wpływające na sposób działania AI.

### Pamięć (Memory)

Przechowywanie trwałych informacji o użytkowniku.

**Feature**
- włącz/wyłącz pamięć
- lista wspomnień
- edycja
- usuwanie
- wyczyszczenie pamięci

Przykłady:

- Użytkownik preferuje TypeScript.
- Odpowiadaj po polsku.
- Ma dwoje dzieci.

---

### Instrukcje użytkownika (Custom Instructions)

Globalny prompt obowiązujący we wszystkich nowych rozmowach.

Przykłady:

- odpowiadaj krótko
- jestem programistą
- preferuję Vue
- nie zgaduj — zadawaj pytania

---

## 4. Charakterystyka odpowiedzi

Konfiguracja stylu komunikacji AI.

### Ciepły ↔ Chłodny

Poziom empatii.

- Ciepły
- Neutralny
- Chłodny

---

### Entuzjastyczny ↔ Rzeczowy

Poziom ekspresji.

- Entuzjastyczny
- Zbalansowany
- Rzeczowy

---

### Formatowanie

Preferowany sposób prezentowania odpowiedzi.

Opcje:

- akapity
- listy
- listy numerowane
- tabele
- nagłówki
- kod
- markdown

---

### Emoji

Poziom używania emoji.

- Nigdy
- Rzadko
- Normalnie
- Często

---

### Długość odpowiedzi

- Krótkie
- Średnie
- Szczegółowe

---

## 5. Profile AI (AI-generated summaries)

Automatyczne podsumowania tworzone przez AI na podstawie wielu rozmów.

To nie są pojedyncze wspomnienia, ale synteza wiedzy.

Przykładowe profile:

### O mnie

Ogólny opis użytkownika.

---

### Praca

Stanowisko, doświadczenie, technologie, styl pracy.

---

### Projekty

Najważniejsze projekty oraz ich aktualny stan.

---

### Dom

Informacje o domu, urządzeniach, instalacjach.

---

### Rodzina

Podsumowanie informacji rodzinnych.

---

### Zainteresowania

Tematy, o których użytkownik często rozmawia.

---

### Preferencje

Preferowany sposób współpracy z AI.

---

**Feature**

AI okresowo aktualizuje te profile.

Każdy profil można:

- przeczytać
- edytować
- usunąć
- odświeżyć

---

## 6. AI

Konfiguracja możliwości modelu.

### Domyślny model

- GPT-5
- szybki model
- model reasoning

---

### Narzędzia

Włączenie funkcji.

Przykłady:

- Search
- Deep Research
- Code Interpreter
- File Analysis
- Image Generation
- Voice
- Canvas

---

### Voice Mode

Rozmowa głosowa.

Opcje:

- wybór głosu
- język
- szybkość

---

## 7. Projekty

Ustawienia dotyczące projektów.

### Wiedza projektu

- pliki
- dokumentacja
- instrukcje

---

### Prompt projektu

Instrukcje obowiązujące tylko w projekcie.

---

### Modele projektu

Model domyślny dla projektu.

---

## 8. Integracje

Połączone aplikacje.

Przykłady:

- GitHub
- Google Drive
- Microsoft 365
- Notion
- Slack
- Dropbox

---

## 9. Dane i prywatność

### Historia rozmów

- zapisuj historię
- nie zapisuj

---

### Trenowanie modeli

Czy rozmowy mogą być użyte do ulepszania modeli.

---

### Eksport danych

Pobranie wszystkich danych.

---

### Usuń konto

Trwałe usunięcie konta.

---

## 10. Bezpieczeństwo

### Logowanie

Metody logowania.

---

### Sesje

Lista zalogowanych urządzeń.

Możliwość wylogowania.

---

### Uwierzytelnianie

- MFA
- Passkeys
- Klucze bezpieczeństwa

---

## 11. Wygląd

### Motyw

- Jasny
- Ciemny
- Systemowy

---

### Kolor akcentu

Zmiana koloru interfejsu.

---

### Dostępność

- większy tekst
- kontrast
- animacje

---

## 12. Powiadomienia

Konfiguracja powiadomień.

Przykłady:

- zakończenie odpowiedzi
- zadania
- przypomnienia
- projekty

---

## 13. Funkcje eksperymentalne

Nowe funkcje dostępne przed oficjalnym wydaniem.

---

## 14. Pomoc

### Centrum pomocy

FAQ.

---

### Kontakt

Zgłoszenie problemu.

---

### Informacje o aplikacji

- wersja
- licencje
- regulaminy

---

# Architektura pamięci AI

Najlepszym rozwiązaniem wydaje się podział pamięci na cztery poziomy.

## 1. Fakty (Memory)

Pojedyncze trwałe informacje.

Przykłady:

- używa FastAPI
- lubi Vue
- odpowiadaj po polsku

---

## 2. Profile (AI Summaries)

Podsumowania tworzone automatycznie przez AI.

Przykłady:

- Praca
- Dom
- Projekty
- Rodzina
- Zainteresowania

Są znacznie bogatsze niż pojedyncze wspomnienia.

---

## 3. Projekty

Pamięć dotycząca konkretnego projektu.

Przykłady:

- architektura
- decyzje
- TODO
- dokumentacja
- pliki

Nie wpływa na inne projekty.

---

## 4. Sesja

Kontekst bieżącej rozmowy.

Po zakończeniu rozmowy może zostać:

- odrzucony,
- zapisany jako Memory,
- dodany do Profilu,
- zapisany do Projektu.

---

# Dlaczego taki podział jest dobry?

AI nie musi analizować setek pojedynczych wspomnień.

Zamiast tego korzysta z:

1. Faktów (Memory)
2. Podsumowań (Profiles)
3. Wiedzy projektu
4. Kontekstu aktualnej rozmowy

To rozwiązanie jest bardziej skalowalne, szybsze i daje użytkownikowi większą kontrolę nad tym, co AI pamięta oraz w jaki sposób wykorzystuje zgromadzoną wiedzę.