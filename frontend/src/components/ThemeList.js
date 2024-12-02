// /Users/sp/vscode/1101/my-ecommerce/src/components/ThemeList.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ThemeList.css';
import { Link } from 'react-router-dom';
import SmartImage from './SmartImage';

  
  const ThemeSection = ({ theme }) => {
    const { title, products } = theme;
    
    return (
      <div className="theme-section" data-category={title}>
        {/* <h3>{title}</h3> 이 줄을 제거 */}
        <div className="grid-container">
          {products.map((item) => (
            <Link to={`/product/${item.id}`} key={item.id} className="grid-item">
              <SmartImage 
                product={item} 
                variant="list"
              />
              <div className="item-info">
                <h4 className="item-name">{item.title}</h4>
                <p className="item-price">
                  {Math.floor(Number(item.price)).toLocaleString()}원
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    );
  };

const ThemeList = () => {
  const [themes, setThemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchThemes = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/products/themes/');
        console.log('Theme data:', response.data); // 데이터 확인용 로그
        setThemes(response.data);
        setError(null);
      } catch (err) {
        console.error('테마 데이터를 불러오는데 실패했습니다:', err);
        setError('테마 데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchThemes();
  }, []);

  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>에러: {error}</div>;
  if (!themes.length) return <div>표시할 테마가 없습니다.</div>;

  return (
    <div className="theme-list-container">
      <h2 className="theme-list-title">테마별 상품</h2>
      <div className="theme-list">
        {themes.map((theme) => (
          <ThemeSection key={theme.title} theme={theme} />
        ))}
      </div>
    </div>
  );
};

export default ThemeList;