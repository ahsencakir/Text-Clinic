# Özellik Seçimi Raporu

Bu rapor, baseline modeller eğitilirken kullanılan metin özelliklerinin
nasıl seçildiğini özetler.

## Genel Strateji

- Metinler Türkçe karakter destekli regex ile tokenlara ayrıldı.
- Çok genel Türkçe stopword kelimeleri çıkarıldı.
- Frekansı 2'den düşük tokenlar sözlüğe alınmadı.
- Her görev için en fazla 5000 token kullanıldı.
- Örneği çok az olan sınıflar eğitimden çıkarıldı.
- Her sınıf için log olasılık farkına göre ayırt edici tokenlar raporlandı.

## Görev Bazlı Özellik Özeti

| Görev | Eğitim Satırı | Sınıf Sayısı | Sözlük Boyutu |
|---|---:|---:|---:|
| Konusma amaci | 5296 | 34 | 4666 |
| Duygu | 5353 | 28 | 4712 |
| Sarkazm | 5823 | 2 | 5000 |
| Tani asamasi | 5109 | 29 | 4530 |
| Organ/sistem | 2711 | 31 | 2680 |

## Sınıflara Göre Ayırt Edici Tokenlar

### Konusma amaci
- `acil`: şoka, alamıyor, yüzünden, oksijen, gerekli, apselerini, kaşıkları, sağlayabiliriz, defibrilasyon, ateşim, septik, örnek
- `açıklama`: yok, var, kan, değil, olabilir, kalp, kadar, sadece, normal, çok, hasta, çıktı
- `bilgi talebi`: ttp, geldiğini, gizli, acil, geri, testlerde, sırtını, kızartır, ölen, hastalar, tucker, boğulmadan
- `değerlendirme`: yok, değil, belirtisi, kalp, normal, ekg, içki, belirgin, iyi, aritmi, olmaz, alerjik
- `durum bilgilendirmesi`: sınırlı, üretiyor, onkoloji, üriner, almakta, bulamazsak, olmamız, doktorların, ameliyathaneyi, tomografide, çekiyor, kolu
- `durum değerlendirme`: düşük, rabdomyosarkom, elin, meningeal, alveoler, bilgisayarlı, elinde, elini, çok, doku, tomografi, omurilik
- `emir`: yapın, başlatın, edin, mri, gidin, alın, interferona, dozu, fib, muayene, arayın, hipofiz
- `gözlem`: lenf, var, bak, yükseliyor, seviyeleri, kalbinin, sağ, yok, bölge, şimdi, ona, kanama
- `hipotez`: olabilir, yol, enfeksiyon, uyuyor, sendromu, açabilir, beyin, açıklayabilir, enfeksiyonu, açıklar, kalp, aşırı
- `hipotez önerme`: loa, virüsü, sendromu, brugada, ilişkiye, feokromasitoma, magnezyum, tirotoksikoz, olabilirdi, basınçlı, nodoza, anlaşılıyor
- `itiraz`: yok, çiçek, zaten, değil, hastalığı, ancak, negatif, kalbi, yoktu, hücreleri, ekg, uyuşturucu
- `karar`: yapalım, yapın, mri, eko, text, type, yapmalıyız, planlanacak, uygulayın, transözofageal, cerrahi, kontrastlı
- `prosedür açıklama`: tüberküloz, akciğerini, insülin, iki, kalsiyum, yıl, kemoterapi, tüberküloza, pankreasta, dekstroz, dirençli, şekeri
- `raporlama`: çıktı, yok, toksin, kardiyomiyopatisi, başlattım, salmonella, normal, izi, negatif, diyalize, çocuğun, etti
- `reçete`: başlayın, heparin, gösteriyor, şimdi, iliğini, bronşlarda, parasentez, vücuda, oğlum, saturasyonu, hayatımı, bitiyor
- `sonuç`: sonrası, resüsitasyon, idrarda, geldi, gösterdi, viral, bulundu, yüksek, protein, negatif, serolojiler, troponin
- `sorgulama`: bozukluğu, mı, etrafını, önleyici, kaybına, düzelme, başladıktan, cefuroxime, sorgulandı, kyle, konversiyon, günlerde
- `soru`: mı, peki, miyim, var, herhangi, yok, düşünüyorsunuz, nedir, mr, kadar, eeg, geri
- `soru sorma`: evet, böbrek, herhangi, anladım, fonksiyonu, osteopeni, böbreği, mı, misin, anlamına, genç, söyledi
- `talep`: yapın, basın, ona, sıtma, miligram, istiyorum, verin, hemen, biyopsisi, coartem, kemiğin, parasentez
- `talimat`: yapın, başlayın, edin, testi, hemen, alın, verin, çekin, ona, dna, hastaya, bakın
- `tanı`: olabilir, hava, ciddi, hastada, gelişti, ağrı, yol, bulundu, açıklayabilir, saptandı, görsel, kondu
- `tanı koymak`: mavimsi, asidoz, ödemi, teşhis, belirtileri, açıklıyor, demek, tümör, bölümüne, hipoksi, şüpheli, davranışların
- `tanısal`: yükselmiş, toksikoloji, kalsiyum, açıklar, test, temiz, damarlarının, sersemlik, michael, sokun, pıhtılaşmıyor, joe
- `tedavi`: başlandı, tedavisi, tedavi, başlayın, verin, vermeye, kesmek, hastayı, antibiyotik, uygulandı, verildi, işe
- `tedavi önerisi`: tanı, böbreklerinden, mikotik, serviste, ayırır, yaktığı, olive, onaylamak, önünde, ediyordum, aşağıya, vücudundaki
- `test`: testi, mr, bt, yapın, yapacağım, çekin, antikor, kültürü, taraması, normal, yapmamız, isteyin
- `test talebi`: felci, kafa, house, ataksiyi, böbreklerinden, masajı, sırtını, edenin, kaymış, olduğunda, löseminin, almaz
- `teşhis`: olabilir, hastalığı, dic, artı, hücreli, paraneoplastik, yok, hücreleri, oluyor, düşük, olmuş, text
- `teşhis sorgusu`: kötü, edenin, birbirini, cihazı, olun, çalışıyorsun, haline, bezlerine, eklediğinde, sağlamaya, arıyorum, yapmaktan
- `uyarı`: eğer, yüz, felç, emma, diyaframa, solunum, tetikler, varsa, olmayabilir, sıvıyla, böbreklerini, iki
- `öneri`: yapılmalı, olacak, biyopsi, azalması, etkilidir, kalmadı, ver, giden, verelim, kateter, edin, apse
- `şaka`: vardır, kokar, dikişleri, harika, adam, sadece, iyi, kontrol, penisimdeki, deodorant, herkes, hastalıkları
- `şikayet bildirimi`: öksürük, karaciğerinin, fazladan, adamın, si, açık, ilaç, yapılmasını, çağrı, tıkanıklığa, bölümüne, rutin

