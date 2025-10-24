import { Camera } from 'lucide-react';

export function PhotoUploadSection({ imageUrl, onUpload, label = 'Фото до доставки', isLoading = false }) {
  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file && onUpload) {
      onUpload(file);
    }
  };

  return (
    <div className="px-4 mb-6">
      <label htmlFor="photo-upload" className="cursor-pointer block">
        <div className="bg-violet-light h-[48px] rounded-full flex items-center gap-3 px-4">
          <div className="flex-shrink-0">
            <Camera size={20} className="text-gray-placeholder" />
          </div>
          <div className="flex-1">
            <p className="text-[16px] font-sans text-black">{label}</p>
            <p className="text-[13px] font-sans text-gray-placeholder">
              {isLoading ? 'Загрузка...' : imageUrl ? 'Загружено' : 'Не добавлено'}
            </p>
          </div>
        </div>
      </label>
      <input
        id="photo-upload"
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isLoading}
      />
      {imageUrl && (
        <div className="mt-3">
          <img
            src={imageUrl}
            alt={label}
            className="w-full h-40 object-cover rounded"
          />
        </div>
      )}
    </div>
  );
}

export default PhotoUploadSection;
