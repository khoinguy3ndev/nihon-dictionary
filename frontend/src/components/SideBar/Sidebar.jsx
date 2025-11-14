import React from "react";
import { NavLink } from "react-router-dom";
import {
  FaSearch,
  FaBook,
  FaClipboardList,
  FaBookReader,
  FaEdit,
  FaComments,
  FaInfoCircle,
  FaCog,
  FaUser,
} from "react-icons/fa";
import "./Sidebar.css";

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <div className="logo-icon">こ</div>
          <span className="logo-text">koihi</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <ul className="menu">
          <li>
            <NavLink
              to="/search"
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <div className="icon-wrapper">
                <FaSearch />
              </div>
              <span>Tra cứu</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/translate"
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <div className="icon-wrapper">
                <FaBook />
              </div>
              <span>Dịch</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/jlpt"
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <div className="icon-wrapper">
                <FaClipboardList />
              </div>
              <span>JLPT</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/mywords"
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <div className="icon-wrapper">
                <FaBookReader />
              </div>
              <span>Từ của tôi</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/japanese-name"
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <div className="icon-wrapper">
                <FaUser />
              </div>
              <span>Tên tiếng Nhật</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/introduce"
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <div className="icon-wrapper">
                <FaInfoCircle />
              </div>
              <span>Giới thiệu</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                `menu-item ${isActive ? "active" : ""}`
              }
            >
              <div className="icon-wrapper">
                <FaCog />
              </div>
              <span>Cài đặt</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </div>
  );
}

export default Sidebar;
