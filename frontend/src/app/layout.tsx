import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

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
        {/* Sleek Navigation Bar */}
        <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-900/80 backdrop-blur-md">
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              {/* App Tile / Logo Mock */}
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500 font-bold text-slate-950 shadow-lg shadow-emerald-500/20">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                  <path fillRule="evenodd" d="M15.22 6.268a.75.75 0 0 1 .968-.431l5.942 2.28a.75.75 0 0 1 .431.97l-2.28 5.94a.75.75 0 1 1-1.4-.537l1.63-4.251-5.341 5.341a.75.75 0 0 1-1.06 0L9.89 11.36l-4.711 4.71a.75.75 0 0 1-1.06-1.06l5.241-5.241a.75.75 0 0 1 1.06 0l4.22 4.22 4.881-4.881-4.25 1.63a.75.75 0 0 1-.971-.432Z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="text-xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                StockAI Predictor
              </div>
            </div>
            
            {/* User Avatar / Login Mock */}
            <div className="flex items-center gap-4">
              <nav className="hidden md:flex gap-6 mr-4">
                <a href="#" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Bảng điều khiển</a>
                <a href="#" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Thị trường</a>
                <a href="#" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Theo dõi</a>
              </nav>

              <button className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800/50 pl-3 pr-1 py-1 text-sm font-medium transition-all hover:bg-slate-800 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50">
                <span className="text-slate-200">Đăng nhập</span>
                {/* Mock Avatar */}
                <div className="h-7 w-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs text-white font-bold shadow-sm">
                  VA
                </div>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content Container */}
        <main className="flex-1 mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-8 flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
