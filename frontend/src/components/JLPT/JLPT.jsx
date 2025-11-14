import React from "react";
import "./JLPT.css";
import { Link } from "react-router-dom";

function JLPT() {
  return (
    <div className="jlpt-component" style={{ padding: "40px" }}>
      <h1 style={{ textAlign: "center", marginBottom: "40px" }}>
        Luyện thi JLPT
      </h1>

      <div
        className="jlpt-main"
        style={{ display: "flex", gap: "20px", justifyContent: "center" }}
      >
        {/* Flashcard */}
        <Link to="/flashcards">
          <button className="jlpt-big-btn">📘 Flashcard</button>
        </Link>

        {/* Quiz */}
        <Link to="/quiz">
          <button className="jlpt-big-btn">📝 Quiz</button>
        </Link>
      </div>
    </div>
  );
}

export default JLPT;
