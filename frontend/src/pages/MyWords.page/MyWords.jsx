import React, { useEffect, useState } from "react";
import Sidebar from "../../components/Sidebar/Sidebar";
import Header from "../../components/Header/Header";
import Footer from "../../components/Footer/Footer";
import "./MyWords.css";

const API_BASE = import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8888";

export default function MyWords() {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch danh sách yêu thích
  const fetchFavorites = async () => {
    const token = localStorage.getItem("access");

    if (!token) {
      console.log("⚠ Không có token → user chưa đăng nhập.");
      setWords([]);
      setLoading(false);
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/favorites/`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.status === 401) {
        console.log("❌ Token sai hoặc hết hạn");
        setWords([]);
        setLoading(false);
        return;
      }

      const data = await res.json();

      if (Array.isArray(data)) {
        setWords(data);
      } else {
        setWords([]);
      }
    } catch (err) {
      console.error("❌ Lỗi fetch favorites:", err);
    } finally {
      setLoading(false);
    }
  };

  // Gỡ khỏi yêu thích
  const removeFavorite = async (wordId) => {
    const token = localStorage.getItem("access");

    if (!token) return;

    try {
      const res = await fetch(`${API_BASE}/api/favorites/toggle/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ word_id: wordId }),
      });

      if (res.ok) {
        setWords((prev) => prev.filter((w) => w.id !== wordId));
      }
    } catch (err) {
      console.error("❌ Lỗi remove favorite:", err);
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, []);

  return (
    <div className="mywords-page">
      <div className="sidebar">
        <Sidebar />
      </div>

      <div className="main-content">
        <Header />

        <div className="content">
          <div className="mywords-container">
            {/* Header Section */}
            <div className="mywords-header">
              <div className="header-icon">⭐</div>
              <h1 className="page-title">Từ của tôi</h1>
              <p className="page-subtitle">
                {words.length > 0
                  ? `Bạn có ${words.length} từ trong danh sách yêu thích`
                  : "Chưa có từ nào được lưu"}
              </p>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="loading-state">
                <div className="spinner">⏳</div>
                <p>Đang tải danh sách...</p>
              </div>
            )}

            {/* Empty State */}
            {!loading && words.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">📚</div>
                <h2>Chưa có từ nào</h2>
                <p>Hãy thêm từ vựng yêu thích để học tập hiệu quả hơn!</p>
              </div>
            )}

            {/* Words List */}
            {!loading && words.length > 0 && (
              <div className="words-grid">
                {words.map((word) => (
                  <div key={word.id} className="word-card">
                    <div className="word-header">
                      <div className="word-main">
                        <h2 className="word-kanji">
                          {word.kanji || word.kana}
                        </h2>
                        {word.kana && word.kanji && (
                          <div className="word-kana">{word.kana}</div>
                        )}
                      </div>
                      <button
                        className="favorite-btn active"
                        onClick={() => removeFavorite(word.id)}
                        title="Bỏ yêu thích"
                      >
                        ⭐
                      </button>
                    </div>

                    <div className="word-meanings">
                      {(word.meanings || []).map((m, index) => (
                        <div key={m.id || index} className="meaning-item">
                          <span className="meaning-bullet">•</span>
                          <span className="meaning-text">{m.meaning}</span>
                        </div>
                      ))}
                    </div>

                    <button
                      className="remove-btn"
                      onClick={() => removeFavorite(word.id)}
                    >
                      <span>🗑️</span>
                      Xóa khỏi danh sách
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <Footer />
      </div>
    </div>
  );
}
