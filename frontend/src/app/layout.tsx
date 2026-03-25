import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { AuthProvider } from "@/context/AuthContext";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
});

export const metadata: Metadata = {
  title: "StockAI Predictor | Phân tích thị trường bằng AI",
  description: "Nền tảng trí tuệ nhân tạo thế hệ mới chuyên phân tích dữ liệu, dự đoán xu hướng thị trường chứng khoán Việt Nam.",
  keywords: ["dự đoán chứng khoán", "AI", "tài chính", "phân tích thị trường", "giao dịch", "chứng khoán VN"],
  authors: [{ name: "StockAI Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="dark" suppressHydrationWarning={true}>
      <body suppressHydrationWarning={true} className={`${inter.className} antialiased min-h-screen bg-slate-950 text-slate-50 flex flex-col`}>
        <AuthProvider>
          <Navbar />

          {/* Main Content Container */}
          <main className="flex-1 mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-8 flex flex-col">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
