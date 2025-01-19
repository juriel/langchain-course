class EventBus {
    static instance = new EventBus();
    static getInstance() {
        return EventBus.instance;
    }

    constructor() {
      this.listeners = new Map();
    }
  
    on(eventName, callback, context) {
      if (!this.listeners.has(eventName)) {
        this.listeners.set(eventName, []);
      }
      this.listeners.get(eventName).push({ callback, context });
    }
  
    off(eventName, callback, context) {
      if (!this.listeners.has(eventName)) return;
  
      const listeners = this.listeners.get(eventName).filter(
        (listener) => listener.callback !== callback || listener.context !== context
      );
  
      if (listeners.length > 0) {
        this.listeners.set(eventName, listeners);
      } else {
        this.listeners.delete(eventName);
      }
    }
  
    emit(eventName, data) {
      if (!this.listeners.has(eventName)) return;
  
      for (const { callback, context } of this.listeners.get(eventName)) {
        callback.call(context, data);
      }
    }
}

export { EventBus };
