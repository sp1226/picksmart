import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

function Login({ isOpen, onClose, onLoginSuccess, onSignUpClick }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/accounts/login/', {
        username,
        password
      }, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.data.status === 'success') {
        setError('');
        setUsername('');
        setPassword('');
        if (onLoginSuccess) {
          onLoginSuccess(response.data.user);
        }
        if (onClose) {
          onClose();
        }
        window.location.reload();
      }
    } catch (error) {
      setError('로그인에 실패했습니다. 계정명과 비밀번호를 확인해주세요.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="login-modal-overlay" onClick={onClose}>
      <div className="login-modal" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        <div className="login-header">
          <h2>로그인</h2>
          <p className="login-subtitle">PickSmart에 오신 것을 환영합니다.</p>
        </div>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <div className="input-wrapper">
              <label htmlFor="username">사용자명</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="예: male_20_low"
              />
            </div>
            <div className="input-wrapper">
              <label htmlFor="password">비밀번호</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="비밀번호 입력"
              />
            </div>
          </div>
          <div className="button-group">
            <button type="submit" className="login-button">로그인</button>
            <button 
              type="button" 
              className="signup-link-button"
              onClick={(e) => {
                e.preventDefault();
                onClose();
                onSignUpClick();
              }}
            >
              회원가입
            </button>
          </div>
        </form>
        <div className="test-accounts">
          <h3>테스트 계정 안내</h3>
          <div className="account-pattern-info">
            <p>아이디 생성 규칙: <strong>성별_연령대_소득수준</strong></p>
            <ul className="pattern-details">
              <li>성별: male(남성), female(여성)</li>
              <li>연령대: 10, 20, 30, 40, 50</li>
              <li>소득수준: low(저소득), mid(중소득), high(고소득)</li>
            </ul>
            <p className="pattern-example">예시: male_20_low (20대 남성 저소득)</p>
          </div>
          
          <div className="test-accounts-info">
            <p>모든 계정 비밀번호: testpass123</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;