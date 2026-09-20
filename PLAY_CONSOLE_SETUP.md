# Google Play Console bağlantısı

Bu repo Google Play'e GitHub Actions üzerinden signed AAB gönderecek şekilde hazırlanmıştır.

## 1. Play Console'da uygulamayı oluştur
Google Play Developer API yeni bir uygulama kaydını sıfırdan oluşturamaz. Bu nedenle Play Console içinde bir kez:
- **Create app**
- App name: **Poyraz Kids**
- Default language: **Turkish – tr-TR**
- App or game: **App**
- Free or paid: **Free**
- Target audience: **2–6 yaş çocuklar ve ebeveynleri**
adımlarını tamamla.

Package name bu repoda sabittir:

`com.poyrazkids.app`

## 2. Play App Signing'i etkinleştir
Play Console > Test and release > App integrity altında **Play App Signing** kullan.

Bir **upload key** oluştur. Private key'i hiçbir zaman repoya commit etme.

## 3. Google Play Developer API service account
Google Cloud/Play Console entegrasyonunda bir service account oluştur ve Play Console'da uygulamaya release yetkisi ver.

Service account JSON private key'i repoya commit etme.

## 4. GitHub Actions Secrets
Repo > Settings > Secrets and variables > Actions > New repository secret:

- `ANDROID_SIGNING_KEY`: upload keystore dosyasının Base64 içeriği
- `ANDROID_SIGNING_ALIAS`: keystore alias
- `ANDROID_SIGNING_STORE_PASSWORD`: keystore password
- `ANDROID_SIGNING_KEY_PASSWORD`: key password
- `ANDROID_SERVICE_ACCOUNT_JSON`: service account JSON dosyasının tam içeriği

### Keystore'u Base64'e çevirme
macOS/Linux:
```bash
base64 -w 0 upload-keystore.jks
```

macOS'ta `-w` desteklenmiyorsa:
```bash
base64 < upload-keystore.jks | tr -d '\n'
```

PowerShell:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("upload-keystore.jks"))
```

## 5. İlk sürüm
İlk uygulama kaydı ve gerekli Play Console beyanları tamamlandıktan sonra:
GitHub > Actions > **Publish to Google Play** > Run workflow

İlk doğrulama için `internal` track önerilir. Test tamamlandıktan sonra aynı workflow `production` ile çalıştırılabilir.

## 6. Çocuk uygulaması beyanları
Gönderimden önce Play Console'da:
- Target audience and content
- Data safety
- Content rating
- Families Policy
- Privacy policy URL
alanlarını eksiksiz tamamla.

Mevcut v1 tasarımı reklam, analytics, hesap, konum, kamera ve mikrofon kullanmaz; dış içerikler ebeveyn geçidi arkasındadır.
