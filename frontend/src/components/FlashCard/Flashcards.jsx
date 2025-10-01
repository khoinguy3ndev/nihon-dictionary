import React, { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8888";

export default function Flashcard() {
  const [flashcards, setFlashcards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [allWords, setAllWords] = useState([]);

  const fetchFlashcards = async () => {
    setLoading(true);
    setErr("");
    try {
      const token = localStorage.getItem("access");
      const res = await fetch(`${API_BASE}/api/flashcards/`, {
        headers: {
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      if (!res.ok) {
        const json = await res.json().catch(() => null);
        throw new Error(json?.detail || `${res.status} ${res.statusText}`);
      }

      const data = await res.json();
      setFlashcards(data);

      const words = [];
      data.forEach((fc) => {
        fc.items.forEach((item) => {
          words.push(item.word);
        });
      });
      setAllWords(words);
    } catch (e) {
      setErr(e.message || "Lỗi khi tải flashcards");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlashcards();
  }, []);

  const handleNext = () => {
    if (currentIndex < allWords.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
    }
  };

  const toggleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const containerStyle = {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px 20px",
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  };

  const cardWrapperStyle = {
    width: "100%",
    maxWidth: "600px",
    margin: "0 auto",
  };

  const cardStyle = {
    background: "white",
    borderRadius: "24px",
    boxShadow: "0 30px 60px rgba(0,0,0,0.3)",
    overflow: "hidden",
    minHeight: "400px",
    position: "relative",
  };

  const headerStyle = {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    padding: "20px 30px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  };

  const titleStyle = {
    fontSize: "24px",
    fontWeight: "bold",
    margin: 0,
  };

  const counterStyle = {
    fontSize: "16px",
    opacity: 0.9,
  };

  const contentStyle = {
    padding: "60px 40px",
    minHeight: "350px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    textAlign: "center",
  };

  const kanjiStyle = {
    fontSize: "80px",
    fontWeight: "bold",
    color: "#667eea",
    marginBottom: "20px",
    lineHeight: 1,
  };

  const kanaStyle = {
    fontSize: "32px",
    color: "#764ba2",
    marginBottom: "10px",
  };

  const meaningTitleStyle = {
    fontSize: "14px",
    color: "#667eea",
    fontWeight: "bold",
    textTransform: "uppercase",
    letterSpacing: "1px",
    marginBottom: "12px",
    textAlign: "left",
    width: "100%",
  };

  const meaningTextStyle = {
    fontSize: "20px",
    color: "#333",
    marginBottom: "30px",
    lineHeight: 1.6,
    textAlign: "left",
    width: "100%",
  };

  const exampleBoxStyle = {
    background: "#f8f9ff",
    borderLeft: "4px solid #667eea",
    borderRadius: "8px",
    padding: "16px",
    marginBottom: "12px",
    width: "100%",
    textAlign: "left",
  };

  const exampleJpStyle = {
    fontSize: "16px",
    color: "#667eea",
    fontWeight: "600",
    marginBottom: "8px",
  };

  const exampleEnStyle = {
    fontSize: "14px",
    color: "#666",
    lineHeight: 1.5,
  };

  const navStyle = {
    display: "flex",
    gap: "12px",
    justifyContent: "center",
    padding: "0 30px 30px",
  };

  const buttonStyle = {
    padding: "14px 32px",
    fontSize: "16px",
    fontWeight: "600",
    borderRadius: "12px",
    border: "none",
    cursor: "pointer",
    transition: "all 0.3s ease",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
  };

  const primaryButtonStyle = {
    ...buttonStyle,
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
  };

  const secondaryButtonStyle = {
    ...buttonStyle,
    background: "white",
    color: "#667eea",
    border: "2px solid #667eea",
  };

  const disabledButtonStyle = {
    ...buttonStyle,
    background: "#e0e0e0",
    color: "#999",
    cursor: "not-allowed",
    boxShadow: "none",
  };

  const progressBarStyle = {
    height: "6px",
    background: "#e0e0e0",
    borderRadius: "3px",
    margin: "0 30px 30px",
    overflow: "hidden",
  };

  const progressFillStyle = {
    height: "100%",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    transition: "width 0.3s ease",
    width:
      allWords.length > 0
        ? `${((currentIndex + 1) / allWords.length) * 100}%`
        : "0%",
  };

  const hintStyle = {
    position: "absolute",
    bottom: "20px",
    left: "50%",
    transform: "translateX(-50%)",
    fontSize: "14px",
    color: "#999",
    fontStyle: "italic",
  };

  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={{ textAlign: "center", color: "white" }}>
          <div
            style={{
              width: "50px",
              height: "50px",
              border: "4px solid rgba(255,255,255,0.3)",
              borderTop: "4px solid white",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              margin: "0 auto 20px",
            }}
          ></div>
          <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          <p style={{ fontSize: "18px" }}>Đang tải flashcards...</p>
        </div>
      </div>
    );
  }

  if (err) {
    return (
      <div style={containerStyle}>
        <div
          style={{
            ...cardStyle,
            padding: "40px",
            textAlign: "center",
            maxWidth: "400px",
          }}
        >
          <div style={{ fontSize: "48px", marginBottom: "20px" }}>⚠️</div>
          <p
            style={{ color: "#dc2626", fontSize: "18px", marginBottom: "20px" }}
          >
            {err}
          </p>
          <button onClick={fetchFlashcards} style={primaryButtonStyle}>
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  if (!allWords.length) {
    return (
      <div style={containerStyle}>
        <div
          style={{
            ...cardStyle,
            padding: "60px",
            textAlign: "center",
            maxWidth: "400px",
          }}
        >
          <div style={{ fontSize: "64px", marginBottom: "20px" }}>📚</div>
          <p style={{ color: "#666", fontSize: "20px" }}>
            Chưa có flashcard nào
          </p>
        </div>
      </div>
    );
  }

  const currentWord = allWords[currentIndex];

  return (
    <div style={containerStyle}>
      <div style={cardWrapperStyle}>
        <div style={cardStyle}>
          <div style={headerStyle}>
            <h1 style={titleStyle}>Flashcards</h1>
            <div style={counterStyle}>
              {currentIndex + 1} / {allWords.length}
            </div>
          </div>

          <div style={contentStyle} onClick={toggleFlip}>
            {!isFlipped ? (
              <>
                <div style={kanjiStyle}>
                  {currentWord.kanji ||
                    currentWord.kana ||
                    currentWord.hiragana}
                </div>
                {currentWord.kanji && (
                  <div style={kanaStyle}>
                    {currentWord.kana || currentWord.hiragana}
                  </div>
                )}
                <div style={hintStyle}>Nhấp để xem nghĩa</div>
              </>
            ) : (
              <div
                style={{ width: "100%", maxHeight: "300px", overflowY: "auto" }}
              >
                <div style={{ marginBottom: "30px" }}>
                  <div
                    style={{
                      fontSize: "36px",
                      fontWeight: "bold",
                      color: "#667eea",
                      marginBottom: "8px",
                    }}
                  >
                    {currentWord.kanji ||
                      currentWord.kana ||
                      currentWord.hiragana}
                  </div>
                  {currentWord.kanji && (
                    <div style={{ fontSize: "20px", color: "#764ba2" }}>
                      {currentWord.kana || currentWord.hiragana}
                    </div>
                  )}
                </div>

                <div style={meaningTitleStyle}>Nghĩa</div>
                <div style={meaningTextStyle}>
                  {(currentWord.meanings || [])
                    .map((m) => m.meaning)
                    .join(", ")}
                </div>

                {currentWord.meanings &&
                  currentWord.meanings.length > 0 &&
                  currentWord.meanings.map(
                    (m, idx) =>
                      m.examples &&
                      m.examples.length > 0 && (
                        <div key={idx}>
                          <div style={meaningTitleStyle}>Ví dụ</div>
                          {m.examples.map((ex, i) => (
                            <div key={i} style={exampleBoxStyle}>
                              <div style={exampleJpStyle}>{ex.jp}</div>
                              <div style={exampleEnStyle}>{ex.en}</div>
                            </div>
                          ))}
                        </div>
                      )
                  )}
              </div>
            )}
          </div>

          <div style={progressBarStyle}>
            <div style={progressFillStyle}></div>
          </div>

          <div style={navStyle}>
            <button
              onClick={handlePrev}
              disabled={currentIndex === 0}
              style={
                currentIndex === 0 ? disabledButtonStyle : primaryButtonStyle
              }
            >
              ← Trước
            </button>

            <button onClick={toggleFlip} style={secondaryButtonStyle}>
              {isFlipped ? "Ẩn" : "Xem"}
            </button>

            <button
              onClick={handleNext}
              disabled={currentIndex === allWords.length - 1}
              style={
                currentIndex === allWords.length - 1
                  ? disabledButtonStyle
                  : primaryButtonStyle
              }
            >
              Tiếp →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
