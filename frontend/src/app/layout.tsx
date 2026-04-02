import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { AuthProvider } from "@/context/AuthContext";
import { QueryProvider } from "@/services/QueryProvider";
import { Toaster } from "sonner";

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
      <body suppressHydrationWarning={true} className={`${inter.className} antialiased min-h-screen bg-[#020617] text-slate-100 flex flex-col`}>
        <QueryProvider>
          <AuthProvider>
            <Navbar />
            <Toaster position="top-right" richColors closeButton />

            {/* Main Content Container with safe height */}
            <main className="flex-1 w-full px-4 sm:px-6 lg:px-10 py-4 flex flex-col min-h-0">
              {children}
            </main>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
