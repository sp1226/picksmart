// my-ecommerce/src/components/RecommendList.js
import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import './RecommendList.css';
import { Link } from 'react-router-dom';
import SmartImage from './SmartImage';
import Tag from './common/Tag';


function RecommendList() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecommendations();
    const interval = setInterval(fetchRecommendations, 300000);
    return () => clearInterval(interval);
  }, []);

  // RecommendList.js 수정
  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/products/recommendations/');
      console.log('Recommendations Data:', response.data);  // 추가
      setRecommendations(response.data);
      setError(null);
    } catch (err) {
      setError('추천 상품을 불러오는데 실패했습니다.');
      console.error('Failed to fetch recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProductClick = async (productId) => {
    try {
      const startTime = Date.now();
      
      await api.post(`/products/${productId}/log_interaction/`, {
        type: 'click',
        duration: Math.floor((Date.now() - startTime) / 1000)
      });
    } catch (err) {
      console.error('Failed to log interaction:', err);
    }
  };

  if (loading) {
    return (
      <div className="recommend-list-container">
        <h2 className="recommend-title">당신의 Pick</h2>
        <div className="loading">상품을 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="recommend-list-container">
        <h2 className="recommend-title">당신의 Pick</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="recommend-list-container">
      <h2 className="recommend-title">당신의 Pick</h2>
      <div className="recommend-list">
        {recommendations.map((item) => (
          <Link 
            to={`/product/${item.id}`} 
            key={item.id} 
            className="recommend-item"
          >
            <SmartImage product={item} variant="list" />
            <div className="product-info">
  <h3>{item.title}</h3>
  <p>{item.description}</p>
  <div className="price">
    {Math.floor(item.price).toLocaleString()}원
  </div>
</div>

          </Link>
        ))}
      </div>
    </div>
  );
}

export default RecommendList;