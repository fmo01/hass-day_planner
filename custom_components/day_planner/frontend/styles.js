console.info("style v0.3");
export const styles = `
  :host {
    display: block;
    width: 100%;
    min-width: 0;
  }

  ha-card {
    display: block;
    width: 100%;
    box-sizing: border-box;
  }

  .container {
    width: 100%;
    box-sizing: border-box;
    padding: 16px;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
  }

  .title {
    font-size: 20px;
    font-weight: 600;
  }

  .month-navigation {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .month-label {
    min-width: 160px;
    text-align: center;
    font-weight: 500;
    text-transform: capitalize;
  }

  .navigation-button {
    border: 0;
    background: transparent;
    cursor: pointer;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    color: var(--primary-text-color);
  }

  .navigation-button:hover {
    background:
      var(--secondary-background-color);
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 16px;
    margin-bottom: 14px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
  }

  .weekdays,
  .calendar-grid {
    display: grid;
    width: 100%;
    grid-template-columns:
      repeat(7, 1fr);
    gap: 4px;
    box-sizing: border-box;
  }

  .weekdays {
    margin-bottom: 4px;
  }

  .weekdays span {
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color:
      var(--secondary-text-color);
    padding: 6px 2px;
  }

  .day {
    position: relative;
    width: 100%;
    min-width: 0;
    min-height: 62px;
    box-sizing: border-box;
    border: 1px solid
      var(--divider-color);
    border-top: 4px solid
      var(--day-type-color);
    border-radius: 8px;
    background:
      var(--card-background-color);
    color:
      var(--primary-text-color);
    padding: 6px;
    text-align: left;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .day.empty {
    border-color: transparent;
    background: transparent;
    cursor: default;
  }

  .day:hover:not(.empty) {
    background:
      var(--secondary-background-color);
  }

  .day.selected {
    outline: 2px solid
      var(--primary-color);
    outline-offset: -2px;
  }

  .day.exception {
    border-left: 4px solid
      var(--warning-color);
  }

  .day-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .day-number {
    font-weight: 600;
  }

  .exception-icon {
    --mdc-icon-size: 16px;
    color: var(--warning-color);
  }

  .day-type {
    display: block;
    width: 100%;
    font-size: 11px;
    font-weight: 500;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .day-types-view h2 {
    margin-top: 0;
  }

.  day-types-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .day-type-item {
    display: grid;
    grid-template-columns:
      16px 1fr auto auto;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border: 1px solid
      var(--divider-color);
    border-radius: 8px;
  }

.day-type-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

  .day-type-name {
    font-weight: 500;
  }

  .day-type-count {
    color:
      var(--secondary-text-color);
    font-size: 12px;
  }

  .day-types-empty {
    color:
      var(--secondary-text-color);
  }

  .day-type-item {
    cursor: pointer;
  }

  .day-type-item:hover {
    background:
      var(--secondary-background-color);
  }

  .day-type-item.selected {
    outline: 2px solid
      var(--primary-color);
    outline-offset: -2px;
  }

  .day-type-details {
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid
      var(--divider-color);
  }

  .day-type-details-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
  }

  .details {
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid
      var(--divider-color);
  }

  .details-title {
    font-size: 18px;
    font-weight: 600;
    text-transform: capitalize;
  }

  .details-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 6px;
    color:
      var(--secondary-text-color);
  }

  .exception-label {
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 12px;
    background:
      var(--warning-color);
    color:
      var(--text-primary-color);
  }

  .moments {
    margin-top: 14px;
  }

  .moment-row {
    display: grid;
    grid-template-columns:
      60px 32px 1fr;
    align-items: center;
    min-height: 42px;
    border-bottom: 1px solid
      var(--divider-color);
  }

  .moment-time {
    font-weight: 600;
  }

  .moment-icon {
    display: flex;
    align-items: center;
  }

  .moment-name {
    font-size: 14px;
  }

  .timeline-wrapper {
    margin-top: 22px;
    padding-top: 20px;
    padding-bottom: 55px;
    overflow: hidden;
  }

  .timeline-hours {
    position: relative;
    height: 18px;
    margin: 0 8px;
    color:
      var(--secondary-text-color);
    font-size: 10px;
  }

  .timeline-hour {
    position: absolute;
    transform: translateX(-50%);
  }

  .timeline {
    position: relative;
    height: 12px;
    margin: 6px 8px 0;
    border-radius: 6px;
    background:
      var(--divider-color);
  }

  .timeline-marker {
    position: absolute;
    top: 50%;
    transform:
      translate(-50%, -50%);
  }

  .timeline-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background:
      var(--primary-color);
    border: 3px solid
      var(--card-background-color);
    box-sizing: border-box;
  }

  .timeline-label {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 80px;
    font-size: 11px;
    white-space: nowrap;
  }

  .timeline-label ha-icon {
    --mdc-icon-size: 18px;
    margin-bottom: 2px;
  }

  .timeline-label strong {
    font-size: 10px;
    color:
      var(--secondary-text-color);
  }

  .timeline-empty,
  .empty-moments {
    margin-top: 16px;
    color:
      var(--secondary-text-color);
  }

  .loading,
  .error {
    padding: 24px;
    text-align: center;
  }

  .error {
    color:
      var(--error-color);
  }

  .timeline-marker.editable {
    cursor: pointer;
  }

  .timeline-marker.editable:hover
  .timeline-dot {
    transform: scale(1.25);
  }

  .scheduled-moment-time input {
    padding: 8px;
    border: 1px solid
      var(--divider-color);
    border-radius: 6px;
    background:
      var(--card-background-color);
    color:
      var(--primary-text-color);
    font: inherit;
  }

  .editor-button {
    border: 0;
    border-radius: 6px;
    padding: 8px 14px;
    cursor: pointer;
    font: inherit;
  }

  .editor-button.primary {
    background:
      var(--primary-color);
    color:
      var(--text-primary-color);
  }

  @media (max-width: 600px) {
    .container {
      padding: 10px;
    }

    .header {
      align-items: flex-start;
      flex-direction: column;
    }

    .day {
      min-height: 58px;
      padding: 4px;
    }

    .day-type {
      font-size: 9px;
    }
  }
.day-type-details-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.day-type-name-input {
  min-width: 220px;
  padding: 8px 10px;
  border: 1px solid
    var(--divider-color);
  border-radius: 6px;
  background:
    var(--card-background-color);
  color:
    var(--primary-text-color);
  font: inherit;
}

.icon-button {
  border: 0;
  background: transparent;
  color:
    var(--primary-text-color);
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.icon-button:hover {
  background:
    var(--secondary-background-color);
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.modal-dialog {
  width: min(420px, 100%);
  background:
    var(--card-background-color);
  color:
    var(--primary-text-color);
  border-radius: 12px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.35);
  padding: 20px;
  box-sizing: border-box;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 18px;
}

.modal-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.modal-field input {
  padding: 10px 12px;
  border: 1px solid
    var(--divider-color);
  border-radius: 8px;
  background:
    var(--card-background-color);
  color:
    var(--primary-text-color);
  font: inherit;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
}

.modal-moment-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  font-size: 16px;
}

.modal-moment-name ha-icon {
  --mdc-icon-size: 22px;
}

.day-types-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.day-types-header h2 {
  margin: 0;
}

.add-button {
  display: flex;
  align-items: center;
  justify-content: center;

  width: 34px;
  height: 34px;

  padding: 0;
  border: 0;
  border-radius: 50%;

  background: #2e7d32;
  color: white;

  cursor: pointer;

  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.22);
}

.add-button ha-icon {
  --mdc-icon-size: 22px;
}

.add-button:hover {
  background: #388e3c;
}

.add-button:active {
  transform: scale(0.94);
}

.editor-button.danger {
  background: var(--error-color);
  color: white;
}

.delete-day-type {
  color: var(--error-color);
}

.modal-message {
  margin: 12px 0 18px;
}


`;
