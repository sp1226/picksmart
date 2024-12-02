// src/components/SignUp.js
import React, { useState } from 'react';
import axios from 'axios';
import './SignUp.css';

function SignUp({ isOpen, onClose, onSignUpSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [gender, setGender] = useState('M');
  const [ageGroup, setAgeGroup] = useState('20');
  const [incomeLevel, setIncomeLevel] = useState('M');
  const [error, setError] = useState('');

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/accounts/signup/', {
        username,
        password,
        gender,
        age_group: ageGroup,
        income_level: incomeLevel
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
        setGender('M');
        setAgeGroup('20');
        setIncomeLevel('M');
        if (onSignUpSuccess) {
          onSignUpSuccess(response.data.user);
        }
        if (onClose) {
          onClose();
        }
        alert('회원가입이 완료되었습니다. 이제 로그인해주세요.');
      }
    } catch (error) {
      setError(error.response?.data?.message || '회원가입에 실패했습니다.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="signup-modal-overlay" onClick={onClose}>
      <div className="signup-modal" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>
        
        <div className="signup-header">
          <h2>회원가입</h2>
          <p className="signup-subtitle">PickSmart에 오신 것을 환영합니다.</p>
        </div>

        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSignUp}>
          <div className="form-group">
            <div className="input-wrapper">
              <label htmlFor="username">사용자명</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="사용자명을 입력하세요"
                required
              />
            </div>

            <div className="input-wrapper">
              <label htmlFor="password">비밀번호</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="비밀번호를 입력하세요"
                required
              />
            </div>

            <div className="input-wrapper">
              <label htmlFor="gender">성별</label>
              <div className="form-select">
                <select
                  id="gender"
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                >
                  <option value="M">남성</option>
                  <option value="F">여성</option>
                  <option value="O">기타</option>
                </select>
              </div>
            </div>

            <div className="input-wrapper">
              <label htmlFor="ageGroup">연령대</label>
              <div className="form-select">
                <select
                  id="ageGroup"
                  value={ageGroup}
                  onChange={(e) => setAgeGroup(e.target.value)}
                >
                  <option value="10">10대</option>
                  <option value="20">20대</option>
                  <option value="30">30대</option>
                  <option value="40">40대</option>
                  <option value="50">50대 이상</option>
                </select>
              </div>
            </div>

            <div className="input-wrapper">
              <label htmlFor="incomeLevel">소득 수준</label>
              <div className="form-select">
                <select
                  id="incomeLevel"
                  value={incomeLevel}
                  onChange={(e) => setIncomeLevel(e.target.value)}
                >
                  <option value="L">저소득</option>
                  <option value="M">중소득</option>
                  <option value="H">고소득</option>
                </select>
              </div>
            </div>
          </div>

          <button type="submit" className="signup-button">
            회원가입
          </button>
        </form>
      </div>
    </div>
  );
}

export default SignUp;