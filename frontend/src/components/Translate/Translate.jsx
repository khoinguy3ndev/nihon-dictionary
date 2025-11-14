import React, { useState } from "react";
import "./Translate.css";

export default function TextTranslator() {
  const [text, setText] = useState("");
  const [translated, setTranslated] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const translate = async () => {
    if (!text.trim()) {
      setError("Vui lòng nhập văn bản");
      return;
    }

    setLoading(true);
    setTranslated("");
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8888/api/translate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();

      if (data.translated) {
        setTranslated(data.translated);
      } else if (data.error) {
        setError(data.error);
      } else {
        setError("Không dịch được");
      }
    } catch (err) {
      setError("Lỗi kết nối đến server");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(translated);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    setText("");
    setTranslated("");
    setError("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      translate();
    }
  };

  return (
    <div className="translator-container">
      <div className="translator-wrapper">
        {/* Header */}
        <div className="translator-header">
          <div className="translator-icon">
            <span>🌐</span>
          </div>
          <h1 className="translator-title">
            Dịch đoạn văn
            <span className="sparkle">✨</span>
          </h1>
          <p className="translator-subtitle">
            Nhật → Việt | Nhanh chóng & Chính xác
          </p>
        </div>

        {/* Main Card */}
        <div className="translator-card">
          {/* Language Indicator */}
          <div className="language-header">
            <div className="language-item">
              <span className="flag">🇯🇵</span>
              <span className="language-name">Tiếng Nhật</span>
            </div>
            <span className="arrow">→</span>
            <div className="language-item">
              <span className="language-name">Tiếng Việt</span>
              <span className="flag">🇻🇳</span>
            </div>
          </div>

          {/* Input Section */}
          <div className="input-section">
            <div className="input-header">
              <label className="input-label">
                <span className="dot"></span>
                Văn bản cần dịch
              </label>
              <div className="input-actions">
                <span className="char-count">{text.length} ký tự</span>
                {text && (
                  <button onClick={handleClear} className="clear-btn">
                    🔄 Xóa
                  </button>
                )}
              </div>
            </div>

            <textarea
              rows={6}
              className="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="こんにちは、元気ですか？&#10;&#10;Nhập hoặc dán văn bản tiếng Nhật vào đây..."
            />

            <div className="input-footer">
              <p className="tip-text">
                💡 Mẹo: Nhấn <kbd>Ctrl</kbd> + <kbd>Enter</kbd> để dịch nhanh
              </p>
              <button
                onClick={translate}
                disabled={loading || !text.trim()}
                className="translate-btn"
              >
                {loading ? (
                  <>
                    <span className="spinner">⏳</span>
                    Đang dịch...
                  </>
                ) : (
                  <>
                    Dịch ngay
                    <span>→</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <div className="error-icon">!</div>
              <div>
                <p className="error-title">Có lỗi xảy ra</p>
                <p className="error-text">{error}</p>
              </div>
            </div>
          )}

          {/* Result Section */}
          {translated && (
            <div className="result-section">
              <div className="result-container">
                <div className="result-header">
                  <label className="result-label">
                    <span className="check-icon">✓</span>
                    Kết quả dịch
                  </label>
                  <button onClick={handleCopy} className="copy-btn">
                    {copied ? (
                      <>
                        <span>✓</span>
                        Đã sao chép!
                      </>
                    ) : (
                      <>
                        <span>📋</span>
                        Sao chép
                      </>
                    )}
                  </button>
                </div>
                <div className="result-box">
                  <p className="result-text">{translated}</p>
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && !translated && (
            <div className="loading-section">
              <div className="loading-container">
                <div className="loading-spinner">⏳</div>
                <p className="loading-title">Đang xử lý bản dịch...</p>
                <p className="loading-text">Vui lòng đợi trong giây lát</p>
              </div>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="info-cards">
          <div className="info-card">
            <div className="info-icon">⚡</div>
            <h3 className="info-title">Dịch nhanh</h3>
            <p className="info-text">Kết quả trong vài giây</p>
          </div>

          <div className="info-card">
            <div className="info-icon">🎯</div>
            <h3 className="info-title">Chính xác</h3>
            <p className="info-text">Công nghệ dịch hiện đại</p>
          </div>

          <div className="info-card">
            <div className="info-icon">🔒</div>
            <h3 className="info-title">An toàn</h3>
            <p className="info-text">Bảo mật thông tin</p>
          </div>
        </div>
      </div>
    </div>
  );
}
