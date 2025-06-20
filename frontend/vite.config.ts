
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward backend calls during dev
      "/chat": "http://localhost:8080",
      "/documents": "http://localhost:8080"
    }
  }
});
