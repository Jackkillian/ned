import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import process from "node:process";
import path from "node:path";
import checker from "vite-plugin-checker";
const host = process.env.TAURI_DEV_HOST;

export default defineConfig(() => ({
  plugins: [react(), checker({ typescript: true })],
  // 1. prevent Vite from obscuring rust errors
  clearScreen: false,
  // 2. tauri expects a fixed port, fail if that port is not available
  server: {
    port: 1420,
    strictPort: true,
    host: host || "127.0.0.1",
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 1421,
        }
      : undefined,
    watch: {
      // 3. tell Vite to ignore watching `src-tauri`
      ignored: ["**/src-tauri/**"],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
