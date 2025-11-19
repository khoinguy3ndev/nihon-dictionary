// src/components/DictionarySearchAll.jsx
import React, { useState } from "react";
import "./DictionaryEntryCard.css";

const API_BASE = import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8888";

export default function DictionarySearchAll({ onSearchDone }) {
  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);

  const [addingToFlashcard, setAddingToFlashcard] = useState(new Set());
  const [inFlashcards, setInFlashcards] = useState(new Set());
  const [defaultFlashcardId, setDefaultFlashcardId] = useState(null);
  const [favorites, setFavorites] = useState(new Set());
  const isLoggedIn = Boolean(localStorage.getItem("access"));

  const fetchUrl = async (url, options = {}) => {
    setLoading(true);
    setErr("");
    try {
      const res = await fetch(url, {
        headers: { Accept: "application/json", ...options.headers },
      });
      const json = await res.json().catch(() => null);

      if (!res.ok) {
        const detail =
          json?.detail ||
          (json &&
            Object.entries(json)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
              .join(" | "));
        throw new Error(detail || `${res.status} ${res.statusText}`);
      }

      const results = Array.isArray(json) ? json : json?.results || [];
      setItems(results);
      setNextUrl(json?.next || null);
      setPrevUrl(json?.previous || null);
      if (onSearchDone) onSearchDone(); // ⭐ báo cho History reload

      // Kiểm tra từ đã có trong flashcard
      if (results.length > 0) {
        const token = localStorage.getItem("access");

        // Không đăng nhập → không check flashcard
        if (!token) {
          setInFlashcards(new Set());
          return;
        }

        const flashcardId = await ensureFlashcard();
        const inFlashSet = new Set();

        await Promise.all(
          results.map(async (entry) => {
            const resCheck = await fetch(
              `${API_BASE}/api/flashcards/${flashcardId}/is_in/?word_id=${entry.id}`,
              { headers: { Authorization: `Bearer ${token}` } }
            );
            if (!resCheck.ok) return;
            const jsonCheck = await resCheck.json().catch(() => null);
            if (jsonCheck?.in_flashcard) inFlashSet.add(entry.id);
          })
        );

        setInFlashcards(inFlashSet);
      }
    } catch (e) {
      setErr(e.message || "Lỗi gọi API");
      setItems([]);
      setNextUrl(null);
      setPrevUrl(null);
    } finally {
      setLoading(false);
    }
  };

  const onSearch = (e) => {
    e.preventDefault();
    if (!q.trim()) return;
    const token = localStorage.getItem("access");
    const url = `${API_BASE}/api/search/?q=${encodeURIComponent(q.trim())}`;
    fetchUrl(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  };

  const loadNext = () => {
    const token = localStorage.getItem("access");
    if (nextUrl)
      fetchUrl(nextUrl, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
  };

  const loadPrev = () => {
    const token = localStorage.getItem("access");
    if (prevUrl)
      fetchUrl(prevUrl, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
  };

  const ensureFlashcard = async () => {
    if (defaultFlashcardId) return defaultFlashcardId;

    const token = localStorage.getItem("access");
    const res = await fetch(`${API_BASE}/api/flashcards/create/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ name: "My deck" }),
    });

    if (!res.ok) throw new Error("Không tạo được flashcard");
    const data = await res.json();
    setDefaultFlashcardId(data.id);
    return data.id;
  };

  const addToFlashcard = async (entry) => {
    const entryId = entry.id;
    setAddingToFlashcard((prev) => new Set([...prev, entryId]));

    try {
      const token = localStorage.getItem("access");
      const flashcardId = await ensureFlashcard();

      const res = await fetch(
        `${API_BASE}/api/flashcards/${flashcardId}/add/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ word_id: entryId }),
        }
      );

      if (!res.ok) {
        const json = await res.json().catch(() => null);
        throw new Error(json?.detail || "Lỗi thêm vào flashcard");
      }

      setInFlashcards((prev) => new Set([...prev, entryId]));

      setTimeout(() => {
        setAddingToFlashcard((prev) => {
          const newSet = new Set(prev);
          newSet.delete(entryId);
          return newSet;
        });
      }, 2000);
    } catch (err) {
      alert(err.message);
      setAddingToFlashcard((prev) => {
        const newSet = new Set(prev);
        newSet.delete(entryId);
        return newSet;
      });
    }
  };
  // toggle favorite
  const toggleFavorite = async (entry) => {
    try {
      const token = localStorage.getItem("access");
      const res = await fetch(`${API_BASE}/api/favorites/toggle/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ word_id: entry.id }),
      });

      const json = await res.json();
      if (!res.ok) throw new Error(json?.detail || "Lỗi API");

      setFavorites((prev) => {
        const newSet = new Set(prev);
        if (json.favorited) newSet.add(entry.id);
        else newSet.delete(entry.id);
        return newSet;
      });

      entry.is_favorited = json.favorited;
      setItems((prev) => [...prev]); // force re-render
    } catch (err) {
      alert(`Lỗi toggle favorite: ${err.message}`);
    }
  };

  return (
    <div className="wrap">
      <header className="header">
        <h1 className="title">Từ điển Tiếng Nhật</h1>
        <p className="subtitle">Tra cứu từ vựng nhanh chóng và chính xác</p>
      </header>

      <div className="searchContainer">
        <div className="searchRow">
          <input
            className="input"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Nhập từ cần tra (vd: いいえ / いえ / nihon)"
            onKeyPress={(e) => e.key === "Enter" && onSearch(e)}
          />
          <button className="btn" onClick={onSearch} disabled={loading}>
            {loading ? "Đang tìm..." : "Tìm kiếm"}
          </button>
        </div>
      </div>

      {err && <div className="error">{err}</div>}

      {!loading && !err && items.length === 0 && q.trim() !== "" && (
        <div className="noResults">
          <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
          <div>Không tìm thấy kết quả phù hợp</div>
        </div>
      )}

      {items.map((entry) => {
        const title = entry.kanji || entry.kana || "—";
        const kana = entry.kana || "";
        const jlpt = entry.jlpt_level || "";
        const isAdding = addingToFlashcard.has(entry.id);
        const isInFlashcard = inFlashcards.has(entry.id);
        const isFav = entry.is_favorited;

        return (
          <article key={entry.id} className="card">
            <header className="cardHeader">
              <div className="cardHeaderContent">
                <h2 className="word">{title}</h2>
                {kana && <div className="kana">{kana}</div>}
                <div className="metaRow">
                  {jlpt && <span className="badge">JLPT {jlpt}</span>}
                </div>
              </div>

              {isLoggedIn && (
                <button
                  className={`addToFlashcardBtn ${
                    isAdding || isInFlashcard ? "addToFlashcardBtnSuccess" : ""
                  }`}
                  onClick={() => addToFlashcard(entry)}
                  disabled={isAdding || isInFlashcard}
                >
                  {isAdding ? (
                    <>
                      <span style={{ fontSize: 16 }}>⏳</span>
                      <span>Đang thêm...</span>
                    </>
                  ) : isInFlashcard ? (
                    <>
                      <span style={{ fontSize: 16 }}>✓</span>
                      <span>Đã có</span>
                    </>
                  ) : (
                    <>
                      <span style={{ fontSize: 18, fontWeight: 700 }}>+</span>
                      <span>Flashcard</span>
                    </>
                  )}
                </button>
              )}

              {isLoggedIn && (
                <button
                  className="favBtn"
                  style={{
                    color: isFav ? "#dc2626" : "#64748b",
                    borderColor: isFav ? "#dc2626" : "#e2e8f0",
                  }}
                  onClick={() => toggleFavorite(entry)}
                >
                  {isFav ? "❤️ Đã thích" : "🤍 Yêu thích"}
                </button>
              )}
            </header>

            <section>
              <h3 className="sectionTitle">Nghĩa của từ</h3>
              <ol className="meaningList">
                {(entry.meanings || []).map((m, idx) => (
                  <li key={m.id ?? idx} className="meaningItem">
                    <div className="meaningLine">
                      <span className="meaningIdx">{idx + 1}</span>
                      <span className="meaningText">{m.meaning || "—"}</span>
                    </div>
                    {Array.isArray(m.examples) && m.examples.length > 0 && (
                      <ul className="exampleList">
                        {m.examples.map((ex) => (
                          <li key={ex.id} className="exampleItem">
                            <div className="exJp">{ex.jp}</div>
                            <div className="exEn">{ex.en}</div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ol>
            </section>
          </article>
        );
      })}

      {(prevUrl || nextUrl) && (
        <div className="pager">
          {prevUrl && (
            <button className="pagerBtn" onClick={loadPrev}>
              ← Trang trước
            </button>
          )}
          {nextUrl && (
            <button className="pagerBtn" onClick={loadNext}>
              Trang sau →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
