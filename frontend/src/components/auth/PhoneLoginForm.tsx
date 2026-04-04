"use client";

import React, { useState, useEffect } from "react";
import { authApi, AuthResponse } from "@/lib/api";

const PhoneLoginForm: React.FC<{
  onSuccess: (response: AuthResponse) => void;
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
      await authApi.sendPhoneCode(phoneNumber);
      setStep("code");
      setTimer(60);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Gửi mã thất bại";
      setError(message);
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
      onSuccess(response);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Mã xác thực không hợp lệ";
      setError(message);
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

export default PhoneLoginForm;
