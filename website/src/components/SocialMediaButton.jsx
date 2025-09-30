import React from 'react';
import { FacebookIcon, YouTubeIcon, InstagramIcon, VKIcon } from '../assets/icons/SocialIcons';

/**
 * Social Media Button Component
 * Renders a social media icon with hover effect
 *
 * @param {string} type - Social media type: 'facebook', 'youtube', 'instagram', 'vk'
 * @param {string} href - Link URL
 * @param {string} ariaLabel - Accessible label for screen readers
 */
export default function SocialMediaButton({ type, href = '#', ariaLabel }) {
  const icons = {
    facebook: FacebookIcon,
    youtube: YouTubeIcon,
    instagram: InstagramIcon,
    vk: VKIcon
  };

  const IconComponent = icons[type];

  if (!IconComponent) {
    console.warn(`Unknown social media type: ${type}`);
    return null;
  }

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={ariaLabel || type}
      className="relative block shrink-0 transition-transform hover:scale-110 active:scale-95"
    >
      <IconComponent className="w-6 h-6" />
    </a>
  );
}