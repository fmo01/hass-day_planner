// Reuse the management frontend, including when a Lovelace resource loaded it.
if (!customElements.get('day-planner-card')) {
  await import('./day-planner-card.js');
}

class DayPlannerPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: flex;
          flex-direction: column;
          height: 100%;
          min-height: 0;
          color: var(--primary-text-color);
          background: var(--primary-background-color);
        }
        header {
          display: flex;
          align-items: center;
          flex-shrink: 0;
          min-height: 56px;
          padding: 0 16px;
          gap: 16px;
          background: var(--app-header-background-color, var(--primary-color));
          color: var(--app-header-text-color, white);
        }
        h1 { font-size: 20px; font-weight: 400; margin: 0; }
        main { flex: 1; min-height: 0; overflow: auto; padding: 16px; }
        :host([narrow]) main { padding: 8px; }
        day-planner-card { display: block; width: 100%; }
      </style>
      <header>
        <ha-menu-button></ha-menu-button>
        <h1>Day Planner</h1>
      </header>
      <main><day-planner-card></day-planner-card></main>
    `;
    this._card = this.shadowRoot.querySelector('day-planner-card');
    this._card.setConfig({ type: 'custom:day-planner-card' });
    this._menu = this.shadowRoot.querySelector('ha-menu-button');
  }

  connectedCallback() {
    this._upgradeProperty('panel');
    this._upgradeProperty('narrow');
    this._upgradeProperty('hass');
  }

  _upgradeProperty(name) {
    if (Object.hasOwn(this, name)) {
      const value = this[name];
      delete this[name];
      this[name] = value;
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._menu.hass = hass;
    this._card.hass = hass;
  }

  get hass() { return this._hass; }

  set narrow(narrow) {
    this.toggleAttribute('narrow', Boolean(narrow));
    this._menu.narrow = Boolean(narrow);
  }

  set panel(panel) { this._panel = panel; }
  get panel() { return this._panel; }
}

if (!customElements.get('day-planner-panel')) {
  customElements.define('day-planner-panel', DayPlannerPanel);
}
console.info(
  '%c DAY-PLANNER-PANEL %c v0.0.2',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);
