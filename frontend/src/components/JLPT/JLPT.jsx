import React, { useState } from "react";
import "./JLPT.css";
import { Link } from "react-router-dom";

function JLPT() {
  const [level, setLevel] = useState("N5");
  const [wordType, setWordType] = useState("vocabulary");
  const [page, setPage] = useState(1);

  const words = [
    { jp: "人", reading: "ひと", meaning: "người" },
    { jp: "年", reading: "とし", meaning: "năm; tuổi" },
    { jp: "何", reading: "なに", meaning: "cái gì" },
    { jp: "私", reading: "わたし", meaning: "tôi" },
    { jp: "今", reading: "いま", meaning: "bây giờ" },
  ];

  return (
    <div className="jlpt-component">
      {/* Sidebar nhỏ */}
      <div className="jlpt-sidebar">
        <h3>Chọn loại từ</h3>
        <div className="filter-group">
          <label>
            <input
              type="radio"
              checked={wordType === "vocabulary"}
              onChange={() => setWordType("vocabulary")}
            />
            Từ vựng
          </label>
          <label>
            <input
              type="radio"
              checked={wordType === "grammar"}
              onChange={() => setWordType("grammar")}
            />
            Ngữ pháp
          </label>
          <label>
            <input
              type="radio"
              checked={wordType === "kanji"}
              onChange={() => setWordType("kanji")}
            />
            Hán tự
          </label>
        </div>

        <h3>Chọn cấp độ</h3>
        <div className="filter-group">
          {["N5", "N4", "N3", "N2", "N1"].map((lv) => (
            <label key={lv}>
              <input
                type="radio"
                checked={level === lv}
                onChange={() => setLevel(lv)}
              />
              {lv}
            </label>
          ))}
        </div>
      </div>

      {/* Main content JLPT */}
      <div className="jlpt-main">
        <div className="jlpt-top-buttons">
          <Link to="/flashcards">
            <button>FlashCard</button>
          </Link>
          <button>Quizz</button>
          <button>Luyện nói, viết</button>
          <button>Mini Test</button>
        </div>

        <div className="jlpt-word-list">
          {words.map((w, idx) => (
            <div className="jlpt-word-card" key={idx}>
              <div className="word-jp">
                <span className="jp">{w.jp}</span>
                <span className="reading">{w.reading}</span>
              </div>
              <div className="word-meaning">{w.meaning}</div>
              <div className="word-actions">
                <button>🔊</button>
                <button>＋</button>
              </div>
            </div>
          ))}
        </div>

        <div className="jlpt-pagination">
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>
            «
          </button>
          {[1, 2, 3].map((p) => (
            <button
              key={p}
              className={page === p ? "active" : ""}
              onClick={() => setPage(p)}
            >
              {p}
            </button>
          ))}
          <button onClick={() => setPage(page + 1)}>»</button>
        </div>
      </div>
    </div>
  );
}

export default JLPT;
