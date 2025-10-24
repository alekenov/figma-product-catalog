/**
 * Bitrix file upload service
 * Handles image and video uploads to production Bitrix API
 */

const BITRIX_API_BASE = 'https://cvety.kz/api/v2';
const UPLOAD_TOKEN = 'ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144';

/**
 * Upload multiple images
 * @param {File[]} files - Array of image files
 * @returns {Promise<string[]>} - Array of image URLs
 */
export async function uploadImages(files) {
  try {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('images[]', file);
    });

    const response = await fetch(`${BITRIX_API_BASE}/uploads/images/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${UPLOAD_TOKEN}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error?.message || 'Upload failed');
    }

    return data.data?.urls || [];
  } catch (error) {
    console.error('Image upload error:', error);
    throw error;
  }
}

/**
 * Upload single video
 * @param {File} file - Video file
 * @returns {Promise<string>} - Video URL
 */
export async function uploadVideo(file) {
  try {
    const formData = new FormData();
    formData.append('video', file);

    const response = await fetch(`${BITRIX_API_BASE}/uploads/videos/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${UPLOAD_TOKEN}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error?.message || 'Upload failed');
    }

    return data.data?.url || '';
  } catch (error) {
    console.error('Video upload error:', error);
    throw error;
  }
}
