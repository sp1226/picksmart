import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../api/axios';
import './SearchResults.css';
import SmartImage from './SmartImage';
import { Link } from 'react-router-dom';

function SearchResults() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const location = useLocation();
  const query = new URLSearchParams(location.search).get('query');

  // fetchProducts를 useCallback으로 메모이제이션
  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get('/products/themes/');
      const allProducts = response.data.flatMap(theme => {
        if (theme.title.toLowerCase().includes(query.toLowerCase())) {
          return theme.products;
        }
        return theme.products.filter(product => 
          product.title.toLowerCase().includes(query.toLowerCase()) ||
          product.description.toLowerCase().includes(query.toLowerCase())
        );
      });

      setProducts(allProducts);
      setError(null);
    } catch (err) {
      console.error('검색 결과를 가져오는데 실패했습니다:', err);
      setError('검색 결과를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [query]); // query만 의존성으로 추가

  // useEffect는 한 번만 사용
  useEffect(() => {
    if (query) {
      fetchProducts();
    }
  }, [query, fetchProducts]); // 두 의존성 모두 포함

  if (loading) return <div className="search-results-loading">로딩 중...</div>;
  if (error) return <div className="search-results-error">{error}</div>;

  return (
    <div className="search-results-container">
      <h2>"{query}" 검색 결과</h2>
      {products.length === 0 ? (
        <p>검색 결과가 없습니다.</p>
      ) : (
        <div className="products-grid">
          {products.map((product) => (
            <Link to={`/product/${product.id}`} key={product.id} className="product-card">
              <SmartImage product={product} variant="list" />
              <div className="product-info">
                <h3>{product.title}</h3>
                <p className="price">₩{Number(product.price).toLocaleString()}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchResults;