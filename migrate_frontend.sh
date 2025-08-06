#!/bin/bash

# Скрипт для переноса frontend из исходного проекта в новую структуру

echo "🚀 Migrating frontend to new structure..."

# Создание папки frontend если не существует
mkdir -p frontend

# Копирование файлов из client/ в frontend/
if [ -d "client" ]; then
    echo "📁 Copying client files to frontend..."
    
    # Копируем содержимое client в frontend
    cp -r client/* frontend/ 2>/dev/null || true
    cp client/.* frontend/ 2>/dev/null || true
    
    echo "✅ Files copied successfully"
else
    echo "⚠️  client/ directory not found, creating minimal frontend structure"
    
    # Создаем минимальную структуру если client не существует
    mkdir -p frontend/src/{components,pages,lib,hooks}
    mkdir -p frontend/public
    
    # Создаем базовые файлы
    cat > frontend/package.json << 'EOF'
{
  "name": "onlinesim-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.2",
    "typescript": "5.6.3",
    "vite": "^5.4.19"
  }
}
EOF

    # Создаем базовый vite.config.ts
    cat > frontend/vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0'
  }
})
EOF
fi

# Обновление путей в конфигурациях
echo "🔧 Updating configuration files..."

# Создание .env файлов для frontend
cat > frontend/.env.example << 'EOF'
VITE_API_URL=http://localhost:8000/api
VITE_SSE_URL=http://localhost:8000/api/events
VITE_WEBAPP_URL=http://localhost
EOF

# Копируем в .env.local для разработки
cp frontend/.env.example frontend/.env.local

# Обновление vite.config.ts для правильной конфигурации
if [ -f "frontend/vite.config.ts" ]; then
    echo "⚙️  Updating vite.config.ts..."
    
    # Создаем обновленный vite.config.ts с правильными настройками
    cat > frontend/vite.config.ts << 'EOF'
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
});
EOF
fi

# Обновление tsconfig.json если нужно
if [ -f "frontend/tsconfig.json" ]; then
    echo "📝 Updating tsconfig.json..."
    # Можно добавить обновления конфигурации TypeScript
fi

# Создание или обновление index.html
if [ ! -f "frontend/index.html" ]; then
    echo "📄 Creating index.html..."
    cat > frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OnlineSim</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
fi

# Обновление путей API в коде (если есть файлы)
echo "🔄 Updating API endpoints in code..."

if [ -d "frontend/src" ]; then
    # Заменяем старые пути API на новые
    find frontend/src -type f -name "*.ts" -o -name "*.tsx" | xargs sed -i.bak 's|"/api/|`${import.meta.env.VITE_API_URL || "/api"}/|g' 2>/dev/null || true
    
    # Удаляем backup файлы
    find frontend -name "*.bak" -delete 2>/dev/null || true
fi

# Создание компонента для интеграции с SSE
if [ -d "frontend/src/lib" ]; then
    echo "📡 Creating SSE integration..."
    cat > frontend/src/lib/sse.ts << 'EOF'
// Server-Sent Events integration
export class SSEClient {
  private eventSource: EventSource | null = null;
  private listeners: Map<string, Function[]> = new Map();

  connect(userId: string) {
    const url = `${import.meta.env.VITE_SSE_URL || '/api/events'}?user_id=${userId}`;
    this.eventSource = new EventSource(url);
    
    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit(event.type || 'message', data);
      } catch (e) {
        console.error('SSE parse error:', e);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE error:', error);
    };
  }

  on(eventType: string, callback: Function) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(callback);
  }

  emit(eventType: string, data: any) {
    const callbacks = this.listeners.get(eventType) || [];
    callbacks.forEach(callback => callback(data));
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

export const sseClient = new SSEClient();
EOF
fi

# Создание обновленного файла окружения для Docker
cat > frontend/.env.production << 'EOF'
VITE_API_URL=/api
VITE_SSE_URL=/api/events
EOF

echo "✅ Frontend migration completed!"
echo ""
echo "📋 Next steps:"
echo "1. cd frontend && npm install"
echo "2. Update any remaining API calls in your components"
echo "3. Test the frontend with: npm run dev"
echo "4. Build for production with: npm run build"
echo ""
echo "🐳 For Docker:"
echo "1. Update any import paths in your components if needed"
echo "2. Run: docker-compose up --build"