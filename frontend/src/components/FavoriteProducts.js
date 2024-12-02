import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import SmartImage from './SmartImage';
import AlertModal from './AlertModal';
import ProductActions from './common/ProductActions';

function FavoriteProducts() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [modalConfig, setModalConfig] = useState({ 
    isOpen: false,
    message: '',
    type: 'success'
  });

  const navigate = useNavigate();

  const fetchFavorites = useCallback(async () => {
    try {
      const response = await api.get('/user-activity/favorites/');
      setFavorites(response.data.results || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching favorites:', err);
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('찜한 상품을 불러오는데 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const removeFavorite = async (productId) => {
    try {
      await api.post(`/products/${productId}/toggle_favorite/`);
      fetchFavorites();
    } catch (err) {
      setModalConfig({
        isOpen: true,
        message: '찜하기 취소에 실패했습니다.',
        type: 'error',
        onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
      });
    }
  };

  const sendToCart = async (productId) => {
    try {
      await api.post('/cart/add_multiple/', {
        productIds: [productId]
      });
      setModalConfig({
        isOpen: true,
        message: '장바구니에 추가되었습니다.',
        type: 'success',
        onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
      });
    } catch (err) {
      setModalConfig({
        isOpen: true,
        message: '장바구니 추가에 실패했습니다.',
        type: 'error',
        onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
      });
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, [fetchFavorites]);

  if (loading) return <div className="loading">로딩 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="favorite-products-container">
      <h2>찜한 상품</h2>
      {favorites.length === 0 ? (
        <p className="empty-message">찜한 상품이 없습니다.</p>
      ) : (
        <div className="products-grid">
          {favorites.map(product => (
            <div key={product.id} className="product-card">
              <ProductActions 
                onAddToCart={() => sendToCart(product.id)}
                onRemove={() => removeFavorite(product.id)}
              />
              <div onClick={() => navigate(`/product/${product.id}`)}>
                <SmartImage product={product} variant="list" />
                <div className="product-info">
                  <h3>{product.title}</h3>
                  <p className="price">₩{Number(product.price).toLocaleString()}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      <AlertModal {...modalConfig} />
    </div>
  );
}

export default FavoriteProducts;