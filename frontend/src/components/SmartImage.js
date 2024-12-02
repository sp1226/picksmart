// src/components/SmartImage.js
import React, { useState } from 'react';
import ImageModal from './ImageModal';
import './SmartImage.css';

const SmartImage = ({ product, variant = 'full' }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 카테고리 매핑
  const getCategoryDisplay = (category) => {
    const categoryMap = {
      '1': '전자기기',
      '2': '패션잡화',
      '3': '화장품',
      '4': '도서',
      '5': '스포츠/레저',
      '6': '문구/취미'
    };
    return categoryMap[category] || category;  // 매핑된 카테고리명이 없으면 원래 값 반환
  };

  // 카테고리별 스타일 클래스 매핑
  const getCategoryClass = (category) => {
    const classMap = {
      'category1': 'electronics',
      'category2': 'fashion',
      'category3': 'cosmetics',
      'category4': 'books',
      'category5': 'sports',
      'category6': 'hobbies'
    };
    return classMap[category] || category;
  };

  const getImageUrl = () => {
    const baseUrl = 'http://localhost:8000';
    let url;

    switch (variant) {
      case 'list':
        url = product.list_thumbnail_url || product.thumbnail_url || product.image_url || product.image;
        break;
      case 'thumbnail':
        url = product.thumbnail_url || product.image_url || product.image;
        break;
      case 'full':
        url = product.image_url || product.image;
        break;
      default:
        url = product.image_url || product.image;
    }

    if (url && !url.startsWith('http')) {
      return `${baseUrl}${url}`;
    }
    return url;
  };

  const handleImageClick = (e) => {
    if (variant === 'full') {
      e.preventDefault();
      setIsModalOpen(true);
    }
  };

  const imageUrl = getImageUrl();
  
  if (!imageUrl) {
    return (
      <div className={`product-image-placeholder ${variant}`}>
        이미지 없음
      </div>
    );
  }

  const categoryDisplay = getCategoryDisplay(product.category);
  const categoryClass = getCategoryClass(product.category);

  return (
    <div className="smart-image-wrapper">
      <img
        src={imageUrl}
        alt={product.title}
        className={`product-image ${variant} ${variant === 'full' ? 'hover-zoom' : ''}`}
        loading="lazy"
        onClick={variant === 'full' ? handleImageClick : undefined}
        style={{ cursor: variant === 'full' ? 'zoom-in' : 'pointer' }}
        onError={(e) => {
          console.error('Image load error:', imageUrl);
          e.target.onerror = null;
          e.target.src = '/placeholder-image.png';
        }}
      />
      {product.category && (
        <div className="product-tag-container">
          <span className={`tag ${categoryClass}`}>
            {categoryDisplay}
          </span>
        </div>
      )}
      {variant === 'full' && (
        <ImageModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          imageUrl={imageUrl}
          title={product.title}
        />
      )}
    </div>
  );
};

export default SmartImage;