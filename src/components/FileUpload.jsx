import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, File, Image, FileText, AlertCircle } from 'lucide-react';

const FileUpload = ({ onFilesSelected, maxFiles = 3, maxSize = 20 * 1024 * 1024, className = '' }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [errors, setErrors] = useState([]);
  const fileInputRef = useRef(null);

  const supportedTypes = {
    'image/jpeg': { icon: Image, label: 'JPEG Image', color: 'text-green-600' },
    'image/png': { icon: Image, label: 'PNG Image', color: 'text-green-600' },
    'image/webp': { icon: Image, label: 'WebP Image', color: 'text-green-600' },
    'image/heic': { icon: Image, label: 'HEIC Image', color: 'text-green-600' },
    'image/heif': { icon: Image, label: 'HEIF Image', color: 'text-green-600' },
    'application/pdf': { icon: FileText, label: 'PDF Document', color: 'text-red-600' },
    'text/plain': { icon: FileText, label: 'Text Document', color: 'text-blue-600' },
    'text/markdown': { icon: FileText, label: 'Markdown Document', color: 'text-blue-600' }
  };

  const validateFile = (file) => {
    const errors = [];
    
    if (!supportedTypes[file.type]) {
      errors.push(`Unsupported file type: ${file.type}`);
    }
    
    if (file.size > maxSize) {
      errors.push(`File size exceeds ${Math.round(maxSize / (1024 * 1024))}MB limit`);
    }
    
    return errors;
  };

  const handleFiles = (files) => {
    const fileArray = Array.from(files);
    const newErrors = [];
    const validFiles = [];

    if (selectedFiles.length + fileArray.length > maxFiles) {
      newErrors.push(`Maximum ${maxFiles} files allowed`);
      setErrors(newErrors);
      return;
    }

    fileArray.forEach((file, index) => {
      const fileErrors = validateFile(file);
      if (fileErrors.length > 0) {
        newErrors.push(`${file.name}: ${fileErrors.join(', ')}`);
      } else {
        validFiles.push({
          id: `${Date.now()}-${index}`,
          file,
          name: file.name,
          size: file.size,
          type: file.type,
          preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null
        });
      }
    });

    if (newErrors.length > 0) {
      setErrors(newErrors);
    } else {
      setErrors([]);
    }

    if (validFiles.length > 0) {
      const updatedFiles = [...selectedFiles, ...validFiles];
      setSelectedFiles(updatedFiles);
      onFilesSelected(updatedFiles.map(f => f.file));
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (fileId) => {
    const updatedFiles = selectedFiles.filter(f => f.id !== fileId);
    setSelectedFiles(updatedFiles);
    onFilesSelected(updatedFiles.map(f => f.file));
    
    // Clean up preview URLs
    const removedFile = selectedFiles.find(f => f.id === fileId);
    if (removedFile && removedFile.preview) {
      URL.revokeObjectURL(removedFile.preview);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    const fileType = supportedTypes[type];
    if (fileType) {
      const IconComponent = fileType.icon;
      return <IconComponent className={`w-8 h-8 ${fileType.color}`} />;
    }
    return <File className="w-8 h-8 text-gray-600" />;
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Upload Area */}
      <motion.div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.webp,.heic,.heif,.pdf,.txt,.md"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-900 mb-2">
          Drop files here or click to upload
        </p>
        <p className="text-sm text-gray-500">
          Support for images (JPEG, PNG, WebP, HEIC), PDF documents, and text files
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Max {maxFiles} files, {Math.round(maxSize / (1024 * 1024))}MB each
        </p>
      </motion.div>

      {/* Error Messages */}
      <AnimatePresence>
        {errors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md"
          >
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-sm text-red-700">
                <ul className="list-disc list-inside space-y-1">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Selected Files */}
      <AnimatePresence>
        {selectedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 space-y-2"
          >
            <h4 className="text-sm font-medium text-gray-900">
              Selected Files ({selectedFiles.length}/{maxFiles})
            </h4>
            {selectedFiles.map((fileData) => (
              <motion.div
                key={fileData.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center p-3 bg-gray-50 rounded-lg border"
              >
                {fileData.preview ? (
                  <img
                    src={fileData.preview}
                    alt={fileData.name}
                    className="w-12 h-12 object-cover rounded-md mr-3"
                  />
                ) : (
                  <div className="w-12 h-12 flex items-center justify-center mr-3">
                    {getFileIcon(fileData.type)}
                  </div>
                )}
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {fileData.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(fileData.size)} • {supportedTypes[fileData.type]?.label || 'Unknown'}
                  </p>
                </div>
                
                <button
                  onClick={() => removeFile(fileData.id)}
                  className="ml-3 p-1 text-gray-400 hover:text-red-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUpload;
