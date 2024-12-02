// src/components/MyPage.js
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js'; // Import necessary Chart.js components
import { 
  Eye, Heart, ShoppingCart, Star, User, Clock, 
  ShoppingBag, TrendingUp 
} from 'lucide-react';
import api from '../api/axios';
import './MyPage.css';

// Chart components for other analytics
import {
  TimePatternChart,
  InteractionChart,
  RatingAnalysisChart,
  PurchasePatternChart,
} from './charts/ChartComponents';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);


// Loading component
const LoadingSpinner = () => (
  <div className="loading-spinner">
    <div className="spinner" />
    <p>데이터를 불러오는 중...</p>
  </div>
);

// Error message component
const ErrorMessage = ({ message, onRetry }) => (
  <div className="error-message">
    <p>{message}</p>
    {onRetry && <button onClick={onRetry}>다시 시도</button>}
  </div>
);

// Stat card component
const StatCard = ({ type, icon, label, value, onClick }) => (
  <div 
    className="stat-card" 
    onClick={onClick}
    role="listitem"
    tabIndex={0}
    onKeyPress={(e) => e.key === 'Enter' && onClick()}
  >
    <div className="stat-icon">{icon}</div>
    <div className="stat-value">{value || 0}</div>
    <div className="stat-label">{label}</div>
  </div>
);

// Analytics section for other stats
const AnalyticsSection = () => {
  const [analytics, setAnalytics] = useState({
    timePatterns: [],
    interactionStats: [],
    ratingAnalysis: [],
    purchasePatterns: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/accounts/analytics/');
        setAnalytics(response.data);
        setError(null);
      } catch (err) {
        setError('분석 데이터를 불러오는데 실패했습니다.');
        console.error('Analytics fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="analytics-container">
      {/* Time Pattern Chart */}
      <div className="analytics-section">
        <div className="section-header">
          <Clock size={24} />
          <h3>시간대별 쇼핑 패턴</h3>
        </div>
        <div style={{ height: 300 }}>
          <TimePatternChart data={analytics.timePatterns} />
        </div>
      </div>

      {/* Interaction Chart */}
      <div className="analytics-section">
        <div className="section-header">
          <ShoppingBag size={24} />
          <h3>상품 상호작용 분석</h3>
        </div>
        <div style={{ height: 300 }}>
          <InteractionChart data={analytics.interactionStats} />
        </div>
      </div>

      {/* Rating Analysis Chart */}
      <div className="analytics-section">
        <div className="section-header">
          <Star size={24} />
          <h3>카테고리별 평점 분석</h3>
        </div>
        <div style={{ height: 300 }}>
          <RatingAnalysisChart data={analytics.ratingAnalysis} />
        </div>
      </div>

      {/* Purchase Pattern Chart */}
      <div className="analytics-section">
        <div className="section-header">
          <TrendingUp size={24} />
          <h3>월별 구매 패턴</h3>
        </div>
        <div style={{ height: 300 }}>
          <PurchasePatternChart data={analytics.purchasePatterns} />
        </div>
      </div>
    </div>
  );
};

// Main MyPage component
const MyPage = () => {
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState(null);
  const [activityStats, setActivityStats] = useState(null);
  const [categoryPreferences, setCategoryPreferences] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchUserData = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/accounts/profile/');
      
      if (!response.data.is_authenticated) {
        navigate('/');
        return;
      }

      const { user, activity_stats, category_preferences } = response.data;
      setUserInfo(user);
      setActivityStats(activity_stats);
      setCategoryPreferences(category_preferences);
      setLastUpdated(new Date().toISOString());
      setError(null);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
      console.error('Profile fetch error:', err);
      if (err.response?.status === 401) {
        setTimeout(() => navigate('/'), 2000);
      }
    } finally {
      setIsLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchUserData} />;
  if (!userInfo) return <ErrorMessage message="사용자 정보를 찾을 수 없습니다." />;

  return (
    <div className="mypage-container">
      {/* Profile Header */}
      <div className="profile-header">
        <div className="profile-header-content">
          <div className="profile-avatar">
            <User size={40} />
          </div>
          <div className="profile-info">
            <h1>{userInfo.username}</h1>
            <p className="user-mileage">
              보유 마일리지: ₩{Number(userInfo.mileage).toLocaleString()}
            </p>
            {lastUpdated && (
              <small>
                마지막 업데이트: {new Date(lastUpdated).toLocaleString()}
              </small>
            )}
          </div>
        </div>
      </div>

      {/* Activity Stats */}
      <div className="stats-grid">
  <StatCard 
    type="viewed"
    icon={<Eye size={24} />}
    label="상품 조회"
    value={activityStats?.total_views}
    onClick={() => navigate('/activity/viewed')}  // 경로 수정
  />
  <StatCard 
    type="favorites"
    icon={<Heart size={24} />}
    label="찜한 상품"
    value={activityStats?.favorite_count}
    onClick={() => navigate('/activity/favorites')}  // 경로 수정
  />
  <StatCard 
    type="cart"
    icon={<ShoppingCart size={24} />}
    label="장바구니"
    value={activityStats?.cart_count}
    onClick={() => navigate('/cart')}
  />
  <StatCard 
    type="reviews"
    icon={<Star size={24} />}
    label="상품 리뷰"
    value={activityStats?.review_count}
    onClick={() => navigate('/activity/reviews')}  // 경로 수정
  />
</div>


      {/* Category Preferences */}
      <div className="category-preferences-section">
        <div className="section-header">
          <ShoppingBag size={24} />
          <h3>카테고리별 선호도</h3>
        </div>
        {categoryPreferences.length > 0 ? (
          <div style={{ height: 300 }}>
            <Bar
              data={{
                labels: categoryPreferences.map((pref) => pref.category),
                datasets: [
                  {
                    label: '선호도 비율',
                    data: categoryPreferences.map((pref) => pref.score),
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: (value) => `${value}%`,
                    },
                  },
                },
                plugins: {
                  tooltip: {
                    callbacks: {
                      label: (context) => `${context.raw}%`,
                    },
                  },
                },
              }}
            />
          </div>
        ) : (
          <p>데이터 없음</p>
        )}
      </div>

      {/* Analytics Section */}
      <AnalyticsSection />
    </div>
  );
};

export default React.memo(MyPage);
