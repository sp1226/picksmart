// HeroBanner.js
import React from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import './HeroBanner.css';

const banners = [
  {
    id: 1,
    image: '/assets/banner-1.png',
  },
  {
    id: 2,
    image: '/assets/banner-2.png',
  },
  {
    id: 3,
    image: '/assets/banner-3.png',
  },
  {
    id: 4,
    image: '/assets/banner-4.png',
  },
  {
    id: 5,
    image: '/assets/banner-5.png',
  },
  {
    id: 6,
    image: '/assets/banner-6.png',
  },
  {
    id: 7,
    image: '/assets/banner-7.png',
  },
];

function HeroBanner() {
  return (
    <div className="hero-banner">
      <Swiper
        modules={[Pagination, Autoplay]}
        spaceBetween={30}
        slidesPerView={1.5}
        centeredSlides={true}
        loop={true}
        autoplay={{
          delay: 3000,
          disableOnInteraction: false,
        }}
        pagination={{ 
          clickable: true,
          dynamicBullets: true,
          dynamicMainBullets: 5
        }}
        allowTouchMove={true}
        slideToClickedSlide={true}
        watchSlidesProgress={true}
        className="banner-swiper"
      >
        {banners.map((banner) => (
          <SwiperSlide key={banner.id}>
            <div className="hero-slide">
              <img 
                src={banner.image} 
                alt={banner.title}
                className="banner-image"
              />
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
}

export default HeroBanner;