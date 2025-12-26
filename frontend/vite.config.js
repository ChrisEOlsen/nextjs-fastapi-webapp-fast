import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss()
  ],
  server: {
    host: '0.0.0.0', // Listen on all network interfaces
    hmr: {
      clientPort: 5173, // HMR client port
    },
    allowedHosts: ["template.crispychrisprivserver.org"], // Allow access from the specified domain
  },
})