### Duygu
- `acil`: trakeotomi, kyle, hava, entübe, nefes, oksijen, yolunu, etmemiz, yolu, verin, trakeostomi, lüppe
- `acı`: ağrıyor, idrar, başım, gerekli, midem, kramp, bacağıma, fizik, şişlik, ağrım, ağrın, girdi
- `alaycı`: bazen, harika, olabilir, sıcak, değil, sadece, herkes, vardır, hiçbir, vicodin, iyi, kontrol
- `analitik`: olabilir, burada, açıklar, sendromu, enfeksiyonu, sistemini, kaybı, artı, sorunu, cinsel, olmuş, travma
- `ciddi`: var, kan, olabilir, kalp, iki, eğer, beyin, hasta, enfeksiyon, gerekiyor, nefes, tüberküloz
- `düşünceli`: olabilir, peki, artı, sebep, akciğeri, benziyor, sendromu, nöbetler, hastalığı, safra, tansiyon, kalp
- `emin`: yok, açıklıyor, yetmezliğine, soğuk, kesinlikle, değil, olmalı, beyninde, başlatacağız, kurdeşen, atmış, belirtisi
- `empati`: metabolik, yeniden, zayıfsa, ilerlerse, gelişebilir, lezyona, azalır, gerekebilir, bebeğin, mesane, ameliyat, gerçekten
- `emredici`: edin, örneği, yapın, bos, başlayın, bulmak, tedavisine, çekin, insanların, etanol, düzeltebilir, takın
- `endişe`: fazla, tansiyonu, kanama, var, testleri, hastanın, nöbet, ateşin, iflas, kan, çok, ciddi
- `kararlı`: başlayın, tümör, sıvı, testosteron, tedavi, yapın, leptospiroz, iyi, plazmaferez, edin, gerekiyor, bakteriyel
- `kaygı`: gerekli, vestibüler, dönmen, denge, kaybın, testler, miyim, baş, ani, ölebilir, yüksek, diyaliz
- `kaygılı`: pnömoni, durumda, yüzünden, dersi, konjonktiviti, bilimi, kutuda, alınması, tutulumunu, duyuluyor, ulaşmış, kurbanın
- `korku`: edin, hiperventile, anormallikler, kardiyak, sıvıyla, çekmemiz, granülom, şeyler, kimse, almıyor, arrest, kalbi
- `meraklı`: senkop, ellerini, peki, herhangi, olabilir, hemoliz, başladıktan, gelişmemiş, kusuru, ağırlık, taşikardiye, görünüp
- `nötr`: olabilir, yok, hasta, var, normal, değil, kalp, yol, hastada, beyin, negatif, hastalığı
- `odaklanmış`: dozu, olduğu, vaskülit, pozitif, demek, ayrıca, dalaktan, artır, kasının, patlamak, hareketi, fikri
- `otoriter`: yapın, gidip, anjiyogram, çekin, arayın, bak, lenf, nodu, çek, ret, elini, yavaşça
- `panik`: ani, acil, gerekli, müdahale, yardım, istiyorum, kalp, kanaması, iltihabı, durması, ekg, mide
- `sakin`: tucker, vermeliyiz, hücrelerini, arsenik, temiz, akyuvar, yapacağız, chase, nin, ın, herhangi, steroid
- `umut`: öksürük, şurubu, şeker, düşmeye, kocam, hastalığın, kez, altına, felci, ilk, hareket, başladı
- `umutlu`: kız, antibiyotikler, gerekir, bulduk, donör, bebeğe, donörden, vermeyi, çıkarınca, apseyi, çıkarırız, bulup
- `yorgunluk`: uyku, baş, yapmalıyız, hastalandı, fakat, olun, tahrip, burnun, hastalar, verebilirsin, sırtını, ölen
- `öfke`: olmadığı, onun, hastayı, rektum, gerekçesi, ttp, istiyor, hastanede, nedir, dışarı, nakil, sürekli
- `üzgün`: yağ, temizliği, hafızasını, engelleyecek, embolisini, karım, sakat, edilemez, birkaç, olduğumu, yapmış, ameliyat
- `üzüntü`: olacak, std, hayır, ihtiyacı, çıktığında, ilaçların, verdiğiniz, tecavüz, bitiyor, kaptı, sepsis, böbreklerine
- `şaşkın`: metal, altı, kitle, bandı, mavi, buldum, atış, alerjisi, yaşındaki, bize, beş, tümör
- `şaşkınlık`: kontrol, sıvı, mıknatısı, zarı, almaz, lekeler, kateterizasyon, embolizasyon, uyguladım, tıkanma, kutsal, vakti

