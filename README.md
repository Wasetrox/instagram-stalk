Instagram-Discord Mesaj Köprüsü ve Takip İzleyici

Bu proje, Instagram ile Discord arasında bir mesaj köprüsü kurar ve belirli bir Instagram kullanıcısının takipçi/takip edilen değişikliklerini izler. Bot, Instagram’dan gelen mesajları Discord’a iletir, Discord’dan gönderilen mesajları Instagram’a taşır ve takipçi/takip edilen ekleme/kayıp olaylarını detaylı embed mesajlarla bildirir. Ayrıca, bot başlatıldığında izlenen kullanıcının profil bilgilerini (takipçi sayısı, takip edilen sayısı, biyografi vb.) Discord’a gönderir. 🦾

## Özellikler ✨

- **Mesaj Köprüsü:** Belirli bir Instagram kullanıcısından gelen DM’leri Discord’a, Discord’dan gelen mesajları Instagram’a iletir.
- **Takipçi/Takip Edilen İzleme:**
  - Yeni takipçi bildirimleri (yeşil embed).
  - Takipçi kaybı bildirimleri (kırmızı embed).
  - Yeni takip edilen bildirimleri (mavi embed).
  - Takip etmeyi bırakma bildirimleri (turuncu embed).
- **Başlangıç Bilgisi:** Bot başlatıldığında, izlenen kullanıcının profil bilgilerini (kullanıcı adı, tam ad, takipçi/takip edilen sayısı, biyografi, gönderi sayısı, profil resmi) Discord’a gönderir.
- **Hata Yönetimi:** Instagram API hataları (`JSONDecodeError`, `login_required`) yakalanır ve otomatik oturum yenileme denenir.
- **Önbellekleme:** Kullanıcı bilgisi çağrılarını azaltmak için önbellek kullanılır.
- **Loglama:** Detaylı konsol logları ile hata ayıklama kolaylığı.

## Gereksinimler 📋

- Python 3.8 veya üstü
- Gerekli Python kütüphaneleri:

  ```bash
  pip install instagrapi discord.py python-dotenv
  ```
- Bir Instagram hesabı (oturum için)
- Bir Discord botu ve token
- `.env` dosyası ile ortam değişkenleri

## Kurulum ⚙️

1. **Depoyu Klonlayın:**

   ```bash
   git clone https://github.com/Wasetrox/instagram-stalk.git
   cd instagram-stalk
   ```

2. **Gerekli Kütüphaneleri Yükleyin:**

   ```bash
   pip install --upgrade instagrapi discord.py python-dotenv
   ```

3. **Ortam Değişkenlerini Ayarlayın:**

   - Proje kök dizininde bir `.env` dosyası oluşturun ve aşağıdaki bilgileri doldurun:

     ```
     INSTAGRAM_USERNAME=instagram_kullanici_adiniz
     INSTAGRAM_PASSWORD=instagram_sifreniz
     DISCORD_TOKEN=discord_bot_tokeniniz
     DISCORD_USER_ID=hedef_discord_kullanici_id
     SPECIFIC_SENDER_USERNAME=mesaj_beklenen_instagram_kullanici_adi
     MONITORED_USERNAME=takip_edilecek_instagram_kullanici_adi
     INSTAGRAM_2FA_ENABLED=true  # 2FA kullanıyorsanız
     ```
   - **Not:** `DISCORD_USER_ID`’yi bulmak için Discord’da geliştirici modunu açın, kullanıcıya sağ tıklayın ve "ID’yi Kopyala" seçeneğini kullanın.

4. **Oturum Dosyasını Silin (Gerekirse):**

   - Eğer oturum sorunları yaşıyorsanız, mevcut `session.json` dosyasını silin:

     ```bash
     rm session.json
     ```

5. **Botu Çalıştırın:**

   ```bash
   python wase.py
   ```

   - 2FA etkinse, konsolda doğrulama kodu girmeniz istenecek.

## Kullanım 🚀

Bot çalıştırıldığında:

1. Discord’a bağlanır ve `wasecikk#6559` gibi bir kullanıcı olarak giriş yapar.
2. İzlenen kullanıcının (`MONITORED_USERNAME`) başlangıç bilgilerini Discord’a gönderir:

   ```
   [wasetrox Profili]
   - Kullanıcı Adı: wasetrox
   - Ad Soyad: Wasetrox Kullanıcı
   - Takipçi Sayısı: 1234
   - Takip Edilen Sayısı: 567
   - Biyografi: Merhaba, ben Wasetrox!
   - Gönderi Sayısı: 89
   - Profil: [Tıkla](https://www.instagram.com/wasetrox/)
   ```
3. Instagram DM’lerini ve takipçi/takip edilen değişikliklerini izler, her olay için Discord’a embed mesajlar gönderir:
   - Yeni takipçi: Yeşil embed
   - Takipçi kaybı: Kırmızı embed
   - Yeni takip edilen: Mavi embed
   - Takip etmeyi bırakma: Turuncu embed
   - Yeni DM: Mor embed
4. Discord’dan gönderilen mesajları `SPECIFIC_SENDER_USERNAME`’a Instagram DM olarak iletir.

## Yaygın Hatalar ve Çözümler 🛠️

- **Hata:** `JSONDecodeError` **veya** `Status 201`

  - **Neden:** Instagram’ın API’si beklenmeyen bir formatta (ör. HTML) yanıt döndürüyor.
  - **Çözüm:**
    - `instagrapi`’yi güncelleyin: `pip install --upgrade instagrapi`
    - `session.json`’u silin: `rm session.json`
    - `MONITORED_USERNAME`’in gizli/askıya alınmış bir hesap olmadığını kontrol edin.
    - Bekleme süresini artırın (örn. `check_followers_following` için 900 saniye):

      ```python
      await asyncio.sleep(900)
      ```

- **Hata:** `login_required`

  - **Neden:** Instagram oturumu geçersiz.
  - **Çözüm:** `session.json`’u silin ve botu yeniden çalıştırın. 2FA varsa, doğrulama kodunu girin.

- **Hata:** `PyNaCl is not installed`

  - **Neden:** Ses özellikleri için eksik kütüphane.
  - **Çözüm:** Ses özelliği kullanmıyorsanız göz ardı edin veya yükleyin:

    ```bash
    pip install PyNaCl
    ```

- **Hata: Mesajlar veya takip bildirimleri gelmiyor**

  - **Çözüm:**
    - `.env` dosyasındaki kullanıcı adlarını kontrol edin.
    - `MONITORED_USERNAME`’in erişilebilir olduğunu ve `stanbr12025`’in bu hesabı takip ettiğini doğrulayın:

      ```python
      monitored_user = cl.user_info_by_username(MONITORED_USERNAME)
      cl.user_follow(monitored_user.pk)
      ```
    - Konsol loglarını inceleyin ve hataları paylaşın.


Lütfen kod tarzı için PEP 8 kurallarına uyun ve değişikliklerinizi açıklayan net commit mesajları yazın.

## Lisans 📜

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasını inceleyin.

## Proje Görüntüleme Sayısı

[![GitHub Views](https://komarev.com/ghpvc/?username=wasetrox&repo=discord-advanced-token-checker&label=Görüntüleme)](https://github.com/wasetrox/instagram-stalk)

## İletişim 📬

Sorularınız veya önerileriniz için Discord’dan [wasetrox](https://discord.com/users/312062402273345537)’a ulaşabilirsiniz! 😊
