import { useState } from "react";
import { Sidebar } from "../components/Sidebar";
import { Link } from "react-router-dom";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setStatus("Uploading...");
    try {
      const form = new FormData();
      form.append("file", file);
      const response = await fetch("/api/documents", { 
        method: "POST", 
        body: form 
      });
      
      if (response.ok) {
        setStatus("Uploaded successfully!");
        setFile(null);
        // Reset file input
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setStatus("Upload failed. Please try again.");
      }
    } catch (error) {
      setStatus("Upload failed. Please try again.");
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar>
        <h2 className="font-semibold mb-4">RAG Chat</h2>
        <nav className="flex flex-col gap-2">
          <Link to="/" className="px-3 py-2 rounded hover:bg-gray-100 text-gray-700">
            Chat
          </Link>
          <Link to="/upload" className="px-3 py-2 rounded bg-blue-100 text-blue-700 font-medium">
            Upload Documents
          </Link>
        </nav>
      </Sidebar>

      <main className="flex flex-col flex-1">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 md:pl-4 pl-16">
          <h1 className="text-xl font-semibold text-gray-800">Upload Documents</h1>
        </div>

        {/* Upload Form */}
        <div className="flex-1 bg-white p-8">
          <div className="max-w-2xl mx-auto">
            <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Upload Document to RAG Database
                  </h3>
                  <p className="text-gray-600">
                    Upload PDF, TXT, or DOCX files to add them to your knowledge base
                  </p>
                </div>
                
                <input
                  type="file"
                  accept=".pdf,.txt,.docx"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                
                {file && (
                  <div className="text-sm text-gray-600">
                    Selected: <span className="font-medium">{file.name}</span>
                  </div>
                )}
                
                <button
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={handleUpload}
                  disabled={!file || status === "Uploading..."}
                >
                  {status === "Uploading..." ? "Uploading..." : "Upload Document"}
                </button>
                
                {status && status !== "Uploading..." && (
                  <div className={`text-sm font-medium ${
                    status.includes("success") ? "text-green-600" : "text-red-600"
                  }`}>
                    {status}
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-6 text-sm text-gray-500">
              <h4 className="font-medium mb-2">Supported file types:</h4>
              <ul className="list-disc list-inside space-y-1">
                <li>PDF files (.pdf)</li>
                <li>Text files (.txt)</li>
                <li>Word documents (.docx)</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
