
import { Route, Routes, Navigate } from "react-router-dom";
import ChatPage from "./pages/ChatPage";
import UploadPage from "./pages/UploadPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
