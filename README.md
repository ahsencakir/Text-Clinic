# House MD: Türkçe Medikal Diyalog Analizi

Bu proje, House MD dizisinden oluşturulan Türkçe hasta-doktor diyalog veri seti üzerinde gelişmiş doğal dil işleme (NLP) yöntemleri kullanarak medikal konuşma bağlamını analiz etmeyi amaçlar. Proje, klasik makine öğrenmesi algoritmalarından en son teknoloji Derin Öğrenme (Deep Learning) dil modellerine kadar uçtan uca bir makine öğrenmesi ardışık düzeni (pipeline) içerir.

## Proje Konusu

**House MD Türkçe medikal diyaloglarında konuşma amacı, duygu, sarkazm ve medikal varlık analizi**

Ana problem, bir diyalog cümlesinin metnine bakarak o cümlenin hangi iletişim amacını taşıdığını, hangi duygu tonuna sahip olduğunu ve sarkazm içerip içermediğini tahmin etmektir. Projeyi güçlendirmek için organ/sistem ve tanı süreci aşaması da yan sınıflandırma görevleri olarak ele alınırken, Derin Öğrenme (NER) modelleri ile metin içerisindeki medikal varlıklar (Hastalık, İlaç, Semptom vb.) tespit edilmektedir.

## Veri Seti

Ham veri dosyası `data/house_md_dataset.csv` yolunda bulunmaktadır.

Veri seti temel olarak aşağıdaki özelliklerden oluşur:
- `season`, `episode`, `speaker` (Konuşmacı ve bağlam bilgileri)
- `Symptom`, `Test`, `Drug`, `Procedure` (Bulunan medikal varlıklar)
- `Intent`, `diagnosis_stage`, `Sarcasm`, `Emotion`, `Organ` (Sınıflandırma hedefleri)
- `text` (İncelenecek replik metni)
- `medical_entities` (JSON formatında çıkarılmış medikal varlık etiketleri)

## Yöntem ve Mimariler

Proje üç ana aşamadan oluşur:

### 1. Veri Hazırlama (`src/data_prep.py`)
- Veri seti temizlenir, boş veya geçersiz etiketler ayıklanır.
- `medical_entities` json kolonundan anlamlı özellikler (entity count) çıkarılır.
- İşlenmiş ve temizlenmiş veri seti `data/house_md_clean.csv` olarak kaydedilir.

### 2. Klasik Makine Öğrenmesi (`src/train_baselines.py`)
Tüm NLP görevleri (Intent, Emotion, Sarcasm, Diagnosis Stage, Organ) için Scikit-Learn kullanılarak güçlü bir `Pipeline` kurulmuştur:
- **Metin Temsili:** Özel Türkçe tokenizasyon + `TfidfVectorizer` (TF-IDF).
- **Ek Özellikler (Feature Engineering):** Konuşmacı kimliği (`speaker`) One-Hot Encoding ile, medikal varlık sayıları ise numerik olarak Modele eklenir.
- **Sınıflandırma Modeli:** Dengesiz sınıflar için ağırlıklandırılmış `LogisticRegression` modeli kullanılır.
- **Çıktılar:** Tüm modeller `.joblib` formatında `models/` klasörüne kaydedilir.

### 3. Derin Öğrenme (HuggingFace Transformers)
Projede klasik NLP yaklaşımlarının yanı sıra modern Transformer tabanlı modeller de bulunur:
- **BERTurk Sınıflandırması:** Türkçe BERT modeli (`dbmdz/bert-base-turkish-cased`) kullanılarak metin sınıflandırma (örn: Konuşma amacı tahmini) için fine-tuning (ince ayar) yapılır.
- **Medikal NER (Varlık İsmi Tanıma):** Replikler içindeki özel medikal kelimeleri (Semptom, İlaç vb.) Token Classification (BIO formatında) yöntemiyle tespit eden özel bir NER modeli eğitilir.

## Kurulum ve Çalıştırma

Gerekli olan tüm kütüphaneler (Scikit-Learn, PyTorch, Transformers, Streamlit) tek bir dosyada birleştirilmiştir.

**Bağımlılıkları yüklemek için:**
```bash
pip install -r requirements.txt
```

**Veriyi temizlemek ve hazırlamak için:**
```bash
python -m src.data_prep
```

**Modelleri Eğitmek İçin:**
Sadece klasik modelleri (Scikit-Learn) eğitmek için:
```bash
python -m src.train_baselines
```

Klasik modellerin yanı sıra Derin Öğrenme (BERT ve NER) modellerini de eğitmek için özel bayrakları kullanabilirsiniz:
```bash
python -m src.train_baselines --bert --ner
```

**Streamlit Web Arayüzünü Başlatmak İçin:**
Eğittiğiniz tüm modelleri test edebileceğiniz, sonuçları ve metrikleri görselleştiren web uygulamasını başlatın:
```bash
python -m streamlit run src/streamlit.py
```

**Komut Satırından Hızlı Tahmin (Predict):**
```bash
python -m src.predict --task intent_norm --text "Hastaya acilen antibiyotik başlayın." --speaker House
```

## Streamlit Arayüzü

Geliştirilen Streamlit arayüzü 3 ana sekmeden oluşur:
1. **Diyalog Tahmini (Klasik Model):** Eğittiğiniz TF-IDF + Logistic Regression `.joblib` modellerini kullanarak canlı olarak cümlelerin niyetini, duygusunu veya sarkazm içerip içermediğini tahmin edebilirsiniz.
2. **Tüm Model Metrikleri:** Scikit-Learn klasik modelleri ve Derin Öğrenme modellerinin (HuggingFace) `Accuracy`, `Macro F1` ve `Loss` metriklerini karşılaştırmalı tablolar halinde incelersiniz.
3. **Derin Öğrenme (BERT & NER):** Fine-tune edilmiş BERT modeli ile cümle analizi yapabilir ve eğitilmiş NER modeliyle cümlenin içindeki medikal terimleri (Token Classification) otomatik olarak buldurabilirsiniz.

## Üretilen (Çıktı) Dosyalar

Scriptleri çalıştırdığınızda aşağıdaki klasörler ve dosyalar otomatik olarak oluşturulur:
- `data/house_md_clean.csv`: Temizlenmiş veri.
- `reports/`: Veri seti özetleri, özellik seçimi raporları, klasik ve DL modellerin performans metriklerini içeren JSON ve CSV dosyaları.
- `models/`: Tüm eğitim ağırlıkları (`.joblib` dosyaları ve PyTorch/Transformers `bert_model` & `ner_model` dizinleri).