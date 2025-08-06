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
