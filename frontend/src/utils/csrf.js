// utils/csrf.js
import axios from 'axios';

export const fetchCSRFToken = async () => {
  try {
    await axios.get('http://localhost:8000/api/accounts/csrf/', {
      withCredentials: true
    });
  } catch (error) {
    console.error('CSRF 토큰 설정 실패:', error);
  }
};