### Sarkazm
- `not_sarcastic`: ani, mr, hastada, nöbet, temiz, gerekli, taraması, müdahale, otoimmün, ciddi, oksijen, acil
- `sarcastic`: dünya, bilir, kestikten, mıdır, ghb, desteğe, davranıp, tartışıyoruz, boğuldu, gerektiğinde, anladım, utanılacak

### Tani asamasi
- `acil`: kyle, miligram, verin, resüsitasyon, çekilin, diazepam, ona, oksijen, şok, başlayın, hızı, sonrası
- `araştırma`: insanların, laparotomi, bağımlı, hap, mı, yok, izi, edin, cıva, güçlü, ödem, tedaviye
- `ayırıcı_tanı`: olabilir, enfeksiyon, sendromu, nörolojik, eksikliği, peki, güvenli, açıklar, normal, kanama, temiz, hastalığı
- `başlangıç`: adam, saattir, kutsal, telefon, farkındalık, çığlık, hayatta, kırılmış, parasentez, boşaltın, ülserler, yanıyor
- `değerlendirme`: hastada, yok, var, değil, hastanın, kan, hasta, olabilir, çok, kalp, görünüyor, böbrek
- `erken`: kalsiyum, kalbindeki, öksürüğü, hesaba, gördü, öksürür, sok, akıntısı, bayıldı, 32, karbonmonoksit, örnek
- `erken evre`: gerekli, ani, dönmen, testleri, baş, kaybın, denge, ağrın, yapacağız, alerji, testler, vestibüler
- `erken tanı`: etti, akciğerlerine, chase, aptalca, tutunup, fakat, çağrı, nöroloji, bölümüne, biyopsisini, albümin, tahrip
- `hipotez`: olabilir, hastalığı, yol, tümör, değil, sendromu, açıklar, yok, uyuyor, enfeksiyon, ağrısı, var
- `ileri evre`: felci, dilerim, farkında, löseminin, kaymış, yerleştireceğiz, sınırlı, enfeksiyonuna, bezleri, eminim, sırtını, antifungal
- `ilk muayene`: kötü, şeyler, karaciğerinin, açık, si, üst, kafa, house, hasta, alınabilir, parçasını, girdiniz
- `ilk_değerlendirme`: lepra, herkes, kanser, şeyi, insanlar, ölmek, çirkin, etkileşimler, dünya, değiştirmez, beklenmeyen, sayılır
- `itiraz`: sistem, nerede, vasküler, açıklamaz, kafa, olsaydı, içi, eğer, hiperakut, öncelikle, gerginliği, yetmezliğinden
- `izlem`: aritmi, trombüs, chagas, taşır, masada, detoks, ritmi, stabil, riski, hızlı, sonrası, ihtimali
- `kesin_tanı`: değil, var, radyasyon, uzun, ipecac, tümör, ameliyat, kalp, kontrast, tüm, burada, tanı
- `kritik`: acil, ani, gerekli, müdahale, yardım, iltihabı, istiyorum, şok, konsültasyonu, ekg, cerrahi, beyin
- `kronik`: sirozu, gerekli, konsültasyonu, ani, nefroloji, hepatoloji, istiyorum, ağrılarım, şeker, hastalığın, testi, eklem
- `orta evre`: ağrın, gerekli, kaybın, göz, testleri, ölçümü, fizik, sırt, bel, ağrıyor, yapalım, cevap
- `semptom_tanıma`: ian, arrest, yükseliyor, geçirdi, oluyor, hemodinamik, melinda, oğlunuzun, grace, üzerindeki, öldürmek, küçüldü
- `tanı`: text, type, disease, var, reaksiyon, olabilir, symptom, alerjik, iki, yol, veba, tüberküloz
- `tanı araması`: öksürük, uyuyor, yapmalıyız, sağlamaya, embolizasyon, şişe, şeyleri, baskılayıcı, bulantın, ayırır, eklediğinde, şurubu
- `tanı koymak`: metanol, eroin, susuz, demek, serum, teşhis, uyuşturucu, sebep, açıklıyor, olabilir, şimdi, davranışların
- `tedavi`: başlayın, verin, tedavi, hastaya, tedavisi, steroid, başlandı, ona, tedavisine, edin, text, type
- `tedavi sonrası`: ttp, ölen, löseminin, aşk, edenin, kalitesini, yapacak, mikotik, hastalar, inanamıyorum, işlemi, değerini
- `tedavi_planı`: yeniden, iş, küçük, bazen, basınç, anjiyom, kaybolabilir, emilince, işaretleri, bulamıyoruz, sistemden, desteğe
- `test`: yapın, bt, biyopsisi, mr, biyopsi, taraması, negatif, yok, alın, testi, eeg, kan
- `test / tetkik`: doğrulamak, değildi, andrews, pcr, sıvısı, sayımı, omurilik, elektriksel, testi, göstermedi, anormal, eeg
- `test_sonucu`: dün, pet, negatifti, si, yoktu, ekg, sol, vejetasyon, çektim, etrafını, etmeyi, dalında
- `test_süreci`: bt, normal, bize, immüno, göstermeyebilir, nöral, çekti, göreceğiz, baktınız, antifosfolipid, berrak, arada

