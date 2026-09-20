package com.poyrazkids.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog

data class LearningItem(
    val title: String,
    val ageGroup: String,
    val area: String,
    val type: String,
    val description: String,
    val parentTip: String,
    val url: String
)

private val learningItems = listOf(
    LearningItem("Renkleri Bul", "2–3", "Bilişsel", "Oyun",
        "Çocuğun evde aynı renkteki nesneleri bulmasını sağlayan kısa eşleştirme oyunu.",
        "3 renk seçin. Her doğru eşleşmede nesnenin adını birlikte söyleyin.",
        "https://pbskids.org/games/"),
    LearningItem("Sesleri Taklit Edelim", "2–3", "Dil", "Video",
        "Hayvan ve çevre seslerini dinleyip tekrar etmeye dayalı dil gelişimi etkinliği.",
        "Videoyu kısa tutun; her sesten sonra ekranı durdurup çocuğun tekrar etmesini bekleyin.",
        "https://www.sesamestreet.org/"),
    LearningItem("Şekil Avı", "3–4", "Erken Matematik", "Oyun",
        "Daire, kare ve üçgenleri günlük nesnelerle ilişkilendiren şekil tanıma çalışması.",
        "Ekrandaki şekli evdeki gerçek bir nesneyle eşleştirmesini isteyin.",
        "https://www.starfall.com/"),
    LearningItem("Hikâyeyi Tamamla", "3–4", "Dil", "Video",
        "Kısa hikâyeyi izlerken sonraki olayı tahmin etmeyi teşvik eden ortak izleme etkinliği.",
        "Her sahnede 'Sence sonra ne olacak?' diye sorun.",
        "https://pbskids.org/videos/"),
    LearningItem("1'den 10'a Say", "4–5", "Erken Matematik", "Oyun",
        "Nesne sayma, sayı sembolü eşleme ve basit miktar karşılaştırma çalışmaları.",
        "Oyundan sonra aynı sayıları oyuncak veya bloklarla tekrar edin.",
        "https://www.khanacademy.org/kids"),
    LearningItem("Desen Kurucu", "4–5", "Problem Çözme", "Oyun",
        "Renk ve şekillerle AB, AAB ve ABC örüntülerini fark etmeye yönelik çalışma.",
        "Ekran sonrasında lego veya kapaklarla aynı deseni fiziksel olarak kurun.",
        "https://pbskids.org/games/"),
    LearningItem("Harf ve Ses Eşleştirme", "5–6", "Okuryazarlık", "Oyun",
        "Harf sembollerini başlangıç sesleriyle eşleştiren okul öncesi etkinlik.",
        "Harf adından çok sesine odaklanın ve günlük kelimelerden örnekler bulun.",
        "https://www.starfall.com/"),
    LearningItem("Mini Bilim: Neden?", "5–6", "Merak & Bilim", "Video",
        "Basit doğa ve günlük yaşam sorularını merak, tahmin ve gözlem üzerinden ele alan içerik.",
        "İzlemeden önce tahmin isteyin; izledikten sonra tahmin ile sonucu karşılaştırın.",
        "https://pbskids.org/videos/"),
    LearningItem("Hareket Molası", "2–6", "Kaba Motor", "Aktivite",
        "Ekran süresini hareketle dengelemek için zıplama, denge ve taklit görevleri.",
        "5–10 dakika ekrandan sonra fiziksel hareket molası verin.",
        "https://www.sesamestreet.org/")
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    PoyrazKidsApp()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PoyrazKidsApp() {
    val context = LocalContext.current
    var selectedAge by remember { mutableStateOf("Tümü") }
    var pendingItem by remember { mutableStateOf<LearningItem?>(null) }
    var parentMode by remember { mutableStateOf(false) }

    val ages = listOf("Tümü", "2–3", "3–4", "4–5", "5–6")
    val filtered = learningItems.filter {
        selectedAge == "Tümü" || it.ageGroup == selectedAge || it.ageGroup == "2–6"
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.25f))
    ) {
        LazyColumn(
            contentPadding = PaddingValues(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            item {
                Text("Poyraz Kids", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Black)
                Text(
                    "2–6 yaş için akıllı oyunlar, videolar ve ebeveyn destekli gelişim aktiviteleri",
                    style = MaterialTheme.typography.bodyLarge
                )
                Spacer(Modifier.height(12.dp))
                Text(
                    if (parentMode) "Ebeveyn modu açık" else "Dış içerikler ebeveyn onayıyla açılır",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            item {
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    ages.forEach { age ->
                        FilterChip(
                            selected = selectedAge == age,
                            onClick = { selectedAge = age },
                            label = { Text(age) }
                        )
                    }
                }
            }

            item { DevelopmentSummary() }

            items(filtered) { learningItem ->
                LearningCard(
                    item = learningItem,
                    onOpen = {
                        if (parentMode) {
                            context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(learningItem.url)))
                        } else {
                            pendingItem = learningItem
                        }
                    }
                )
            }

            item {
                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                    Column(Modifier.padding(16.dp)) {
                        Text("Ebeveyn Notu", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                        Text(
                            "Bu uygulama tıbbi veya gelişimsel değerlendirme aracı değildir. " +
                                "Ekran içeriğini yetişkin eşliğinde, kısa oturumlarla ve fiziksel oyunla dengeli kullanın."
                        )
                        Spacer(Modifier.height(8.dp))
                        OutlinedButton(onClick = { pendingItem = learningItems.first() }) {
                            Text("Ebeveyn modunu aç")
                        }
                    }
                }
            }
        }

        pendingItem?.let { learningItem ->
            ParentGateDialog(
                itemTitle = learningItem.title,
                onDismiss = { pendingItem = null },
                onSuccess = {
                    parentMode = true
                    pendingItem = null
                    context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(learningItem.url)))
                }
            )
        }
    }
}

