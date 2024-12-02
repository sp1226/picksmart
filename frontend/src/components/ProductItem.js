// ProductItem.js 수정
import React from 'react';
import { Link } from 'react-router-dom';
import './ProductItem.css';


function ProductItem({ product }) {
  return (
    <Link to={`/product/${product.id}`} className="product-item-link">
      <div className="product-item">
        <img 
          src={`http://localhost:8000${product.image_url}`}
          alt={product.title}
        />
        <p>₩{Number(product.price).toLocaleString()}원</p>
      </div>
    </Link>
  );
}


export default ProductItem;