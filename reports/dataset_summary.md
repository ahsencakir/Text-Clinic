# Veri Seti Ozeti

- Satir sayisi: 7281
- Kolon sayisi: 28
- Ortalama metin uzunlugu: 65.89 karakter
- Medikal varlik iceren satir sayisi: 6535

## Temel Kolonlar

season, episode, speaker, Symptom, Test, Drug, Procedure, Intent, diagnosis_stage, Sarcasm, Emotion, Organ, correct_prediction, model_prediction, text, medical_entities, text_clean, intent_norm, emotion_norm, organ_norm, diagnosis_stage_norm, sarcasm_label, has_symptom, has_test, has_drug, has_procedure, entity_count, entity_types

## Hedef Etiket Dagilimlari

### Konusma amaci (intent_norm)
- açıklama: 3477
- hipotez: 912
- soru: 242
- tanı: 203
- unknown: 200
- talimat: 197
- tedavi: 176
- değerlendirme: 128
- gözlem: 119
- öneri: 92
- test: 91
- teşhis: 88
- şaka: 85
- karar: 63
- itiraz: 63

### Duygu (emotion_norm)
- nötr: 3818
- ciddi: 711
- endişe: 317
- alaycı: 275
- panik: 225
- analitik: 225
- kararlı: 150
- emin: 87
- korku: 78
- acil: 76
- otoriter: 68
- düşünceli: 62
- kaygı: 56
- öfke: 53
- empati: 52

### Sarkazm (sarcasm_label)
- not_sarcastic: 6872
- sarcastic: 406
- unknown: 3

### Tani asamasi (diagnosis_stage_norm)
- değerlendirme: 1791
- hipotez: 1272
- test: 952
- tedavi: 602
- unknown: 411
- tanı: 363
- kesin_tanı: 308
- ayırıcı_tanı: 283
- kritik: 121
- araştırma: 60
- acil: 51
- tedavi_planı: 50
- ilk_değerlendirme: 45
- orta evre: 41
- erken evre: 40

### Organ/sistem (organ_norm)
- unknown: 2525
- beyin: 741
- kalp: 504
- akciğer: 358
- kan: 250
- karaciğer: 209
- genel: 152
- böbrek: 133
- mide: 89
- bacak: 78
- bağırsak: 74
- göz: 71
- nötr: 64
- sinir sistemi: 58
- damar: 56
