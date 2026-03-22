export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface PredictRequest {
  ticker: string;
}

export interface PredictResponse {
  ticker: string;
  prediction: string; // VD: "Tăng giá", "Giảm giá", "Đi ngang"
  probability: number; // VD: 0.92 cho 92% độ tin cậy
}

/**
 * Gửi yêu cầu dự đoán cổ phiếu tới backend.
 * @param ticker Mã chứng khoán (VD: "FPT", "VCB")
 * @returns Một promise trả về dữ liệu PredictResponse
 */
export async function predictStock(ticker: string): Promise<PredictResponse> {
  const payload: PredictRequest = { ticker };

  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      // Cố gắng phân tích chi tiết lỗi gửi về từ server
      let errorMessage = "Đã xảy ra lỗi không xác định từ máy chủ.";
      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorMessage;
      } catch {
        // Dự phòng nếu response trả về không phải định dạng JSON
        errorMessage = `Lỗi HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(`Không thể lấy dự đoán cho mã cổ phiếu: ${errorMessage}`);
    }

    const data: PredictResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      throw new Error("Lỗi mạng: Không thể kết nối tới máy chủ backend. Vui lòng kiểm tra lại API.");
    }
    
    // Ném lại lỗi nếu đó đã là các Error được tuỳ chỉnh ở trên, nếu không thì bọc lại
    if (error instanceof Error) {
      throw error;
    }
    
    throw new Error("Đã xảy ra lỗi không xác định trong quá trình gửi yêu cầu dự đoán.");
  }
}
