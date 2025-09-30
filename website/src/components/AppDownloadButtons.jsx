import React from 'react';
import { AppStoreButton, GooglePlayButton } from '../assets/icons/SocialIcons';

/**
 * App Download Buttons Component
 * Displays App Store and Google Play download buttons
 */
export default function AppDownloadButtons() {
  return (
    <div className="flex gap-2 w-full">
      <a
        href="#"
        className="flex-1 transition-opacity hover:opacity-80 active:opacity-60"
        aria-label="Download on the App Store"
      >
        <AppStoreButton className="h-10 w-full" />
      </a>
      <a
        href="#"
        className="flex-1 transition-opacity hover:opacity-80 active:opacity-60"
        aria-label="Get it on Google Play"
      >
        <GooglePlayButton className="h-10 w-full" />
      </a>
    </div>
  );
}