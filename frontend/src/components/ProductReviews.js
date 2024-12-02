import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import SmartImage from './SmartImage';
import AlertModal from './AlertModal';
import ProductActions from './common/ProductActions';

function ProductReviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    message: '',
    type: 'success'
  });

  const navigate = useNavigate();

  const removeReview = async (reviewId) => {
    try {
      await api.delete(`/products/user-activity/reviews/${reviewId}/`);
      setReviews(reviews.filter(r => r.id !== reviewId));
      setModalConfig({
        isOpen: true,
        message: '리뷰가 삭제되었습니다.',
        type: 'success',
        onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
      });
    } catch (err) {
      setModalConfig({
        isOpen: true,
        message: '리뷰 삭제에 실패했습니다.',
        type: 'error',
        onClose: () => setModalConfig(prev => ({ ...prev, isOpen: false }))
      });
    }
  };

  const fetchReviews = useCallback(async (pageNum) => {
    try {
      const response = await api.get('/user-activity/reviews/', {
        params: { page: pageNum, page_size: 12 }
      });

      const { results, next } = response.data;
      setReviews(prev => pageNum === 1 ? results : [...prev, ...results]);
      setHasMore(!!next);
      setError(null);
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('리뷰를 불러오는데 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate, setHasMore]);

  useEffect(() => {
    fetchReviews(page);
  }, [page, fetchReviews]);

  const StarRating = ({ rating }) => (
    <div className="star-rating">
      {[1, 2, 3, 4, 5].map(star => (
        <span key={star} className={star <= rating ? 'filled' : ''}>
          ★
        </span>
      ))}
    </div>
  );

  if (loading && page === 1) return <div className="loading">로딩 중...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="product-reviews-container">
      <h2>내가 작성한 리뷰</h2>
      {reviews.length === 0 ? (
        <p className="empty-message">작성한 리뷰가 없습니다.</p>
      ) : (
        <div className="reviews-grid">
          {reviews.map(review => (
            <div key={review.id} className="product-card">
              <ProductActions 
                onRemove={() => removeReview(review.id)}
                showCartButton={false} // 장바구니 버튼 숨김
              />
              <div onClick={() => navigate(`/product/${review.product.id}`)}>
                <SmartImage product={review.product} variant="list" />
                <div className="review-info">
                  <h3>{review.product.title}</h3>
                  <StarRating rating={review.rating} />
                  <p className="review-content">{review.content}</p>
                  <p className="review-date">
                    {new Date(review.created_at).toLocaleDateString()}
                  </p>
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

export default ProductReviews;