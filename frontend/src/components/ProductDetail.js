import React, { useEffect, useState, useCallback, memo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import api from '../api/axios';
import './ProductDetail.css';
import SmartImage from './SmartImage';
import AlertModal from './AlertModal';
import { ChevronRight, ChevronLeft } from 'lucide-react';

// Extracted Components
const StarRating = memo(({ rating }) => (
  <div className="review-rating" role="img" aria-label={`${rating}점`}>
    {[1, 2, 3, 4, 5].map((star) => (
      <span key={star} className={star <= rating ? 'filled' : 'empty'}>★</span>
    ))}
  </div>
));

const ReviewForm = memo(({ rating, comment, setRating, setComment, onSubmit, hasReviewed }) => (
  <form className="review-form" onSubmit={onSubmit}>
    <div className="rating-container">
      <span className="rating-label">평점을 선택해주세요</span>
      <div className="star-rating-input">
        {[5, 4, 3, 2, 1].map((star) => (
          <React.Fragment key={star}>
            <input
              type="radio"
              id={`star${star}`}
              name="rating"
              value={star}
              checked={rating === star}
              onChange={(e) => setRating(Number(e.target.value))}
              aria-label={`${star}점`}
            />
            <label htmlFor={`star${star}`} />
          </React.Fragment>
        ))}
      </div>
    </div>
    <textarea
      value={comment}
      onChange={(e) => setComment(e.target.value)}
      placeholder="이 상품에 대한 솔직한 리뷰를 남겨주세요."
      rows={4}
      aria-label="리뷰 내용"
    />
    <button type="submit" className={hasReviewed ? 'reviewed' : ''}>
      {hasReviewed ? '리뷰 수정하기' : '리뷰 등록하기'}
    </button>
  </form>
));

const ReviewList = memo(({ reviews }) => (
  <div className="reviews-list">
    {reviews.length === 0 ? (
      <div className="no-reviews">
        아직 작성된 리뷰가 없습니다.<br />
        첫 번째 리뷰를 작성해보세요!
      </div>
    ) : (
      reviews.map(review => (
        <div key={review.id} className="review-item">
          <div className="review-header">
            <span className="review-author">{review.user}</span>
            <StarRating rating={review.rating} />
            <span className="review-date">
              {new Date(review.created_at).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </span>
          </div>
          <p className="review-content">{review.content}</p>
        </div>
      ))
    )}
  </div>
));

const ProductNavigation = memo(({ prevId, nextId, onPrev, onNext }) => {
  return (
    <>
      {prevId && (
        <button 
          className="prev-product-button"
          onClick={onPrev}
          aria-label="이전 상품"
        >
          <ChevronLeft size={24} />
        </button>
      )}
      {nextId && (
        <button 
          className="next-product-button"
          onClick={onNext}
          aria-label="다음 상품"
        >
          <ChevronRight size={24} />
        </button>
      )}
    </>
  );
});

function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [isInCart, setIsInCart] = useState(false);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [cartError, setCartError] = useState(null);
  const [hasReviewed, setHasReviewed] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [reviews, setReviews] = useState([]);
  const [prevProductId, setPrevProductId] = useState(null);
  const [nextProductId, setNextProductId] = useState(null);
  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    message: '',
    onClose: () => {}
  });

  const showAlert = useCallback((message, callback, type = 'success') => {
    setModalConfig({
      isOpen: true,
      message,
      type,
      onClose: () => {
        setModalConfig(prev => ({ ...prev, isOpen: false }));
        if (callback) callback();
      }
    });
  }, []);

  const logInteraction = useCallback(async (type, duration = 0) => {
    try {
      await api.post(`/products/${id}/log_interaction/`, { type, duration });
    } catch (err) {
      console.error(`Failed to log ${type}:`, err);
    }
  }, [id]);

  const handleError = useCallback((err, defaultMessage) => {
    console.error('Error:', err);
    
    // 에러 응답의 데이터 구조를 더 자세히 확인
    const errorMsg = err.response?.data?.error || 
                    err.response?.data?.message || 
                    err.response?.data?.detail ||
                    defaultMessage;

    showAlert(errorMsg, null, 'error');
    
    // 인증 관련 에러 처리
    if (err.response?.status === 401) {
      showAlert('로그인이 필요한 서비스입니다.', () => {
        navigate('/');
      });
    }
  }, [navigate, showAlert]);

  const fetchProduct = useCallback(async () => {
    try {
      const response = await api.get(`/products/${id}/`);
      setProduct(response.data);
      setError(null);
    } catch (err) {
      handleError(err, '상품 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [id, handleError]);

  const fetchSurroundingProducts = useCallback(async () => {
    try {
      const response = await api.get('/products/recommendations/', {
        params: {
          current_id: id,
          limit: 2
        }
      });
      if (response.data && response.data.length > 0) {
        const products = response.data;
        const currentIndex = products.findIndex(p => p.id === parseInt(id));
        setPrevProductId(currentIndex > 0 ? products[currentIndex - 1].id : null);
        setNextProductId(currentIndex < products.length - 1 ? products[currentIndex + 1].id : null);
      }
    } catch (err) {
      console.error('상품 정보 조회 실패:', err);
    }
  }, [id]);

  const fetchReviews = useCallback(async () => {
    try {
      const response = await api.get(`/products/${id}/reviews/`);
      setReviews(response.data);
    } catch (err) {
      console.error('리뷰 로딩 실패:', err);
    }
  }, [id]);

  const checkExistingReview = useCallback(async () => {
    try {
      const response = await api.get(`/products/${id}/check_review/`);
      setHasReviewed(response.data.hasReview);
      if (response.data.hasReview) {
        setRating(response.data.review.rating);
        setComment(response.data.review.content);
      }
    } catch (err) {
      console.error('리뷰 확인 중 에러:', err);
    }
  }, [id]);

  const goToNextProduct = useCallback(() => {
    if (nextProductId) {
      navigate(`/product/${nextProductId}`);
    }
  }, [nextProductId, navigate]);

  const goToPrevProduct = useCallback(() => {
    if (prevProductId) {
      navigate(`/product/${prevProductId}`);
    }
  }, [prevProductId, navigate]);

  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'ArrowRight') {
        goToNextProduct();
      } else if (e.key === 'ArrowLeft') {
        goToPrevProduct();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [goToNextProduct, goToPrevProduct]);

  const handleFavoriteToggle = async (e) => {
    e.stopPropagation();
    await logInteraction('click');
    try {
      const response = await api.post(`/products/${id}/toggle_favorite/`);
      setIsFavorite(response.data.status === 'favorited');
      showAlert(response.data.message);
    } catch (err) {
      handleError(err, '찜하기 처리 중 오류가 발생했습니다.');
    }
  };

  const handleAddToCart = async () => {
    if (isAddingToCart || isInCart) return;

    try {
      setIsAddingToCart(true);
      setCartError(null);
      await api.post(`/cart/add_multiple/`, {
        productIds: [id]  // 상품 ID 배열로 전송
    });

      setIsInCart(true);
      showAlert('상품이 장바구니에 추가되었습니다.');
    } catch (err) {
      const errorMessage = err.response?.status === 401
        ? '로그인이 필요한 서비스입니다.'
        : err.response?.data?.error || '장바구니 추가 중 오류가 발생했습니다.';
      setCartError(errorMessage);
      handleError(err, errorMessage);
    } finally {
      setIsAddingToCart(false);
    }
  };



  const handleRemoveFromCart = async () => {
    try {
      const response = await api.delete(`/cart/${id}/remove_item/`);
      setIsInCart(false);
      showAlert('상품이 장바구니에서 제거되었습니다.', null, 'success');
    } catch (err) {
      const errorMessage = err.response?.status === 401
        ? '로그인이 필요한 서비스입니다.'
        : err.response?.data?.error || '장바구니에서 제거하는 중 오류가 발생했습니다.';
      setCartError(errorMessage);
      showAlert(errorMessage, null, 'error');
    }
  };


const checkCartStatus = useCallback(async () => {
  try {
      const response = await api.get(`/products/${id}/check_cart/`);
      setIsInCart(response.data.in_cart);
  } catch (err) {
      console.error('장바구니 상태 확인 실패:', err);
  }
}, [id]);  


useEffect(() => {
  fetchProduct();
  fetchSurroundingProducts();
  fetchReviews();
  checkExistingReview();
  checkCartStatus();  // 추가
}, [fetchProduct, fetchSurroundingProducts, fetchReviews, checkExistingReview, checkCartStatus]);


  const handleAddReview = async (e) => {
    e.preventDefault();
    await logInteraction('click');
    
    if (rating < 1 || rating > 5) {
      showAlert('1-5점 사이의 평점을 선택해주세요.');
      return;
    }
    
    if (!comment.trim()) {
      showAlert('리뷰 내용을 입력해주세요.');
      return;
    }
    
    try {
      await api.post(`/products/${id}/add_review/`, { 
        rating, 
        content: comment 
      });
      
      showAlert(
        hasReviewed ? '리뷰가 수정되었습니다.' : '리뷰가 등록되었습니다.',
        () => {
          checkExistingReview();
          fetchReviews();
        }
      );
    } catch (err) {
      handleError(err, '리뷰 등록 중 오류가 발생했습니다.');
    }
  };

  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>에러: {error}</div>;
  if (!product) return <div>상품을 찾을 수 없습니다.</div>;

  return (
    <div className="product-detail-container">
      <h2>{product.title}</h2>
      <div className="product-detail">
        <div className="product-image-container">
          <SmartImage 
            product={product} 
            variant="full" 
            alt={product.title}
          />
          <ProductNavigation 
            prevId={prevProductId}
            nextId={nextProductId}
            onPrev={goToPrevProduct}
            onNext={goToNextProduct}
          />
        </div>
        <div className="product-info">
          <p><strong>가격:</strong> ₩{Number(product.price).toLocaleString()}</p>
          <p><strong>테마:</strong> {product.theme}</p>
          <p><strong>카테고리:</strong> {product.category}</p>
          <p><strong>설명:</strong> {product.description}</p>
          <p><strong>재고:</strong> {product.stock}</p>
          <p><strong>평균 평점:</strong> {product.average_rating}</p>
          <p><strong>총 조회수:</strong> {product.total_views}</p>

          <button 
            className={`favorite-button ${isFavorite ? 'active' : ''}`}
            onClick={handleFavoriteToggle}
            aria-label={isFavorite ? '찜취소' : '찜하기'}
          >
            {isFavorite ? '찜취소' : '찜하기'}
          </button>

          <button 
            className={`cart-button ${isInCart ? 'in-cart' : ''} ${isAddingToCart ? 'loading' : ''}`}
            onClick={isInCart ? handleRemoveFromCart : handleAddToCart}
            disabled={isAddingToCart}
            aria-label={isAddingToCart ? '처리 중' : isInCart ? '장바구니에서 빼기' : '장바구니 담기'}
          >
            {isAddingToCart ? (
              <span className="loading-spinner" aria-hidden="true"></span>
            ) : isInCart ? (
              '장바구니에서 빼기'
            ) : (
              '장바구니 담기'
            )}
          </button>

          {cartError && (
            <div className="error-message" role="alert">
              {cartError}
            </div>
          )}
        </div>
      </div>

      <div className="reviews-container">
        <div className="review-form-section">
          <h3>리뷰 작성</h3>
          <ReviewForm
            rating={rating}
            comment={comment}
            setRating={setRating}
            setComment={setComment}
            onSubmit={handleAddReview}
            hasReviewed={hasReviewed}
          />
        </div>

        <div className="reviews-list-section">
          <h3>상품 리뷰</h3>
          <ReviewList reviews={reviews} />
        </div>

        <AlertModal 
          isOpen={modalConfig.isOpen}
          message={modalConfig.message}
          onClose={modalConfig.onClose}
          type={modalConfig.type || 'success'}
          aria-label={modalConfig.message}
        />
      </div>
    </div>
  );
}

StarRating.propTypes = {
  rating: PropTypes.number.isRequired,
};

ReviewForm.propTypes = {
  rating: PropTypes.number.isRequired,
  comment: PropTypes.string.isRequired,
  setRating: PropTypes.func.isRequired,
  setComment: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  hasReviewed: PropTypes.bool.isRequired,
};

ReviewList.propTypes = {
  reviews: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      user: PropTypes.string.isRequired,
      rating: PropTypes.number.isRequired,
      content: PropTypes.string.isRequired,
      created_at: PropTypes.string.isRequired,
    })
  ).isRequired,
};

ProductNavigation.propTypes = {
  prevId: PropTypes.number,
  nextId: PropTypes.number,
  onPrev: PropTypes.func.isRequired,
  onNext: PropTypes.func.isRequired
};

export default memo(ProductDetail);