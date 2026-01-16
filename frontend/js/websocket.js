/**
 * WebSocket 연결 관리
 */
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 2000;
        this.isConnected = false;
        this.onDataCallback = null;
        this.onConnectionChangeCallback = null;
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.ws = new WebSocket(wsUrl);
            this.ws.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                if (this.onConnectionChangeCallback) this.onConnectionChangeCallback(true);
            };
            this.ws.onclose = () => {
                this.isConnected = false;
                if (this.onConnectionChangeCallback) this.onConnectionChangeCallback(false);
                this.scheduleReconnect();
            };
            this.ws.onerror = (e) => console.error('WebSocket error:', e);
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (this.onDataCallback) this.onDataCallback(data);
                } catch (e) { console.error('Parse error:', e); }
            };
        } catch (error) {
            this.scheduleReconnect();
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), this.reconnectDelay);
        }
    }

    disconnect() { if (this.ws) { this.ws.close(); this.ws = null; } }
    onData(callback) { this.onDataCallback = callback; }
    onConnectionChange(callback) { this.onConnectionChangeCallback = callback; }
}

window.wsManager = new WebSocketManager();
