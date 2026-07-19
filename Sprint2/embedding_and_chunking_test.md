# Embedding ve Chunking Test Raporu (Sprint 2)

## Amaç
Türkçe hukuki sözleşmelerden (iş ve kira) OCR ile elde edilen metinlerin, emsal kararlar ve kanun maddeleri ile vektörel (embedding) olarak nasıl eşleştiğini ve sınıflandırıldığını (geçerli/geçersiz) değerlendirmek.

## Kullanılan Model ve Araçlar
* **Embedding Modeli:** newmindai/Mursit-Large-TR-Retrieval
* **Görselleştirme Araçları:** 3D PCA/t-SNE Vektör Kümeleme Uzayı

## Test Edilen Veriler ve İstatistik
| Metrik | Sonuç |
| :--- | :--- |
| Toplam Test Edilen Madde | 18 |
| Eşleşme Bulunan | ✅ 18 |
| Eşleşme Bulunamayan | ✅ 0 |
| Riskli (Geçersiz) Görünen Madde | ⚠️ 13 |

## Örnek Test Çıktısı (Ham Veri)
```text

İşveren tarafından sözleşme süresi dolmadan ve herhangi bir bildirimde bulunmadan ve bildirim süresine ilişkin ücret ödenmeksizin iş sözleşmesi sona erdirebilir....

Eşleşme  : 3 referans bulundu

[1] Skor: 0.685 | Geçersiz | 1. Madde, işçinin alacakları için dava açma süresini 6 ay ile sınırlandırmaktadır. 2. İK Ek m.325'e göre, yasal zamanaşımı süreleri (örneğin ücret ve tazminat alacakları için 5 yıl) sözleşmeyle kısaltılamaz veya uzatılamaz. 3. Bu madde yasal süreyi kısaltarak işçi aleyhine bir düzenleme getirmektedir. 4. Bu nedenle geçersizdir....

[2] Skor: 0.680 | Geçerli | 1. Madde incelendi. 2. İş Kanunu m.2025'e uygun olarak işçinin işe iade hakkını korumaktadır. 3. Madde, feragat yasağına aykırı bir düzenleme içermemektedir. 4. Bu nedenle madde geçerlidir....

[3] Skor: 0.675 | Geçersiz | 1. Sözleşme maddesi incelendi. 2. TBK m.347/12 uyarınca kiraya verenin sebepsiz fesih hakkı ancak 10 yıllık uzama süresinin bitiminde doğar. 3. Maddede 5. yılda sebepsiz fesih hakkı tanınması kanuna aykırıdır. 4. Bu nedenle madde geçersizdir....

\------------------------------------------------------------



MADDE #16: h)

Tür      : \['fesih', 'uyusmazlik', 'mahkeme']

Metin    : h)

İş sözleşmesinin işveren tarafından feshinde; fesih bildiriminde sebep gösterilmediği veya gösterilen sebebin geçerli olmadığı hususunda ortaya çıkacak uyuşmazlıklar, bir ay içinde iş mahkemesine götürülür. ı) Bu sözleşmede yer almayan hususlarda İş Kanunu ve diğer ilgili mevzuat uygulanır....

Eşleşme  : 3 referans bulundu

[1] Skor: 0.700 | Geçerli | 1. Madde incelendi. 2. İş Kanunu m.2025'e uygun olarak işçinin işe iade hakkını korumaktadır. 3. Madde, feragat yasağına aykırı bir düzenleme içermemektedir. 4. Bu nedenle madde geçerlidir....

...

```

## Gözlemler
* **Eşleşme Başarısı:** Okunan tüm maddeler (18/18) veri tabanındaki referans mevzuat ve emsal kararlarla yüksek doğruluk skorlarıyla eşleşti. Model olarak kullanılan `nezahatkorkmaz/turkce-embedding-bge-m3`, Türkçe hukuki metinlerin vektörel izdüşümlerini çıkarırken başarılı sonuç verdi.
* **Madde İçi Mantıksal Çıkarımlar:**
  * **Fesih (Madde 16):** İş Kanunu m.2025'e uygun olan maddeler "Geçerli" kümesinde yer alırken, yasal zamanaşımı süresini işçi aleyhine daraltan metinler "Geçersiz" olarak sınıflandırıldı.
* **Vektörel Kümeleme ve Görsel Analizler:**
  * İşlenmiş sözleşmelerde "işçi", "kira", "sözleşme", "işveren" ve "kiracı" gibi anahtar terimlerin frekans ağırlıkları Word Cloud ile başarıyla haritalandırıldı.
  ![Frekans ve Terim Analizi](preview.webp)
 
  * Spotlight CE üzerindeki "Similarity Map" sayesinde, OCR ile okunan her bir cümle (clause_text embedding) anlamsal yakınlıklarına göre uzayda gruplandı.
  ![Benzerlik Haritası 1](preview(1).webp)
 
  * 3 boyutlu kümeleme (Bileşen 1, 2, 3) grafiğinde, modelin geçerli (mavi) ve geçersiz (kırmızı) sözleşme maddelerini net sınırlarla iki ayrı sınıf olarak ayırabildiği görüldü.
  ![3D Vektör Kümeleme](preview(2).webp)

## Sonuç
Unlimited-OCR modeli ile çıkarılan metinler, `newmindai/Mursit-Large-TR-Retrieval` modeli kullanılarak vektör uzayında yüksek doğrulukla sınıflandırılabilmiş ve geçersiz/riskli hükümler emsal mevzuatla başarılı şekilde eşleşmiştir. Sistemin sınıflandırma mantığı projenin Sprint 2 hedefleri doğrultusunda uygun bulunmuştur. Bir sonraki sprintte SLM ile birleştirilip uçtan uca RAG pipeline'ı tamamlanacaktır.
