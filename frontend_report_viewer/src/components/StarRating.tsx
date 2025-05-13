// src/components/StarRating.tsx
import styles from '@/styles/StarRating.module.css'; // We'll create this next
import React from 'react';

interface StarRatingProps {
  score: number | undefined; // Score out of 10
  maxStars?: number;
}

const StarRating: React.FC<StarRatingProps> = ({ score = 0, maxStars = 5 }) => {
  const normalizedScore = Math.max(0, Math.min(score, 10)); // Ensure score is 0-10
  const starsToFill = Math.round((normalizedScore / 10) * maxStars * 2) / 2; // Calculate half-stars

  const stars = [];
  for (let i = 1; i <= maxStars; i++) {
    if (i <= starsToFill) {
      stars.push(<span key={i} className={`${styles.star} ${styles.filled}`}>★</span>);
    } else if (i - 0.5 === starsToFill) {
      stars.push(<span key={i} className={`${styles.star} ${styles.halfFilled}`}>★</span>); // Or use a half-star icon
    } else {
      stars.push(<span key={i} className={`${styles.star} ${styles.empty}`}>☆</span>);
    }
  }

  return <div className={styles.starRatingContainer}>{stars}</div>;
};

export default StarRating;
