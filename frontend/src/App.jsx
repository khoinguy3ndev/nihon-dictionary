import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage/HomePage";
import LoginPage from "./pages/LoginPage/LoginPage";
import RegisterPage from "./pages/RegisterPage/RegisterPage";
import TranslatePage from "./pages/TranslatePage/TranslatePage";
import IntroducePage from "./pages/IntroducePage/Introducepage";
import JLPTPage from "./pages/JLPTPage/JLPTPage";
import FlashcardsPage from "./pages/FlashcardPage/FlashcardPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/translate" element={<TranslatePage />} />
        <Route path="/introduce" element={<IntroducePage />} />
        <Route path="/jlpt" element={<JLPTPage />} />
        <Route path="*" element={<HomePage />} />
        <Route path="/flashcards" element={<FlashcardsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
