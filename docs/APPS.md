# FLUMM als Android- und iOS-App

Die App ist eine Capacitor-Hülle um `index.html`. App-ID: **de.daviddigital.flumm** · Version **0.10.2 (Build 17)**.

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

Jeder Push auf `main` erstellt automatisch ein Release (z. B. `v0.10.2-build17`) mit allen Dateien. Zusätzlich liegen sie unter Actions → Lauf → **Artifacts** (nur angemeldet).

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
