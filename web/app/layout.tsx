import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Poyraz Kids | 2–6 Yaş Akıllı Gelişim Platformu",
  description:
    "2–6 yaş çocuklar için ebeveyn kontrollü akıllı oyunlar, videolar, gelişim aktiviteleri ve kişiselleştirilmiş planlar."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
