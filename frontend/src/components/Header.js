import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Menu, ShoppingCart, Heart } from 'lucide-react'; // Heart 추가
import './Header.css';
import Login from './Login';
import api from '../api/axios';
import './SignUp.css';
import SignUp from './SignUp';
import { Link, useNavigate } from 'react-router-dom';
import { User, Settings, LogIn, LogOut, UserPlus, HelpCircle } from 'lucide-react';

function Header() {
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [isSignUpModalOpen, setIsSignUpModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  // 현재 테마 카테고리 정의
  const categories = [
    '전자기기',
    '패션잡화',
    '화장품',
    '도서',
    '스포츠/레저',
    '문구/취미'
  ];

  useEffect(() => {
    checkLoginStatus();
  }, []);

  const checkLoginStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/accounts/check-login/', {
        withCredentials: true
      });
      if (response.data.isAuthenticated) {
        setIsLoggedIn(true);
        setCurrentUser(response.data.user);
      } else {
        setIsLoggedIn(false);
        setCurrentUser(null);
      }
    } catch (error) {
      console.error('로그인 상태 확인 실패:', error);
      setIsLoggedIn(false);
      setCurrentUser(null);
    }
  };

  const handleLoginSuccess = (user) => {
    setIsLoggedIn(true);
    setCurrentUser(user);
    setIsLoginModalOpen(false);
  };

  const handleLogout = async () => {
    try {
      const response = await api.post('/accounts/logout/');
      if (response.data.status === 'success') {
        setIsLoggedIn(false);
        setCurrentUser(null);
        window.location.reload();
      }
    } catch (error) {
      console.error('로그아웃 실패:', error);
      alert('로그아웃 처리 중 오류가 발생했습니다.');
    }
  };

  const handleSearch = () => {
    if (searchQuery.trim() !== '') {
      navigate(`/search?query=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleCategoryClick = (category) => {
    navigate(`/search?query=${encodeURIComponent(category)}`);
    setIsCategoryOpen(false);
  };

  return (
    <>
<div className="user-menu">
  {isLoggedIn ? (
    <>
      <span className="user-name">
        <User className="icon" size={16} />
        {currentUser?.username}님
      </span>
      <Link to="/mypage" className="user-menu-item">
        <Settings className="icon" size={16} />
        마이페이지
      </Link>
      <span className="divider" />
      <span onClick={handleLogout}>
        <LogOut className="icon" size={16} />
        로그아웃
      </span>
    </>
  ) : (
    <>
      <span onClick={() => setIsLoginModalOpen(true)}>
        <LogIn className="icon" size={16} />
        로그인
      </span>
      <span className="divider" />
      <span onClick={() => setIsSignUpModalOpen(true)}>
        <UserPlus className="icon" size={16} />
        회원가입
      </span>
    </>
  )}
  <span className="divider" />
  <span>
    <HelpCircle className="icon" size={16} />
    고객센터
  </span>
</div>


      <header className="header">
        <nav className="navigation">
        <div className="logo-container">
  <Link to="/" className="logo-link">
    <div className="logo-text">
      <span className="logo-text-pick">Pick</span>
      <span className="logo-text-smart">Smart</span>
    </div>
  </Link>
</div>

          <div className="search-bar">
            <input
              type="text"
              placeholder="검색어를 입력하세요"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button onClick={handleSearch}>검색</button>
          </div>
        </nav>
      </header>

      <div className="sub-navigation">
  <div 
    className="icon-container category-tab"
    onMouseEnter={() => setIsCategoryOpen(true)}
    onMouseLeave={() => setIsCategoryOpen(false)}
  >
    <Menu size={24} />
    {isCategoryOpen && (
      <div className="category-dropdown">
        <ul>
          {categories.map((category, index) => (
            <li 
              key={index} 
              className="category-item"
              onClick={() => handleCategoryClick(category)}
            >
              {category}
            </li>
          ))}
        </ul>
      </div>
    )}
  </div>
  
  <div className="icons-group">
    <Link to="/activity/favorites" className="icon-container favorites-tab">
      <Heart size={24} />
    </Link>
    <Link to="/cart" className="icon-container cart-tab">
      <ShoppingCart size={24} />
    </Link>
  </div>
</div>

      <Login 
  isOpen={isLoginModalOpen} 
  onClose={() => setIsLoginModalOpen(false)}
  onLoginSuccess={handleLoginSuccess}
  onSignUpClick={() => {
    setIsLoginModalOpen(false);  // 로그인 모달 닫기
    setIsSignUpModalOpen(true);  // 회원가입 모달 열기
  }}
/>

      <SignUp
        isOpen={isSignUpModalOpen}
        onClose={() => setIsSignUpModalOpen(false)}
        onSignUpSuccess={() => {
          setIsSignUpModalOpen(false);
          setIsLoginModalOpen(true);
        }}
      />      
    </>
  );
}

export default Header;