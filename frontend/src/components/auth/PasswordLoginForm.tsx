"use client";

import React, { useState } from "react";
import { authApi, AuthResponse } from "@/lib/api";

const PasswordLoginForm: React.FC<{
  onSuccess: (response: AuthResponse) => void;
  onSwitchToPhone: () => void;
}> = ({ onSuccess, onSwitchToPhone }) => {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async () => {
    if (!identifier || !password || (isRegister && !fullName)) {
      setError("Vui lòng điền đầy đủ thông tin");
      return;
    }

    setLoading(true);
    setError("");

    try {
      let response;
      if (isRegister) {
        response = await authApi.register(identifier, password, fullName);
      } else {
        response = await authApi.login(identifier, password);
      }
      onSuccess(response);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Thao tác thất bại";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="text-center">
        <h3 className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-cyan-500 bg-clip-text text-transparent">
          {isRegister ? "Đăng ký tài khoản" : "Đăng nhập với mật khẩu"}
        </h3>
        <p className="text-sm text-slate-500 mt-2">
          {isRegister 
            ? "Tạo tài khoản mới để bắt đầu sử dụng" 
            : "Nhập email hoặc số điện thoại và mật khẩu của bạn"}
        </p>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm animate-in fade-in slide-in-from-top-2 duration-300">
          {error}
        </div>
      )}

      <div className="space-y-5">
        {isRegister && (
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Họ và tên
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Nguyễn Văn A"
              className="w-full px-4 py-3.5 border-2 border-slate-200 rounded-xl focus:border-violet-500 focus:ring-4 focus:ring-violet-500/10 transition-all outline-none text-slate-700 placeholder:text-slate-400"
            />
          </div>
        )}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            {isRegister ? "Email" : "Email hoặc Số điện thoại"}
          </label>
          <input
            type={isRegister ? "email" : "text"}
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder={isRegister ? "email@example.com" : "email@example.com hoặc +84xxxxxxxxx"}
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
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-gradient-to-r from-violet-600 to-cyan-500 text-white py-3.5 rounded-xl hover:shadow-lg hover:shadow-violet-500/30 active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-semibold text-lg"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {isRegister ? "Đang tạo tài khoản..." : "Đang đăng nhập..."}
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              {isRegister ? "Đăng ký" : "Đăng nhập"}{" "}
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </span>
          )}
        </button>
        <div className="text-center space-y-2">
          <p className="text-sm text-slate-500">
            {isRegister ? "Đã có tài khoản?" : "Chưa có tài khoản?"}{" "}
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
              }}
              className="text-violet-600 hover:text-violet-700 font-semibold hover:underline transition-all"
            >
              {isRegister ? "Đăng nhập ngay" : "Đăng ký bằng Email"}
            </button>
          </p>
          {!isRegister && (
            <p className="text-sm text-slate-500">
              Hoặc dùng{" "}
              <button
                onClick={onSwitchToPhone}
                className="text-violet-600 hover:text-violet-700 font-semibold hover:underline transition-all"
              >
                Số điện thoại
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PasswordLoginForm;
