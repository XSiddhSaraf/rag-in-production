'use client';

import { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function FileUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true);
        } else if (e.type === 'dragleave') {
            setIsDragging(false);
        }
    }, []);

    const validateFile = (file: File): string | null => {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        const maxSize = 50 * 1024 * 1024; // 50MB

        if (!allowedTypes.includes(file.type)) {
            return 'Invalid file type. Please upload a PDF or Word document.';
        }

        if (file.size > maxSize) {
            return 'File too large. Maximum size is 50MB.';
        }

        return null;
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        setError(null);

        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            const validationError = validateFile(droppedFile);
            if (validationError) {
                setError(validationError);
            } else {
                setFile(droppedFile);
            }
        }
    }, []);

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        setError(null);
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            const validationError = validateFile(selectedFile);
            if (validationError) {
                setError(validationError);
            } else {
                setFile(selectedFile);
            }
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setError(null);

        try {
            const response = await apiClient.uploadDocument(file);
            // Redirect to dashboard
            router.push(`/dashboard/${response.job_id}`);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Upload failed. Please try again.');
            setIsUploading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto">
            {/* Drop zone */}
            <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`
          relative border-2 border-dashed rounded-xl p-12 transition-all duration-300
          ${isDragging ? 'border-primary-500 bg-primary-50 scale-105' : 'border-gray-300 bg-white'}
          ${file ? 'border-success-500 bg-success-50' : ''}
          hover:border-primary-400 hover:bg-primary-50/50 cursor-pointer
        `}
            >
                <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileInput}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={isUploading}
                />

                <div className="text-center">
                    {file ? (
                        <CheckCircle className="mx-auto h-16 w-16 text-success-500 mb-4" />
                    ) : (
                        <Upload className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                    )}

                    {file ? (
                        <>
                            <div className="flex items-center justify-center gap-2 mb-2">
                                <FileText className="h-5 w-5 text-success-600" />
                                <p className="text-lg font-semibold text-success-700">{file.name}</p>
                            </div>
                            <p className="text-sm text-gray-500 mb-4">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setFile(null);
                                }}
                                className="text-sm text-primary-600 hover:text-primary-700 underline"
                            >
                                Choose different file
                            </button>
                        </>
                    ) : (
                        <>
                            <p className="text-xl font-semibold text-gray-700 mb-2">
                                Drop your technical document here
                            </p>
                            <p className="text-sm text-gray-500 mb-4">
                                or click to browse
                            </p>
                            <p className="text-xs text-gray-400">
                                Supported formats: PDF, Word (DOC, DOCX) • Max size: 50MB
                            </p>
                        </>
                    )}
                </div>
            </div>

            {/* Error message */}
            {error && (
                <div className="mt-4 p-4 bg-danger-50 border border-danger-200 rounded-lg flex items-start gap-3 animate-fade-in">
                    <AlertCircle className="h-5 w-5 text-danger-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-danger-700">{error}</p>
                </div>
            )}

            {/* Upload button */}
            {file && !error && (
                <button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className={`
            mt-6 w-full py-4 px-6 rounded-xl font-semibold text-white
            transition-all duration-300 transform
            ${isUploading
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 hover:scale-105 hover:shadow-lg'
                        }
          `}
                >
                    {isUploading ? (
                        <span className="flex items-center justify-center gap-2">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                            Uploading and analyzing...
                        </span>
                    ) : (
                        'Analyze Document'
                    )}
                </button>
            )}
        </div>
    );
}
