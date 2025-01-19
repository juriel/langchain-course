import { LitElement, html } from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';
import { EventBus } from './event-bus.js';

// ChatGptMessages Component
class ChatGptMessages extends LitElement {
    static properties = {
        messages: { type: Array },
    };

    constructor() {
        super();
        this.messages = [];
        EventBus.getInstance().on('chat-gpt-message', (message) => {
            console.log("ChatGptMessages: ", message);

            this.messages = [...this.messages, message];
        });
    }

    render() {
        return html`
      <div>
        ${this.messages.map((message) => html`<p>${message}</p>`)}
      </div>
    `;
    }
    createRenderRoot() {
        return this; // Renderiza en el Light DOM.
    }
}
customElements.define('chat-gpt-messages', ChatGptMessages);

// ChatGptInput Component
class ChatGptInput extends LitElement {
    static properties = {
        onSend: { type: Function },
    };

    constructor() {
        super();
        this.onSend = null;

    }

    _handleClick() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        console.log("Send Messsage: ", message);
        if (message) {
            input.value = '';
            EventBus.getInstance().emit('chat-gpt-message', message);
        }
    }

    render() {
        return html`
      <div>
        <input type="text" id="chat-input" placeholder="Pregunta acá" />
        <button @click="${this._handleClick}">Send</button>
      </div>
    `;
    }
    createRenderRoot() {
        return this; // Renderiza en el Light DOM.
    }
}
customElements.define('chat-gpt-input', ChatGptInput);

// ChatGptApp Component
class ChatGptApp extends LitElement {

    render() {
        return html`
      <div>
        <chat-gpt-messages ></chat-gpt-messages>
        <chat-gpt-input ></chat-gpt-input>
      </div>
    `;
    }
    createRenderRoot() {
        return this; // Renderiza en el Light DOM.
    }
}
customElements.define('chat-gpt-app', ChatGptApp);
