# House MD Türkçe Medikal Diyalog NLP Projesi

Bu proje, House MD dizisinden oluşturulan Türkçe hasta-doktor diyalog veri seti
üzerinde doğal dil işleme yöntemleri kullanarak medikal konuşma bağlamını
analiz etmeyi amaçlar.

## Proje Konusu

**House MD Türkçe medikal diyaloglarında konuşma amacı, duygu ve sarkazm
analizi**

Ana problem, bir diyalog cümlesinin metnine bakarak o cümlenin hangi iletişim
amacını taşıdığını, hangi duygu tonuna sahip olduğunu ve sarkazm içerip
içermediğini tahmin etmektir. Projeyi güçlendirmek için organ/sistem ve tanı
süreci aşaması da yan sınıflandırma görevleri olarak ele alınır.

## Araştırma Soruları

- Medikal diyaloglarda konuşma amacı yalnızca metinden tahmin edilebilir mi?
- Sarkazm içeren doktor replikleri klasik metin özellikleriyle ayrıştırılabilir mi?
- Duygu sınıfları, medikal terimler ve konuşmacı tarzı ile ilişkili midir?
- Semptom, test, ilaç ve prosedür bilgileri model başarısını artırabilir mi?
- Organ/sistem veya tanı aşaması gibi medikal bağlam etiketleri metinden
  çıkarılabilir mi?

## Veri Seti

Ham veri dosyası:

```text
data/raw/house_md_dataset.csv
```

Veri seti 7282 satırdan oluşur. Temel kolonlar:

- `season`, `episode`, `speaker`
- `Symptom`, `Test`, `Drug`, `Procedure`
- `Intent`, `diagnosis_stage`, `Sarcasm`, `Emotion`, `Organ`
- `correct_prediction`, `model_prediction`
- `text`
- `medical_entities`

## Yöntem

### 1. Veri İşleme

`src/data_prep.py` scripti aşağıdaki işlemleri yapar:

- CSV dosyasını UTF-8 olarak okur.
- Boş metinleri veri setinden çıkarır.
- Metin alanındaki gereksiz boşlukları temizler.
- `Intent`, `Emotion`, `Sarcasm`, `diagnosis_stage` ve `Organ` etiketlerini
  normalize eder.
- Büyük/küçük harf farklılıklarını birleştirir.
- `-`, `none`, boş değer gibi geçersiz etiketleri `unknown` olarak işaretler.
- `medical_entities` kolonundaki JSON benzeri varlık listesini ayrıştırır.
- Semptom, test, ilaç ve prosedür varlığı için boolean özellikler üretir.
- Temizlenmiş veri setini `data/processed/house_md_clean.csv` olarak kaydeder.

### 2. Özellik Çıkarımı

İlk modelde metinlerden aşağıdaki özellikler çıkarılır:

- Türkçe karakterleri destekleyen tokenizasyon
- Küçük harfe çevirme
- Türkçe stopword temizleme
- Bag-of-words kelime frekansı temsili
- Medikal varlık sayısı ve varlık türü özetleri
- `has_symptom`, `has_test`, `has_drug`, `has_procedure` yardımcı özellikleri

### 3. Özellik Seçimi

`src/train_baselines.py` eğitim sırasında özellik seçimini şu şekilde yapar:

- Çok nadir geçen kelimeleri eler.
- En sık ve en kullanışlı ilk 5000 tokenı sözlüğe alır.
- Her görev için örneği çok az olan sınıfları dışarıda bırakır.
- Her sınıf için ayırt edici kelimeleri raporlar.

Üretilen özellik seçimi raporu:

```text
reports/feature_selection.md
```

### 4. Modelleme

İlk sürümde baseline model olarak **Bag-of-Words + Multinomial Naive Bayes**
kullanılır. Bu yaklaşım, transformer tabanlı modellere geçmeden önce veri
setinin öğrenilebilirliğini ölçmek için güçlü ve açıklanabilir bir başlangıçtır.

Modelleme görevleri:

- `intent_norm`: konuşma amacı tahmini
- `emotion_norm`: duygu tahmini
- `sarcasm_label`: sarkazm tahmini
- `diagnosis_stage_norm`: tanı süreci aşaması tahmini
- `organ_norm`: organ/sistem tahmini

### 5. Değerlendirme

Her görev için aşağıdaki metrikler hesaplanır:

- Accuracy
- Macro F1
- Weighted F1
- Majority baseline karşılaştırması
- Sınıf bazlı precision, recall ve F1

## Çalıştırma

Kurulum:

```bash
pip install -r requirements.txt
```

İleri seviye deneyler için opsiyonel paketler:

```bash
pip install -r requirements-optional.txt
```

Veri temizleme:

```bash
python -m src.data_prep
```

Baseline modelleri eğitme:

```bash
python -m src.train_baselines
```

Streamlit arayüzünü açma:

```bash
python -m streamlit run streamlit_app.py
```

Tek cümle tahmini:

```bash
python -m src.predict --task intent_norm --text "Hastanın MR sonucunda lezyon görüldü."
```

## Çıktılar

Scriptler çalıştığında aşağıdaki dosyalar üretilir:

```text
data/processed/house_md_clean.csv
reports/dataset_summary.md
reports/label_distribution.csv
reports/feature_selection.md
reports/baseline_metrics.json
reports/baseline_metrics.md
reports/prediction_samples.csv
models/*.json
```

## Sunum Planı

1. Veri setinin tanıtılması
2. Problem tanımı ve araştırma soruları
3. Veri temizleme adımları
4. Özellik çıkarımı ve özellik seçimi
5. Baseline model mimarisi
6. Model sonuçları ve hata analizi
7. Geliştirme önerileri: TF-IDF, Logistic Regression, BERTurk, NER

## Geliştirme Fikirleri

- TF-IDF + Logistic Regression veya Linear SVM modeli eklemek
- BERTurk ile metin sınıflandırma yapmak
- `medical_entities` alanını kullanarak medikal varlık tanıma modeli kurmak
- Konuşmacı bazlı duygu ve sarkazm analizi yapmak
- Sezon/bölüm bazlı tanı süreci akışını görselleştirmek
