"use client";

import React, { useState, useEffect } from "react";
import { authApi, AuthUser } from "@/lib/api";

// Google OAuth button component
const GoogleButton: React.FC<{ 
  onClick: () => void; 
  isLoading: boolean;
}> = ({ onClick, isLoading }) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:border-gray-300 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
    >
      <svg className="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path
          fill="#4285F4"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="#34A853"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="#FBBC05"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        />
        <path
          fill="#EA4335"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        />
      </svg>
      <span className="font-semibold text-slate-700">
        {isLoading ? "Đang đăng nhập..." : "Đăng nhập với Google"}
      </span>
    </button>
  );
};

// Phone login form
const PhoneLoginForm: React.FC<{
  onSuccess: (user: AuthUser) => void;
  onSwitchToLogin: () => void;
}> = ({ onSuccess, onSwitchToLogin }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer]);

  const handleSendCode = async () => {
    if (!phoneNumber) {
      setError("Vui lòng nhập số điện thoại");
      return;
    }

    const phonePattern = /^(\+84|0|84)[0-9]{9,10}$/;
    if (!phonePattern.test(phoneNumber)) {
      setError("Số điện thoại không hợp lệ. Dùng: +84xxxxxxxxx hoặc 0xxxxxxxxx");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await authApi.sendPhoneCode(phoneNumber);
      console.log("Verification code:", response.code); // For demo only!
      setStep("code");
      setTimer(60);
    } catch (err: any) {
      setError(err.message || "Gửi mã thất bại");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!verificationCode) {
      setError("Vui lòng nhập mã xác thực");
      return;
    }

    if (verificationCode.length !== 6) {
      setError("Mã xác thực phải có 6 chữ số");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await authApi.verifyPhoneCode(phoneNumber, verificationCode);
      onSuccess(response.user);
    } catch (err: any) {
      setError(err.message || "Mã xác thực không hợp lệ");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="text-center">
        <h3 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-cyan-500 bg-clip-text text-transparent">
          {step === "phone" ? "Đăng nhập bằng SMS" : "Xác thực SMS"}
        </h3>
        <p className="text-sm text-slate-500 mt-2">
          {step === "phone" 
            ? "Nhập số điện thoại để nhận mã xác thực" 
            : "Nhập mã 6 chữ số đã gửi đến điện thoại của bạn"}
        </p>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm animate-in fade-in slide-in-from-top-2 duration-300">
          {error}
        </div>
      )}

      {step === "phone" ? (
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Số điện thoại
            </label>
            <div className="relative">
              <div className="absolute left-4 top-1/2 -translate-y-1/2">
                <span className="text-slate-400 font-medium">+84</span>
              </div>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="912 345 678"
                className="w-full pl-16 pr-4 py-3.5 border-2 border-slate-200 rounded-xl focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition-all outline-none text-slate-700 placeholder:text-slate-400"
                maxLength={10}
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
            </div>
          </div>
          <button
            onClick={handleSendCode}
            disabled={loading}
            className="w-full bg-gradient-to-r from-violet-600 to-cyan-500 text-white py-3.5 rounded-xl hover:shadow-lg hover:shadow-violet-500/30 active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-semibold text-lg"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Đang gửi mã...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                Gửi mã xác thực <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
              </span>
            )}
          </button>
          <p className="text-center text-sm text-slate-500">
            Hoặc{" "}
            <button
              onClick={onSwitchToLogin}
              className="text-violet-600 hover:text-violet-700 font-semibold hover:underline transition-all"
            >
              đăng nhập bằng mật khẩu
            </button>
          </p>
        </div>
      ) : (
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Mã xác thực
            </label>
            <input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              placeholder="Nhập mã 6 chữ số"
              className="w-full px-4 py-3.5 border-2 border-slate-200 rounded-xl text-center text-2xl tracking-widest focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition-all outline-none text-slate-700 placeholder:text-slate-300"
              maxLength={6}
            />
          </div>
          <button
            onClick={handleVerifyCode}
            disabled={loading}
            className="w-full bg-gradient-to-r from-violet-600 to-cyan-500 text-white py-3.5 rounded-xl hover:shadow-lg hover:shadow-violet-500/30 active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-semibold text-lg"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Đang xác thực...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                Xác thực <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              </span>
            )}
          </button>
          <p className="text-center text-sm text-slate-500">
            {timer > 0 ? (
              <span className="font-semibold text-cyan-600 bg-cyan-50 px-3 py-1 rounded-full">
                Gửi lại mã sau {timer}s
              </span>
            ) : (
              <button
                onClick={handleSendCode}
                className="text-violet-600 hover:text-violet-700 font-semibold hover:underline transition-all"
              >
                Gửi lại mã
              </button>
            )}
          </p>
          <p className="text-center text-sm text-slate-500">
            Hoặc{" "}
            <button
              onClick={() => {
                setStep("phone");
                setVerificationCode("");
              }}
              className="text-violet-600 hover:text-violet-700 font-semibold hover:underline transition-all"
            >
              Quay lại
            </button>
          </p>
        </div>
      )}
    </div>
  );
};

