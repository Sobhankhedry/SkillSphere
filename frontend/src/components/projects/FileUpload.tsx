"use client";

import { useState, useRef } from "react";
import { Upload, FileText, Archive, Image as ImageIcon, Download } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { projectsAPI } from "@/lib/api";
import { ProjectFile } from "@/types";

interface FileUploadProps {
  projectId: string;
  files: ProjectFile[];
  onFilesUpdate: (files: ProjectFile[]) => void;
  canUpload: boolean;
}

export function FileUpload({ projectId, files, onFilesUpdate, canUpload }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      console.log("[FileUpload] Starting upload:", {
        projectId,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
      });

      const { data } = await projectsAPI.uploadFile(projectId, formData);
      console.log("[FileUpload] Upload successful:", data);
      onFilesUpdate([...files, data]);
    } catch (err: any) {
      console.error("[FileUpload] Upload failed:", {
        message: err.message,
        name: err.name,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        headers: err.response?.headers,
        requestURL: err.config?.url,
        requestMethod: err.config?.method,
        requestData: err.config?.data,
        requestHeaders: err.config?.headers,
        code: err.code,
        stack: err.stack,
      });
      alert(`Failed to upload file: ${err.response?.status || err.message}`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDownload = async (fileId: string) => {
    try {
      const { data } = await projectsAPI.downloadFile(projectId, fileId);
      const url = window.URL.createObjectURL(data);
      const a = document.createElement("a");
      const file = files.find((f) => f.id === fileId);
      a.href = url;
      a.download = file?.original_filename || "download";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error("[FileUpload] Download failed:", {
        message: err.message,
        status: err.response?.status,
        data: err.response?.data,
        code: err.code,
      });
      alert(`Download failed: ${err.response?.status || err.message}`);
    }
  };

  const fileIcon = (type: string) => {
    switch (type) {
      case "pdf": return <FileText size={18} className="text-red-500" />;
      case "zip": return <Archive size={18} className="text-yellow-500" />;
      default: return <ImageIcon size={18} className="text-green-500" />;
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      {canUpload && (
        <div>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleUpload}
            accept=".pdf,.zip,.jpg,.jpeg,.png,.gif,.webp"
            className="hidden"
          />
          <Button
            variant="secondary"
            size="sm"
            loading={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={16} className="mr-2" />
            Upload File
          </Button>
          <p className="text-xs text-gray-500 mt-1">PDF, ZIP, or images up to 50MB</p>
        </div>
      )}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file) => (
            <div
              key={file.id}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <div className="flex items-center gap-3">
                {fileIcon(file.file_type)}
                <div>
                  <p className="text-sm font-medium">{file.original_filename}</p>
                  <p className="text-xs text-gray-500">
                    {formatSize(file.file_size)} &middot; {file.uploaded_by}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDownload(file.id)}
                className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg"
              >
                <Download size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
      {files.length === 0 && (
        <p className="text-sm text-gray-500">No files uploaded yet.</p>
      )}
    </div>
  );
}
