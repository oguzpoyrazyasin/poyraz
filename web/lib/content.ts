export type Activity = {
  key: string;
  title: string;
  ages: number[];
  category: string;
  type: "Oyun" | "Video" | "Aktivite";
  minutes: number;
  description: string;
  parentTip: string;
};

export const activities: Activity[] = [
  { key:"color-hunt", title:"Renk Avı", ages:[2,3], category:"Bilişsel", type:"Oyun", minutes:7, description:"Evdeki nesneleri renklere göre bulup eşleştirme.", parentTip:"Üç renkle başlayın; doğru eşleşmede nesnenin adını birlikte söyleyin." },
  { key:"sound-copy", title:"Sesleri Taklit Edelim", ages:[2,3], category:"Dil & İletişim", type:"Video", minutes:6, description:"Hayvan ve çevre sesleriyle dinleme ve tekrar etme.", parentTip:"Her sesten sonra durup çocuğun tekrar etmesini bekleyin." },
  { key:"shape-hunt", title:"Şekil Avı", ages:[3,4], category:"Erken Matematik", type:"Oyun", minutes:8, description:"Daire, kare ve üçgeni günlük nesnelerle eşleştirme.", parentTip:"Ekrandaki şeklin evde bir örneğini bulmasını isteyin." },
  { key:"story-next", title:"Hikâyeyi Tamamla", ages:[3,4,5], category:"Dil & İletişim", type:"Video", minutes:8, description:"Kısa hikâyelerde sonraki olayı tahmin etme.", parentTip:"Sahneyi durdurup “Sence sonra ne olacak?” diye sorun." },
  { key:"count-ten", title:"1'den 10'a Say", ages:[4,5], category:"Erken Matematik", type:"Oyun", minutes:9, description:"Nesne sayma, sayı sembolü ve miktar eşleştirme.", parentTip:"Sonrasında aynı sayıları oyuncaklarla tekrar edin." },
  { key:"patterns", title:"Desen Kurucu", ages:[4,5,6], category:"Problem Çözme", type:"Oyun", minutes:10, description:"AB, AAB ve ABC örüntülerini keşfetme.", parentTip:"Kapak veya lego parçalarıyla deseni fiziksel olarak kurun." },
  { key:"letter-sound", title:"Harf & Ses", ages:[5,6], category:"Okuryazarlık", type:"Oyun", minutes:9, description:"Harfleri başlangıç sesleriyle eşleştirme.", parentTip:"Harf adından çok sesine odaklanın." },
  { key:"mini-science", title:"Mini Bilim: Neden?", ages:[5,6], category:"Merak & Bilim", type:"Video", minutes:10, description:"Basit doğa olaylarını tahmin ve gözlemle keşfetme.", parentTip:"İzlemeden önce tahmin isteyin, sonra sonucu karşılaştırın." },
  { key:"movement-break", title:"Hareket Molası", ages:[2,3,4,5,6], category:"Kaba Motor", type:"Aktivite", minutes:10, description:"Zıplama, denge ve taklit hareketleriyle ekran dışı mola.", parentTip:"Dijital aktiviteyi mutlaka hareketle dengeleyin." },
  { key:"fine-motor", title:"Kıskaç Görevi", ages:[3,4,5], category:"İnce Motor", type:"Aktivite", minutes:12, description:"Mandallar veya güvenli büyük parçalarla kavrama çalışması.", parentTip:"Küçük parçalarda yetişkin gözetimi şarttır." },
  { key:"emotion-match", title:"Duyguyu Bul", ages:[3,4,5,6], category:"Sosyal-Duygusal", type:"Oyun", minutes:8, description:"Yüz ifadelerini temel duygularla eşleştirme.", parentTip:"Günlük hayattan örneklerle duygunun adını birlikte söyleyin." },
  { key:"creative-story", title:"Üç Nesneyle Hikâye", ages:[4,5,6], category:"Yaratıcılık", type:"Aktivite", minutes:15, description:"Seçilen üç nesneyi kullanarak kısa hikâye oluşturma.", parentTip:"Doğru cevap aramayın; çocuğun özgün anlatımını destekleyin." }
];

export const developmentGoals = [
  "Dil & İletişim",
  "Erken Matematik",
  "Problem Çözme",
  "İnce Motor",
  "Kaba Motor",
  "Sosyal-Duygusal",
  "Yaratıcılık",
  "Merak & Bilim"
] as const;