// Password login form
const PasswordLoginForm: React.FC<{
  onSuccess: (user: AuthUser) => void;
  onSwitchToPhone: () => void;
}> = ({ onSuccess, onSwitchToPhone }) => {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    if (!identifier || !password) {
      setError("Vui lòng nhập email/phone và mật khẩu");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await authApi.login(identifier, password);
      onSuccess(response.user);
    } catch (err: any) {
      setError(err.message || "Đăng nhập thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="text-center">
        <h3 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-cyan-500 bg-clip-text text-transparent">
          Đăng nhập với mật khẩu
        </h3>
        <p className="text-sm text-slate-500 mt-2">
          Nhập email hoặc số điện thoại và mật khẩu của bạn
        </p>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm animate-in fade-in slide-in-from-top-2 duration-300">
          {error}
        </div>
      )}

      <div className="space-y-5">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Email hoặc Số điện thoại
          </label>
          <input
            type="text"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder="email@example.com hoặc +84xxxxxxxxx"
            className="w-full px-4 py-3.5 border-2 border-slate-200 rounded-xl focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition-all outline-none text-slate-700 placeholder:text-slate-400"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Mật khẩu
          </label>
          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3.5 pr-12 border-2 border-slate-200 rounded-xl focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition-all outline-none text-slate-700 placeholder:text-slate-400"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-violet-600 transition-colors"
            >
              {showPassword ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              )}
            </button>
          </div>
        </div>
        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full bg-gradient-to-r from-violet-600 to-cyan-500 text-white py-3.5 rounded-xl hover:shadow-lg hover:shadow-violet-500/30 active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-semibold text-lg"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Đang đăng nhập...
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              Đăng nhập <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </span>
          )}
        </button>
        <p className="text-center text-sm text-slate-500">
          Chưa có tài khoản?{" "}
          <button
            onClick={onSwitchToPhone}
            className="text-violet-600 hover:text-violet-700 font-semibold hover:underline transition-all"
          >
            Đăng ký bằng SMS
          </button>
        </p>
      </div>
    </div>
  );
};

// Main Auth Modal Component - Simple Google Login Only
export const AuthModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: AuthUser) => void;
}> = ({ isOpen, onClose, onSuccess }) => {
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

        {/* Content - Google Login Only */}
        <div className="p-8 text-center">
          <p className="text-slate-600 mb-6">
            Chọn phương thức đăng nhập để tiếp tục
          </p>
          <div className="space-y-4">
            <GoogleButton
              onClick={() => {
                // Trigger Google OAuth flow
                alert("Google OAuth - Cần cấu hình Google Cloud Console");
              }}
              isLoading={false}
            />
          </div>
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
