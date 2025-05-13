import styles from '@/styles/FighterImage.module.css';
import Image from 'next/image'; // Using Next.js Image component for optimization
import React from 'react';

interface FighterImageProps {
  fighterName: string; // To decide which image to show, e.g., "Core" or "Knots"
  imageUrl: string;
  altText: string;
}

const FighterImage: React.FC<FighterImageProps> = ({ fighterName, imageUrl, altText }) => {
  return (
    <div className={styles.fighterImageContainer}>
      <Image
        src={imageUrl}
        alt={altText}
        width={120} // Adjust base width as needed
        height={120} // Adjust base height as needed
        className={styles.fighterImage}
        priority // Preload if these are critical LCP elements
      />
    </div>
  );
};

export default FighterImage;