### Organ/sistem
- `akciğer`: akciğer, pulmoner, nefes, oksijen, solunum, akciğerleri, akciğerlerde, emboli, devam, entübe, pnömoni, sıvı
- `akciğerler`: akciğer, müdahale, gerekli, ani, acil, embolisi, iltihabı, yetmezliği, havasız, nedir, ettikten, solunumu
- `bacak`: ağrı, bacak, bacağındaki, bacağım, bacağımda, ağrısı, bacağı, bacağıma, şiddetli, house, hareket, düşündürüyor
- `bağırsak`: bağırsak, ishal, bağırsağının, ağrısı, bağırsakta, kolonoskopi, tıkanıklığı, hava, anjiyodisplazi, kamera, yetişkinlerde, bağırsaklarında
- `bağışıklık`: bağışıklık, sistemini, steroid, sistemi, otoimmün, sitokin, fırtınası, çalışıyor, böyle, hastalık, yapabilir, tablo
- `bağışıklık sistemi`: bağışıklık, aids, sistemini, darlığım, ige, immün, biyolojik, sendromu, ay, şok, karşı, alerjik
- `beyin`: beyin, mr, nöbet, nörolojik, eeg, baş, olabilir, tümör, hasta, lob, temporal, basınç
- `boyun`: boyun, boynun, çip, ediyorum, kanser, damarları, şişliği, solgun, boynunu, morarma, tarayın, gerekiyordu
- `burun`: burun, kanaması, izleri, koterizasyon, aslında, öksürür, çıkıyor, reflü, yapıldı, kanaman, bel, bulursak
- `böbrek`: böbrek, böbrekleri, idrar, iflas, diyalize, böbrekler, böbreği, ediyor, protein, taşı, fonksiyonları, yetmezliği
- `cilt`: alerji, cilt, döküntü, döküntüler, yapın, geçer, küf, biyopsi, büyük, kırmızı, testi, testleri
- `damar`: vasküler, pıhtı, damar, vaskülit, damarlarını, poliarterit, şüphesi, vasküliti, problem, kalmadı, antikorları, olursa
- `deri`: deri, döküntü, görülen, irin, bulaşan, genellikle, doku, negatifti, gösterebilir, vaskülit, şekilde, alerjik
- `genel`: kanser, hasta, şeyi, test, herkes, insanlar, ölecek, deneysel, bazen, küçük, semptomları, ilaçları
- `göz`: göz, görme, gözü, sağ, optik, göremiyorum, vardı, gözlerinde, korneada, gözüm, gözde, körlük
- `göğüs`: göğüs, ağrısı, nefes, arasına, tuhaf, göğsümde, göğsünde, göğsüm, röntgeni, si, hissediyor, cerrahi
- `kalp`: kalp, ekg, kalbi, hızı, kalbini, kardiyak, krizi, eko, ani, ritim, acil, kalpte
- `kan`: kan, pıhtılaşma, kırmızı, bozukluğu, kanı, kanama, dic, alın, düşük, paneli, sayımı, negatif
- `karaciğer`: karaciğer, karaciğeri, hepatit, konsültasyonu, hepatoloji, iflas, yetmezliği, biyopsisi, gerekli, karaciğerine, karaciğerinde, kadar
- `karın`: karın, ağrısı, abdominal, oda, grey, turner, karında, type, text, mevcut, hastada, kesi
- `kas`: kas, glikojen, türü, görünüyor, iki, tekrar, felç, şiddetli, açıklar, rapor, edemem, sayıda
- `kemik`: kemik, osteopeni, osteomyelit, röntgen, yoğunluğunda, basıyordur, kırılmış, plağı, zarına, azalma, iliği, enfeksiyon
- `kol`: sanki, kolum, löseminin, aşısı, asla, ampute, kolunu, kuduz, kol, kolu, sol, kolundaki
- `kulak`: kulağında, duyamıyorum, implant, hamam, işitsel, hiçbir, yayılmış, böcek, hazır, 27, gitmiş, psikoz
- `mide`: mide, endoskopi, kusma, kanaması, kusmam, midem, acil, ani, istiyorum, midesinin, kustu, tekrar
- `nötr`: zehir, çocuk, pestisit, aynı, tedavi, matt, organofosfatlar, hidrolaz, paratiyon, disülfoton, kullanmış, etil
- `omurilik`: omuriliğe, omurilik, miyelit, transvers, mr, ponksiyon, yapıyor, çekin, sistemi, felç, sıvı, bikarbonat
- `pankreas`: pankreas, pankreatit, nesidioblastoma, insülin, pankreasta, pankreasında, kitle, pankreatik, selektif, insülinoma, küçük, gerekli
- `sinir`: sinir, ekarte, nöropati, barr, sinirindeki, guillain, crps, duyusal, sinirlere, otonom, skleroz, multipl
- `sinir sistemi`: nörolojik, motor, sinir, felç, ivig, mevcut, koordinasyon, paralizi, bozarak, emg, progresif, istemsiz
- `tüm vücut`: gerekli, ani, acil, şok, müdahale, antidot, yıkama, kanama, travma, mide, zehirlenmesi, durumunda
