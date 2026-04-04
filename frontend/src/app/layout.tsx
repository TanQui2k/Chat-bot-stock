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

import { ThemeProvider } from "@/context/ThemeContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" suppressHydrationWarning={true}>
      <body suppressHydrationWarning={true} className={`${inter.className} antialiased h-screen overflow-hidden bg-background text-foreground flex flex-col transition-colors duration-300`}>
        <ThemeProvider>
          <QueryProvider>
            <AuthProvider>
              <Navbar />
              <Toaster position="top-right" richColors closeButton />

              {/* Main Content Container - Fixed Height, No Scroll */}
              <main className="flex-1 w-full flex flex-col min-h-0 overflow-hidden">
                {children}
              </main>
            </AuthProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
