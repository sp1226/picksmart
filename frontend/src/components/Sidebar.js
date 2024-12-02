import React from 'react';
import './Sidebar.css';

function Sidebar() {
    return (
        <aside className="sidebar">
            <h3>카테고리</h3>
            <ul className="category-list">
                <li>과일 & 채소</li>
                <li>신선 식품</li>
                <li>가공 식품</li>
                <li>음료</li>
                <li>생활 용품</li>
            </ul>
        </aside>
    );
}

export default Sidebar;