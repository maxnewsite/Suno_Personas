'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function UploadForm() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (selectedFile: File) => {
    setError(null);

    // Validate file type
    if (!selectedFile.name.endsWith('.mp3')) {
      setError('Please upload an MP3 file');
      return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setError('File too large. Maximum size is 10MB');
      return;
    }

    setFile(selectedFile);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const response = await apiClient.uploadFile(file);
      // Redirect to results page
      router.push(`/results/${response.job_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
          dragActive
            ? 'border-primary-400 bg-primary-400/10'
            : 'border-gray-600 hover:border-gray-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".mp3"
          onChange={handleFileInput}
          className="hidden"
          id="file-upload"
          disabled={uploading}
        />

        {!file ? (
          <div className="space-y-4">
            <div className="text-6xl">🎵</div>
            <div>
              <p className="text-xl text-white font-medium mb-2">
                Drop your MP3 file here
              </p>
              <p className="text-gray-400 mb-4">or</p>
              <label
                htmlFor="file-upload"
                className="inline-block px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg cursor-pointer transition-colors"
              >
                Browse Files
              </label>
            </div>
            <p className="text-sm text-gray-500">
              Maximum file size: 10MB • MP3 format only
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-4xl">✓</div>
            <div>
              <p className="text-lg text-white font-medium">{file.name}</p>
              <p className="text-sm text-gray-400">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <div className="flex gap-3 justify-center">
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="px-8 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
              >
                {uploading ? 'Uploading...' : 'Analyze Track'}
              </button>
              <label
                htmlFor="file-upload"
                className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg cursor-pointer transition-colors"
              >
                Change File
              </label>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {uploading && (
        <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/50 rounded-lg">
          <p className="text-blue-400">Uploading and starting analysis...</p>
        </div>
      )}
    </div>
  );
}
