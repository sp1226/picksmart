/* App.js */

import React, { useEffect } from 'react';
import { fetchCSRFToken } from './utils/csrf';
import './App.css';

import Header from './components/Header';
import HeroBanner from './components/HeroBanner';
import RecommendList from './components/RecommendList';
import Footer from './components/Footer';
import ThemeList from './components/ThemeList';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SearchResults from './components/SearchResults'; 
import MyPage from './components/MyPage';
import ProductDetail from './components/ProductDetail';
import Cart from './components/Cart';
import ViewedProducts from './components/ViewedProducts';
import FavoriteProducts from './components/FavoriteProducts';
import ProductReviews from './components/ProductReviews';


const MainPage = () => (
  <>
    <div className="section">
      <RecommendList />
    </div>
    <div className="section">
      <ThemeList />
    </div>
  </>
);

function App() {
  useEffect(() => {
    fetchCSRFToken();
  }, []);

  return (
    <Router>
      <div className="App">
        <div className="header-wrapper">
          <div className="container">
            <Header />
          </div>
        </div>
        <div className="hero-banner">
          <HeroBanner />
        </div>
        <div className="container">
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/search" element={<SearchResults />} />
            <Route path="/mypage" element={<MyPage />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            {/* activity 라우트 수정 */}
            <Route path="/activity/viewed" element={<ViewedProducts />} />
            <Route path="/activity/favorites" element={<FavoriteProducts />} />
            <Route path="/activity/reviews" element={<ProductReviews />} />
            <Route path="/cart" element={<Cart />} />
          {/* ... 다른 라우트들 ... */}            {/* favorites 라우트 추가 */}
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
