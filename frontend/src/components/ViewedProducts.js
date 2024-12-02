// ViewedProducts.js
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import SmartImage from './SmartImage';
import AlertModal from './AlertModal';
import { ShoppingCart, X } from 'lucide-react';
import ProductActions from './common/ProductActions';



function ViewedProducts() {
  const [products, setProducts] = useState([]); // 초기값을 빈 배열로 설정
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    message: '',
    type: 'success'
  });
  
  const navigate = useNavigate();
  const observer = useRef();

  const removeFromViewed = async (productId) => {
    try {
      // 최근 본 상품 삭제 API 호출
      await api.delete(`/products/user-activity/viewed/${productId}/`);
      setProducts(products.filter(p => p.id !== productId));
      setModalConfig({
        isOpen: true,
        message: '최근 본 상품에서 삭제되었습니다.',
        type: 'success',
        onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
      });
    } catch (err) {
      setModalConfig({
        isOpen: true,
        message: '삭제에 실패했습니다.',
        type: 'error',
        onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
      });
    }
  };

  const fetchProducts = useCallback(async (pageNum) => {
    try {
      const response = await api.get('/user-activity/viewed/', {
        params: { page: pageNum, page_size: 12 }
      });

      // response.data가 undefined일 수 있으므로 안전하게 처리
      const results = response.data?.results || [];
      const next = response.data?.next || false;

      setProducts(prev => pageNum === 1 ? results : [...prev, ...results]);
      setHasMore(!!next);
      setError(null);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('최근 본 상품을 불러오는데 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const lastElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1);
      }
    }, { rootMargin: '100px' });

    if (node) observer.current.observe(node);
  }, [loading, hasMore]);

  useEffect(() => {
    fetchProducts(page);
  }, [page, fetchProducts]);

  const sendToCart = async () => {
    try {
      await api.post('/cart/add_multiple/', {
        productIds: selectedProducts
      });
      
      setModalConfig({
        isOpen: true,
        message: '선택한 상품이 장바구니에 추가되었습니다.',
        type: 'success',
        onClose: () => {
          setModalConfig(prev => ({ ...prev, isOpen: false }));
          setSelectedProducts([]);
        }
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

  const toggleSelection = (productId) => {
    setSelectedProducts(prev =>
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  if (loading) return <div className="loading">로딩 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="activity-list-container">
      <h2>최근 본 상품</h2>
      {products.length === 0 ? (
        <p className="empty-message">최근 본 상품이 없습니다.</p>
      ) : (
        <div className="products-grid">
          {products.map((product) => (
            <div key={product.id} className="product-card">
              <ProductActions 
                onAddToCart={() => sendToCart(product.id)}
                onRemove={() => removeFromViewed(product.id)}
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


export default ViewedProducts;
