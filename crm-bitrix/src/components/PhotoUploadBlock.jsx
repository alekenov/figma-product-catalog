import { useState } from 'react';
import { Upload, X } from 'lucide-react';
import { uploadImages } from '../services/bitrix-upload';

export function PhotoUploadBlock({ photos = [], onChange, disabled = false }) {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const maxPhotos = 10;

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = [...e.dataTransfer.files];
    handleFiles(files);
  };

  const handleFileInput = (e) => {
    const files = [...e.target.files];
    handleFiles(files);
  };

  const handleFiles = async (files) => {
    if (uploading || disabled) return;
    if (photos.length >= maxPhotos) {
      alert(`Максимум ${maxPhotos} фото`);
      return;
    }

    try {
      setUploading(true);
      const filesToUpload = files.slice(0, maxPhotos - photos.length);
      const urls = await uploadImages(filesToUpload);
      onChange([...photos, ...urls]);
    } catch (error) {
      alert('Ошибка при загрузке фото: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const removePhoto = (index) => {
    onChange(photos.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-900">
        Фото букета
      </label>

      {/* Upload Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition ${
          dragActive
            ? 'border-purple-600 bg-purple-50'
            : 'border-gray-300 bg-gray-50'
        } ${disabled || uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileInput}
          disabled={uploading || disabled}
          className="absolute inset-0 opacity-0 cursor-pointer"
        />

        <div className="flex flex-col items-center gap-2">
          <Upload size={24} className="text-purple-600" />
          <div>
            <p className="text-sm font-medium text-gray-900">
              Загрузите фото или перетащите
            </p>
            <p className="text-xs text-gray-600">
              {photos.length}/{maxPhotos} фото
            </p>
          </div>
          {uploading && <p className="text-xs text-purple-600">Загрузка...</p>}
        </div>
      </div>

      {/* Photo Previews */}
      {photos.length > 0 && (
        <div className="grid grid-cols-4 gap-2">
          {photos.map((photo, index) => (
            <div key={index} className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 group">
              <img
                src={photo}
                alt={`Фото ${index + 1}`}
                className="w-full h-full object-cover"
              />
              <button
                type="button"
                onClick={() => removePhoto(index)}
                disabled={disabled}
                className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center"
              >
                <X size={20} className="text-white" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
