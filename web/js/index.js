// Import the Lit library
import { LitElement, html, css } from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

// Define ChatGptMessages component
class ChatGptMessages extends LitElement {
  static properties = {
    messages: { type: Array },
  };

  constructor() {
    super();
    this.messages = [];
  }

  render() {
    return html`
      <div>
        ${this.messages.map((message) => html`<p>${message}</p>`)}
      </div>
    `;
  }
}
customElements.define('chat-gpt-messages', ChatGptMessages);

// Define ChatGptInput component
class ChatGptInput extends LitElement {
  static styles = css`
    div {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    input {
      flex: 1;
      padding: 8px;
      font-size: 1rem;
    }
    button {
      padding: 8px 16px;
      font-size: 1rem;
      cursor: pointer;
    }
  `;

  static properties = {
    onSend: { type: Function },
  };

  constructor() {
    super();
    this.onSend = null;
  }

  _handleClick() {
    const input = this.shadowRoot.getElementById('chat-input');
    const message = input.value.trim();
    if (message) {
      this.onSend?.(message);
      input.value = '';
    }
  }

  render() {
    return html`
      <div>
        <input type="text" id="chat-input" placeholder="Type your message here..." />
        <button @click="${this._handleClick}">Send</button>
      </div>
    `;
  }
}
customElements.define('chat-gpt-input', ChatGptInput);

// Define ChatGptApp (Parent Component)
class ChatGptApp extends LitElement {
  static properties = {
    messages: { type: Array },
  };

  constructor() {
    super();
    this.messages = [];
  }

  _handleMessage(message) {
    this.messages = [...this.messages, message];
  }

  render() {
    return html`
      <div>
        <chat-gpt-messages .messages="${this.messages}"></chat-gpt-messages>
        <chat-gpt-input .onSend="${(msg) => this._handleMessage(msg)}"></chat-gpt-input>
      </div>
    `;
  }
}
customElements.define('chat-gpt-app', ChatGptApp);

// Add the custom element to the document
document.body.innerHTML = '<chat-gpt-app></chat-gpt-app>';
