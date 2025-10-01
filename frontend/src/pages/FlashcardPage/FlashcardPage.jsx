// src/pages/FlashcardPage/FlashcardPage.jsx
import React from "react";
import Header from "../../components/Header/Header";
import Sidebar from "../../components/Sidebar/Sidebar";
import Flashcard from "../../components/Flashcard/Flashcards"; // chỉnh lại nếu tên file khác

const pageStyle = {
  display: "flex",
  minHeight: "100vh",
  fontFamily:
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
};

const sidebarStyle = {
  width: "250px",
  borderRight: "1px solid #e5e7eb",
};

const mainContentStyle = {
  flex: 1,
  display: "flex",
  flexDirection: "column",
};

const contentStyle = {
  flex: 1,
  padding: "20px",
  background: "#f3f4f6",
};

export default function FlashcardPage() {
  return (
    <div style={pageStyle}>
      {/* Sidebar */}
      <aside style={sidebarStyle}>
        <Sidebar />
      </aside>

      {/* Main content */}
      <div style={mainContentStyle}>
        {/* Header */}
        <Header />

        {/* Flashcard content */}
        <main style={contentStyle}>
          <Flashcard />
        </main>
      </div>
    </div>
  );
}
