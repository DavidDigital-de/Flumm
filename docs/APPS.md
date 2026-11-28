# FLUMM als Android- und iOS-App

Die App ist eine Capacitor-Hülle um `index.html`. App-ID: **de.daviddigital.flumm** · Version **0.27.0 (Build 55)**.

## Wie die Builds entstehen
Bei jedem Push auf `main` baut GitHub Actions (Reiter **Actions** → „Apps bauen“) automatisch:

| Datei | Wofür | Voraussetzung |
|---|---|---|
| `FLUMM-v…-debug.apk` | direkt aufs Android-Handy installieren und testen | keine |
| `FLUMM-v…-release.aab` | Upload in die Google Play Console | Android-Signatur-Secrets |
| `FLUMM-v…-release.apk` | signierte APK zum Weitergeben | Android-Signatur-Secrets |
| `FLUMM-v…-unsigned.ipa` | Prüfung des iOS-Builds / Sideloading (z. B. AltStore) | keine |
| TestFlight-Upload | iPhone-Test + App-Store-Einreichung | Apple-Secrets |

**Direkter Download der neuesten APK (auch am Handy):**
https://github.com/DavidDigital-de/Flumm/releases/latest/download/FLUMM.apk

Jeder Push auf `main` erstellt automatisch ein Release (z. B. `v0.27.0-build55`) mit allen Dateien. Zusätzlich liegen sie unter Actions → Lauf → **Artifacts** (nur angemeldet).

## Android-Signatur einrichten (einmalig)
1. Keystore erstellen (gut aufbewahren – ohne ihn keine Updates im Play Store!):
   `keytool -genkeypair -v -keystore flumm.jks -alias flumm -keyalg RSA -keysize 2048 -validity 10000`
2. Als Base64 umwandeln: `base64 -w0 flumm.jks` (Windows: `certutil -encode flumm.jks out.txt`)
3. Im Repo unter **Settings → Secrets and variables → Actions** anlegen:
   - `FLUMM_KEYSTORE_BASE64` – Inhalt aus Schritt 2
   - `FLUMM_KEYSTORE_PASSWORD` – Keystore-Passwort
   - `FLUMM_KEY_ALIAS` – `flumm`
   - `FLUMM_KEY_PASSWORD` – Schlüssel-Passwort

## iOS / TestFlight einrichten (einmalig)
Voraussetzung: Apple Developer Program (99 €/Jahr).
1. In App Store Connect die App mit der Bundle-ID `de.daviddigital.flumm` anlegen.
2. App Store Connect → Benutzer und Zugriff → Integrationen → **API-Schlüssel** (Rolle „App-Manager“) erstellen, `.p8` herunterladen.
3. Secrets anlegen:
   - `IOS_TEAM_ID` – Team-ID (Developer-Konto → Mitgliedschaft)
   - `ASC_KEY_ID`, `ASC_ISSUER_ID` – vom API-Schlüssel
   - `ASC_KEY_P8_BASE64` – `.p8`-Datei als Base64
Dann signiert der Workflow automatisch und lädt den Build zu TestFlight hoch.

## Lokal bauen (optional)
```
npm ci
mkdir -p www && cp index.html www/ && cp -r fonts www/
npx cap sync
npx cap open android   # Android Studio
npx cap open ios       # Xcode (nur Mac)
```

## Versionen hochzählen
Bei jeder Auslieferung: `VERSION`/`BUILD` in `index.html`, `version` in `package.json`,
`versionName`/`versionCode` in `android/app/build.gradle`, `MARKETING_VERSION`/`CURRENT_PROJECT_VERSION` in `ios/App/App.xcodeproj/project.pbxproj`.

## Noch offen
- Google Play Games (Erfolge, Bestenlisten) – braucht die IDs aus der Play Console
- Firebase (Duelle, Freunde, Push) – braucht `google-services.json` / `GoogleService-Info.plist`
- AdMob (Werbung) – braucht App- und Anzeigenblock-IDs

## Vollbild
Android: `MainActivity.java` blendet Status- und Navigationsleiste immersiv aus (Wischen vom Rand zeigt sie kurz). iOS: `UIStatusBarHidden` in Info.plist + `StatusBar.hide()` im Spiel.

## Werbung (AdMob)
Eingebunden über `@capacitor-community/admob` (8.4.2). **Android live** (App-ID ca-app-pub-8873350241195536~6331311803, Mit Prämie „Rettung“ …/8454912264, Interstitial „Zwischen Runden“ …/1729721819). iOS noch Testanzeigen.

