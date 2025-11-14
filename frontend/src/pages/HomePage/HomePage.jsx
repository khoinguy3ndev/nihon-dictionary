import React from "react";
import Header from "../../components/Header/Header";
import Footer from "../../components/Footer/Footer";
import SearchBox from "../../components/SearchBox/SearchBox";
import Sidebar from "../../components/Sidebar/Sidebar";
import History from "../../components/History/History";
import "./HomePage.css";
import DictionaryEntryCard from "../../components/DictionaryEntryCard/DictionaryEntryCard";
import { useState } from "react";

function HomePage() {
  const [reloadHistory, setReloadHistory] = useState(0);

  const handleSearchDone = () => {
    setReloadHistory((prev) => prev + 1); // ⭐ trigger reload
  };

  return (
    <div className="homepage">
      <div className="sidebar">
        <Sidebar />
      </div>

      <div className="main-content">
        <Header />

        <div className="content-wrapper">
          <div className="content-left">
            {/* ⭐ Truyền callback vào DictionaryEntryCard */}
            <DictionaryEntryCard onSearchDone={handleSearchDone} />
          </div>

          <div className="content-right">
            {/* ⭐ Mỗi lần reloadHistory thay đổi → History fetch lại */}
            <History reloadSignal={reloadHistory} />
          </div>
        </div>

        <Footer />
      </div>
    </div>
  );
}

export default HomePage;