@Composable
private fun DevelopmentSummary() {
    Card(
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
    ) {
        Column(Modifier.padding(18.dp)) {
            Text("Bugünün dengesi", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            Text("• 10 dk akıllı oyun")
            Text("• 10 dk birlikte video / hikâye")
            Text("• 20+ dk fiziksel oyun")
            Text("• Gün içinde bol sohbet ve kitap")
        }
    }
}

@Composable
private fun LearningCard(item: LearningItem, onOpen: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(Modifier.padding(18.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(Modifier.weight(1f)) {
                    Text(item.title, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    Text(
                        "${item.ageGroup} • ${item.area} • ${item.type}",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
            Spacer(Modifier.height(10.dp))
            Text(item.description)
            Spacer(Modifier.height(10.dp))
            Text(
                "Ebeveyn ipucu: ${item.parentTip}",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(Modifier.height(14.dp))
            Button(onClick = onOpen) {
                Text(if (item.type == "Video") "İçeriği aç" else "Etkinliği aç")
            }
        }
    }
}

@Composable
private fun ParentGateDialog(
    itemTitle: String,
    onDismiss: () -> Unit,
    onSuccess: () -> Unit
) {
    var answer by remember { mutableStateOf("") }
    var error by remember { mutableStateOf(false) }
    var a by remember { mutableIntStateOf(7) }
    var b by remember { mutableIntStateOf(5) }

    Dialog(onDismissRequest = onDismiss) {
        Card(shape = RoundedCornerShape(24.dp)) {
            Column(Modifier.padding(22.dp)) {
                Text("Ebeveyn Onayı", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text(
                    "“$itemTitle” harici bir eğitim sitesinde açılacak. " +
                        "Devam etmek için yetişkin kontrolünü tamamlayın."
                )
                Spacer(Modifier.height(14.dp))
                Text("$a + $b = ?", fontWeight = FontWeight.Bold)
                OutlinedTextField(
                    value = answer,
                    onValueChange = {
                        answer = it.filter(Char::isDigit).take(3)
                        error = false
                    },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Cevap") },
                    isError = error,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )
                if (error) {
                    Text(
                        "Cevap doğru değil.",
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
                Spacer(Modifier.height(14.dp))
                Button(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = {
                        if (answer.toIntOrNull() == a + b) {
                            onSuccess()
                        } else {
                            error = true
                            a = 6
                            b = 8
                            answer = ""
                        }
                    }
                ) {
                    Text("Ebeveyn olarak devam et")
                }
                TextButton(modifier = Modifier.fillMaxWidth(), onClick = onDismiss) {
                    Text("Vazgeç")
                }
            }
        }
    }
}