Platzierungen: Video (Belohnung) für *Weiterspielen* im Endlos-Modus (1× pro Lauf, ab Insel 5), *Münzen ×2* nach Spielen und *Gratis-Medizin*. Werbepause (Interstitial) nach jedem 3. Spiel, höchstens alle 150 s. Kein Banner. Datenschutz-Abfrage (UMP) beim Start, iOS-Tracking-Abfrage (ATT), änderbar in den Einstellungen.

### Auf echte Werbung umstellen
1. In AdMob die App „Flumm“ für Android (und iOS) anlegen → **App-ID** (`ca-app-pub-…~…`).
2. Je Plattform zwei Anzeigenblöcke anlegen: **Interstitial** und **Mit Prämie** → IDs (`ca-app-pub-…/…`).
3. App-ID eintragen: `android/app/src/main/res/values/strings.xml` (`admob_app_id`) und `ios/App/App/Info.plist` (`GADApplicationIdentifier`).
4. Anzeigenblock-IDs in `index.html` bei `ADS_CFG` eintragen und `live:true` setzen.
5. In AdMob unter *Datenschutz & Mitteilungen* eine DSGVO-Mitteilung (Einwilligung) für die App erstellen und veröffentlichen.
6. Play Console: *App-Inhalte → Werbung: Ja* und *Werbe-ID* angeben; `app-ads.txt` auf der Entwickler-Website hinterlegen.

## Bestenlisten (Google Play Spiele)
Eigene Brücke `PlayGamesPlugin.java` (PGS v2, play-services-games-v2 21.0.0); iOS Game Center folgt. Drei Bestenlisten: Tageslauf, Endlos, Duell-Siege (Zahl, höher = besser). Tageslauf/Endlos senden einen Score-Tag `t<Sek>p<Perfekt>c<Münzen>b<Beeren>`; die App zeigt die Top 25 inkl. dieser Werte in einer eigenen Ansicht (Heute/Woche/Gesamt). Solange `LB_CFG` in `index.html` leer ist, zeigt die App nur lokale Rekorde.

Test-APK ist jetzt immer mit `android/app/flumm-debug.keystore` signiert (nicht geheim):
- SHA-1: `EA:07:65:A5:0C:6E:78:30:F3:A7:8D:AF:A5:F8:54:6A:BF:35:05:C4`

### Einrichten
1. Play Console → Flumm → *Play-Spieldienste* → *Einrichtung und Verwaltung* → Projekt erstellen.
2. *Anmeldedaten* → Android-Anmeldedaten mit Paketname `de.daviddigital.flumm` und obigem SHA-1 (Test-APK) anlegen; für den Store zusätzlich den SHA-1 des App-Signaturschlüssels (Play Console → App-Integrität).
3. *Bestenlisten* anlegen (siehe Liste oben).
4. *Tester* hinzufügen (eigenes Google-Konto) und veröffentlichen.
5. Projekt-ID (Zahl) → `android/app/src/main/res/values/games-ids.xml` + Manifest-Eintrag `com.google.android.gms.games.APP_ID`; Bestenlisten-IDs (`CgkI…`) → `LB_CFG.android` in `index.html`.


## Update-Hinweis (In-App-Update)
- Plugin `@capawesome/capacitor-app-update`. Gibt es bei Google Play eine neuere Version, zeigt das Hauptmenü „Neue Version verfügbar – Aktualisieren“ (flexibles Update im Hintergrund, danach „Neu starten“). Mit ✕ pro Version ausblendbar.
- Funktioniert nur bei Installationen aus Google Play (auch geschlossener/interner Test), nicht bei der Debug-APK.
- iOS: vorbereitet, aktiv sobald `IOS_APP_ID` in `index.html` eingetragen ist (öffnet den App-Store-Eintrag).


## Sprache
- Die App nutzt die Systemsprache: Geräte mit Deutsch (de-DE, de-AT, de-CH …) → Deutsch, alle anderen → Englisch.
- Umschalter in den Einstellungen: Auto / DE / EN (Spiel lädt kurz neu).
- Übersetzungen: `EN` (Texte im Code, Schlüssel = deutscher Text), `EN_H` (feste Texte im HTML), `HELP_EN` (Hilfe), `CHANGELOG_EN`. Neue Texte im Code mit `L('…')` umschließen und in `EN` ergänzen.
