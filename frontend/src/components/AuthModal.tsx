"use client";

import React, { useState } from "react";
import { AuthResponse } from "@/lib/api";
import { authApi } from "@/lib/api";
import { useGoogleLogin } from "@react-oauth/google";
import { toast } from "sonner";

import GoogleLoginButton from "@/components/auth/GoogleLoginButton";
import PhoneLoginForm from "@/components/auth/PhoneLoginForm";
import PasswordLoginForm from "@/components/auth/PasswordLoginForm";

export const AuthModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (response: AuthResponse) => void;
}> = ({ isOpen, onClose, onSuccess }) => {
  const [authMode, setAuthMode] = useState<"selection" | "phone" | "password">("selection");
  const [googleLoading, setGoogleLoading] = useState(false);

  const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  const triggerGoogleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setGoogleLoading(true);
      try {
        const response = await authApi.googleLogin(tokenResponse.access_token);
        onSuccess(response);
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Google Login failed";
        toast.error(`Đăng nhập Google thất bại: ${message}`);
      } finally {
        setGoogleLoading(false);
      }
    },
    onError: () => toast.error("Đăng nhập Google thất bại. Vui lòng thử lại."),
  });

  const handleGoogleClick = () => {
    if (!GOOGLE_CLIENT_ID) {
      toast.error("Chưa cấu hình Google Client ID trong file .env");
      return;
    }
    triggerGoogleLogin();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop with blur */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-300"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md bg-white/90 backdrop-blur-xl border border-white/20 rounded-3xl shadow-2xl shadow-violet-500/20 overflow-hidden animate-in zoom-in-95 duration-300">
        {/* Gradient Header */}
        <div className="bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-600 px-8 py-10 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-32 h-32 bg-white/10 rounded-full -translate-x-1/2 -translate-y-1/2 blur-2xl"></div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-400/20 rounded-full translate-x-1/2 -translate-y-1/2 blur-2xl"></div>
          <div className="absolute bottom-0 left-1/2 w-24 h-24 bg-violet-400/20 rounded-full -translate-x-1/2 translate-y-1/2 blur-2xl"></div>

          <div className="relative z-10">
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">AI</span>
              </div>
              <h2 className="text-3xl font-bold text-white tracking-tight">StockAI</h2>
            </div>
            <p className="text-violet-100 text-sm font-medium">
              Trợ lý AI Chứng khoán thông minh
            </p>
          </div>
        </div>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center bg-white/20 hover:bg-white/30 rounded-full text-white/80 hover:text-white transition-all duration-300 backdrop-blur-sm"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Content */}
        <div className="p-8">
          {authMode === "selection" && (
            <div className="text-center space-y-6">
              <p className="text-slate-600">
                Chọn phương thức đăng nhập để tiếp tục
              </p>
              <div className="space-y-4">
                <GoogleLoginButton
                  onClick={handleGoogleClick}
                  isLoading={googleLoading}
                />

                <div className="relative flex items-center py-2">
                  <div className="flex-grow border-t border-slate-200"></div>
                  <span className="flex-shrink mx-4 text-slate-400 text-xs font-medium uppercase tracking-wider">Hoặc</span>
                  <div className="flex-grow border-t border-slate-200"></div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setAuthMode("phone")}
                    className="flex flex-col items-center gap-2 p-4 rounded-2xl border border-slate-200 hover:border-violet-500 hover:bg-violet-50/50 transition-all group"
                  >
                    <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-violet-100 transition-colors">
                      <svg className="w-5 h-5 text-slate-500 group-hover:text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <span className="text-xs font-semibold text-slate-600 group-hover:text-violet-700">SMS / OTP</span>
                  </button>

                  <button
                    onClick={() => setAuthMode("password")}
                    className="flex flex-col items-center gap-2 p-4 rounded-2xl border border-slate-200 hover:border-cyan-500 hover:bg-cyan-50/50 transition-all group"
                  >
                    <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-cyan-100 transition-colors">
                      <svg className="w-5 h-5 text-slate-500 group-hover:text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <span className="text-xs font-semibold text-slate-600 group-hover:text-cyan-700">Mật khẩu</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {authMode === "phone" && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <PhoneLoginForm
                onSuccess={onSuccess}
                onSwitchToLogin={() => setAuthMode("password")}
              />
              <button
                onClick={() => setAuthMode("selection")}
                className="w-full mt-4 text-xs text-slate-400 hover:text-slate-600 transition-colors"
              >
                ← Quay lại lựa chọn
              </button>
            </div>
          )}

          {authMode === "password" && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              <PasswordLoginForm
                onSuccess={onSuccess}
                onSwitchToPhone={() => setAuthMode("phone")}
              />
              <button
                onClick={() => setAuthMode("selection")}
                className="w-full mt-4 text-xs text-slate-400 hover:text-slate-600 transition-colors"
              >
                ← Quay lại lựa chọn
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-50/50 px-8 py-4 text-center text-xs text-slate-500">
          Bằng cách đăng nhập, bạn đồng ý với{" "}
          <a href="#" className="text-violet-600 hover:text-violet-700 font-medium hover:underline">
            Điều khoản
          </a>
          {" "}và{" "}
          <a href="#" className="text-cyan-600 hover:text-cyan-700 font-medium hover:underline">
            Chính sách bảo mật
          </a>
        </div>
      </div>
    </div>
  );
};
