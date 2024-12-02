// src/components/Cart.js

import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import './Cart.css';
import SmartImage from './SmartImage';
import AlertModal from './AlertModal'; // AlertModal import 추가

function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    message: '',
    type: 'success',
  });

  useEffect(() => {
    fetchCartItems();
  }, []);

  const fetchCartItems = async () => {
    try {
      const response = await api.get('/cart/my_cart/');
      setCartItems(Array.isArray(response.data) ? response.data : []);
      setError(null);
    } catch (err) {
      setError('장바구니를 불러오는데 실패했습니다.');
      console.error('Error fetching cart:', err);
      setCartItems([]);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId, newQuantity) => {
    try {
      setCartItems(prevItems => 
        prevItems.map(item => 
          item.product.id === productId 
            ? { ...item, quantity: newQuantity }
            : item
        )
      );

      const response = await api.post(`/products/${productId}/update_cart_quantity/`, {
        quantity: newQuantity
      });

      if (response.data.status !== 'success') {
        fetchCartItems();
        alert('수량 변경에 실패했습니다.');
      }
    } catch (err) {
      console.error('Failed to update quantity:', err);
      fetchCartItems();
      alert('수량 변경에 실패했습니다.');
    }
  };

  const removeFromCart = async (productId) => {
    try {
      await api.delete(`/cart/${productId}/remove_from_cart/`);
      fetchCartItems();
    } catch (err) {
      alert('상품 삭제에 실패했습니다.');
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => 
      total + (item.product.price * item.quantity), 0
    );
  };

  const handlePurchase = async () => {
    try {
        console.log("구매 시도 중...");  // 디버그 로그
        const response = await api.post('/cart/purchase/');
        
        console.log("서버 응답:", response.data);  // 응답 데이터 확인
        
        setModalConfig({
            isOpen: true,
            message: `${response.data.message}\n남은 마일리지: ${Number(response.data.remaining_mileage).toLocaleString()}원`,
            type: 'success',
            onClose: () => {
                setModalConfig(prev => ({ ...prev, isOpen: false }));
                fetchCartItems();
            }
        });
    } catch (err) {
        console.error("구매 오류:", err);  // 에러 로그
        console.error("에러 응답:", err.response?.data);  // 에러 응답 데이터
        console.error("에러 상태:", err.response?.status);  // 에러 상태 코드
        
        setModalConfig({
            isOpen: true,
            message: err.response?.data?.error || '구매 처리 중 오류가 발생했습니다.',
            type: 'error',
            onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
        });
    }
};
  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="cart-container">
      <h2>장바구니</h2>
      {cartItems.length === 0 ? (
        <p>장바구니가 비어있습니다.</p>
      ) : (
        <>
          <div className="cart-items">
            {cartItems.map(item => (
              <div key={item.id} className="cart-item">
                <div className="cart-item-image">
                  <SmartImage 
                    product={item.product} 
                    variant="list"
                    alt={item.product.title}
                  />
                </div>
                <div className="item-details">
                  <h3>{item.product.title}</h3>
                  <p className="price">
                    ₩{Number(item.product.price).toLocaleString()}
                  </p>
                </div>
                <div className="quantity-controls">
                  <button 
                    className="quantity-btn"
                    onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                    disabled={item.quantity <= 1}
                  >
                    －
                  </button>
                  <input
                    type="number"
                    min="1"
                    value={item.quantity}
                    onChange={(e) => {
                      const newQuantity = parseInt(e.target.value) || 1;
                      updateQuantity(item.product.id, newQuantity);
                    }}
                    className="quantity-input"
                  />
                  <button 
                    className="quantity-btn"
                    onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                  >
                    ＋
                  </button>
                </div>
                <p className="item-total">
                  ₩{Number(item.product.price * item.quantity).toLocaleString()}
                </p>
                <button 
                  className="remove-button"
                  onClick={() => removeFromCart(item.product.id)}
                >
                  삭제
                </button>
              </div>
            ))}
          </div>
          <div className="cart-summary">
            <h3>총 결제금액</h3>
            <div className="total-price">
              ₩{Number(calculateTotal()).toLocaleString()}
            </div>
            <button 
              className="checkout-button"
              onClick={handlePurchase}
            >
              구매하기
            </button>
          </div>
        </>
      )}
      <AlertModal {...modalConfig} />
    </div>
  );
}

export default Cart;