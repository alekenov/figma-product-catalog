import { useState } from 'react';
import { Upload, X } from 'lucide-react';
import { uploadVideo } from '../services/bitrix-upload';

export function VideoUploadBlock({ video = null, onChange, disabled = false }) {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

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
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files?.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    if (uploading || disabled) return;

    try {
      setUploading(true);
      const url = await uploadVideo(file);
      onChange(url);
    } catch (error) {
      alert('Ошибка при загрузке видео: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const removeVideo = () => {
    onChange(null);
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-900">
        Видео букета
      </label>

      {/* Upload Zone or Video Preview */}
      {!video ? (
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
            accept="video/*"
            onChange={handleFileInput}
            disabled={uploading || disabled}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />

          <div className="flex flex-col items-center gap-2">
            <Upload size={24} className="text-purple-600" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                Загрузите видео или перетащите
              </p>
              <p className="text-xs text-gray-600">MP4, WebM, Ogg</p>
            </div>
            {uploading && <p className="text-xs text-purple-600">Загрузка...</p>}
          </div>
        </div>
      ) : (
        <div className="relative rounded-lg overflow-hidden bg-gray-900 aspect-video flex items-center justify-center group">
          <video
            src={video}
            className="w-full h-full object-cover"
            controls
          />
          <button
            type="button"
            onClick={removeVideo}
            disabled={disabled}
            className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white rounded-full p-1 transition"
          >
            <X size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
