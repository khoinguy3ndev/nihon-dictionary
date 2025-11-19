import React, { useEffect, useMemo, useState } from "react";
import "./Quiz.css";

const API_BASE = import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8888";

export default function Quiz() {
  const [level, setLevel] = useState("N5");
  const [count, setCount] = useState(10);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    setQuestions([]);
    setAnswers({});
    setSubmitted(false);
    setScore(null);
    setCurrentIndex(0);
    setError("");
  }, [level, count]);

  const fetchQuiz = async () => {
    setLoading(true);
    setError("");
    setQuestions([]);
    setAnswers({});
    setSubmitted(false);
    setScore(null);
    setCurrentIndex(0);

    try {
      const token = localStorage.getItem("access");
      const res = await fetch(`${API_BASE}/api/quiz/jlpt/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ level, count }),
      });

      const json = await res.json().catch(() => null);
      if (!res.ok) {
        const msg = json?.detail || json?.message || `HTTP ${res.status}`;
        throw new Error(msg);
      }

      if (!Array.isArray(json?.questions)) {
        throw new Error("Server did not return questions array");
      }

      const normalized = json.questions.map((q, idx) => ({
        id: q.id ?? idx,
        sentence: q.sentence ?? "",
        choices: Array.isArray(q.choices) ? q.choices : [],
        correct_index:
          typeof q.correct_index === "number"
            ? q.correct_index
            : typeof q.correct === "number"
            ? q.correct
            : null,
      }));

      setQuestions(normalized);
    } catch (err) {
      setError(err.message || "Lỗi khi lấy câu hỏi");
    } finally {
      setLoading(false);
    }
  };

  const selectChoice = (qIndex, choiceIndex) => {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [qIndex]: choiceIndex }));
  };

  const submit = () => {
    if (questions.length === 0) return;
    let correct = 0;
    questions.forEach((q, i) => {
      const a = answers[i];
      if (typeof a === "number" && a === q.correct_index) correct += 1;
    });
    setScore(correct);
    setSubmitted(true);
  };

  const restart = () => {
    setAnswers({});
    setSubmitted(false);
    setScore(null);
    setCurrentIndex(0);
  };

  const currentQuestion = questions[currentIndex];

  const progressLabel = useMemo(() => {
    if (!questions.length) return "0/0";
    return `${Object.keys(answers).length}/${questions.length}`;
  }, [answers, questions]);

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <h1 className="quiz-title">JLPT Quiz</h1>
        <p className="quiz-subtitle">Luyện tập năng lực tiếng Nhật</p>
      </div>

      <div className="quiz-settings">
        <div className="setting-group">
          <label className="setting-label">Cấp độ</label>
          <select
            className="setting-select"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
          >
            <option value="N5">N5 - Sơ cấp</option>
            <option value="N4">N4 - Sơ - Trung cấp</option>
            <option value="N3">N3 - Trung cấp</option>
            <option value="N2">N2 - Trung - Cao cấp</option>
            <option value="N1">N1 - Cao cấp</option>
          </select>
        </div>

        <div className="setting-group">
          <label className="setting-label">Số câu hỏi</label>
          <input
            type="number"
            min={1}
            max={50}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="setting-input"
          />
        </div>

        <button
          onClick={fetchQuiz}
          disabled={loading}
          className="btn btn-primary btn-generate"
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Đang tải...
            </>
          ) : (
            "Tạo đề thi"
          )}
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          {error}
        </div>
      )}

      {!questions.length && !loading && (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <p>Chọn cấp độ và số câu hỏi, sau đó nhấn "Tạo đề thi" để bắt đầu</p>
        </div>
      )}

      {questions.length > 0 && (
        <div className="quiz-content">
          <div className="quiz-info-bar">
            <div className="info-badge">
              <span className="info-label">Cấp độ:</span>
              <span className="info-value">{level}</span>
            </div>
            <div className="info-badge">
              <span className="info-label">Số câu:</span>
              <span className="info-value">{questions.length}</span>
            </div>
            <div className="info-badge">
              <span className="info-label">Đã làm:</span>
              <span className="info-value">{progressLabel}</span>
            </div>
          </div>

          <div className="quiz-controls">
            <div className="view-mode-group">
              <button
                onClick={() => setShowAll(false)}
                className={`btn btn-view ${!showAll ? "active" : ""}`}
              >
                📄 Từng câu
              </button>
              <button
                onClick={() => setShowAll(true)}
                className={`btn btn-view ${showAll ? "active" : ""}`}
              >
                📋 Tất cả
              </button>
            </div>
            <div className="action-group">
              <button onClick={restart} className="btn btn-secondary">
                🔄 Làm lại
              </button>
              <button onClick={() => fetchQuiz()} className="btn btn-secondary">
                ✨ Đề mới
              </button>
            </div>
          </div>

          {showAll ? (
            <div className="questions-list">
              {questions.map((q, qi) => (
                <QuestionCard
                  key={q.id}
                  qIndex={qi}
                  question={q}
                  selected={answers[qi]}
                  onSelect={selectChoice}
                  submitted={submitted}
                />
              ))}

              {!submitted ? (
                <div className="submit-section">
                  <button onClick={submit} className="btn btn-submit">
                    ✓ Nộp bài
                  </button>
                </div>
              ) : (
                <ResultPanel score={score} total={questions.length} />
              )}
            </div>
          ) : (
            <div className="single-question-view">
              <QuestionCard
                qIndex={currentIndex}
                question={currentQuestion}
                selected={answers[currentIndex]}
                onSelect={selectChoice}
                submitted={submitted}
              />

              <div className="navigation-bar">
                <button
                  onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
                  disabled={currentIndex === 0}
                  className="btn btn-nav"
                >
                  ← Trước
                </button>

                <div className="question-indicator">
                  Câu {currentIndex + 1} / {questions.length}
                </div>

                <button
                  onClick={() =>
                    setCurrentIndex((i) =>
                      Math.min(questions.length - 1, i + 1)
                    )
                  }
                  disabled={currentIndex === questions.length - 1}
                  className="btn btn-nav"
                >
                  Sau →
                </button>

                {!submitted ? (
                  <button onClick={submit} className="btn btn-submit">
                    ✓ Nộp bài
                  </button>
                ) : (
                  <ResultPanel score={score} total={questions.length} />
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function QuestionCard({ qIndex, question, selected, onSelect, submitted }) {
  if (!question)
    return <div className="question-card">(Câu hỏi không hợp lệ)</div>;

  return (
    <div className="question-card">
      <div className="question-number">Câu {qIndex + 1}</div>
      <div
        className="question-text"
        dangerouslySetInnerHTML={{ __html: question.sentence }}
      />

      <div className="choices-grid">
        {question.choices.map((c, ci) => {
          const isSelected = selected === ci;
          const isCorrect = question.correct_index === ci;

          let className = "choice-card";
          if (submitted) {
            if (isCorrect) className += " choice-correct";
            else if (isSelected && !isCorrect) className += " choice-incorrect";
          } else if (isSelected) {
            className += " choice-selected";
          }

          return (
            <label key={ci} className={className}>
              <input
                type="radio"
                name={`q-${qIndex}`}
                className="choice-input"
                checked={isSelected}
                onChange={() => onSelect(qIndex, ci)}
              />
              <div className="choice-content">
                <div className="choice-letter">
                  {String.fromCharCode(65 + ci)}
                </div>
                <div
                  className="choice-text"
                  dangerouslySetInnerHTML={{ __html: c }}
                />
              </div>
            </label>
          );
        })}
      </div>

      {submitted && (
        <div className="answer-reveal">
          ✓ Đáp án đúng:{" "}
          <strong>{String.fromCharCode(65 + question.correct_index)}</strong>
        </div>
      )}
    </div>
  );
}

function ResultPanel({ score, total }) {
  const percentage = ((score / total) * 100).toFixed(0);
  const isPassed = percentage >= 60;

  return (
    <div className={`result-panel ${isPassed ? "passed" : "failed"}`}>
      <div className="result-icon">{isPassed ? "🎉" : "💪"}</div>
      <div className="result-content">
        <div className="result-score">
          {score} / {total}
        </div>
        <div className="result-percentage">{percentage}%</div>
        <div className="result-message">
          {isPassed ? "Xuất sắc!" : "Cố gắng lên!"}
        </div>
      </div>
    </div>
  );
}
