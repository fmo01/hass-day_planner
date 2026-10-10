console.info('style v0.5');
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

.day-types-list {
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
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
    gap: 10px;
    font-size: 18px;
    flex-wrap: wrap;
  }

.day-type-details-header .add-scheduled-moment {
  margin-left: auto;
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

  .timeline-wrapper {
    margin-top: 22px;
    padding-top: 20px;
    padding-bottom: calc(
      55px +
      var(--timeline-max-lane, 0) * 44px
    );
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
    top: calc(
      16px +
      var(--timeline-label-lane, 0) * 44px
    );
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 80px;
    font-size: 11px;
    white-space: nowrap;
  }

  .timeline-marker.edge-start .timeline-label {
    left: 0;
    transform: translateX(0);
    align-items: flex-start;
  }

  .timeline-marker.edge-end .timeline-label {
    left: auto;
    right: 0;
    transform: translateX(0);
    align-items: flex-end;
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

@media (max-width: 800px) {
  .moment-details-sequence-step {
    grid-template-columns: 1fr;
    row-gap: 2px;
  }

  .moment-details-service-label {
    padding-left: 12px;
  }

  .moment-details-step-value {
    padding-left: 12px;
  }
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

    .day-type-item {
      grid-template-columns: 16px minmax(0, 1fr) auto;
      row-gap: 6px;
    }

    .day-type-count {
      grid-column: 2;
    }

    .day-type-actions {
      grid-column: 3;
      grid-row: 1 / span 2;
    }
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
  width: min(520px, 100%);
  max-height: calc(100vh - 40px);

  display: flex;
  flex-direction: column;

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

.modal-dialog-content {
  overflow-y: auto;
  min-height: 0;
  padding-right: 4px;
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
  gap: 10px;
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

.icon-button.danger {
  color: var(--error-color);
}

.icon-button.danger:hover {
  background: rgba(255, 0, 0, 0.08);
}

.modal-message {
  margin: 20px 0 28px;
  line-height: 1.5;
}

.secondary-button {
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  background: var(--secondary-background-color);
  color: var(--primary-text-color);
  font-size: 14px;
  cursor: pointer;
}

.danger-button {
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  background: var(--error-color);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.week-schedules-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.week-schedules-header h2 {
  margin: 0;
}

.week-schedules-header .add-button {
  margin-left: auto;
}

.week-schedule-card {
  border: 1px solid var(--divider-color);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.week-schedule-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.week-schedule-days {
  display: grid;
  gap: 4px;
}

.week-schedule-day {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  padding: 7px 0;
  border-bottom: 1px solid var(--divider-color);
}

.week-schedule-day:last-child {
  border-bottom: 0;
}

.week-schedule-day-name {
  font-weight: 500;
}

.week-schedule-day-type {
  color: var(--secondary-text-color);
}

.week-schedules-empty {
  color: var(--secondary-text-color);
  padding: 16px 0;
}

.week-schedule-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.week-schedule-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.cycles-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.cycles-header h2 {
  margin: 0;
}

.cycles-header .add-button {
  margin-left: auto;
}

.cycle-card {
  border: 1px solid var(--divider-color);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.cycle-start-date {
  color: var(--secondary-text-color);
  margin-bottom: 10px;
}

.cycle-weeks {
  display: grid;
  gap: 6px;
}

.cycle-week {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cycle-week-number {
  min-width: 20px;
  font-weight: 500;
}

.cycles-empty {
  color: var(--secondary-text-color);
  padding: 16px 0;
}

.cycle-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.cycle-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

.delete-cycle {
  color: var(--error-color);
}

.modal-error {
  margin: 10px 0 14px;
  padding: 10px 12px;
  border-radius: 8px;
  background: color-mix(
    in srgb,
    var(--error-color) 12%,
    transparent
  );
  color: var(--error-color);
  font-weight: 500;
}


.calendar-exception-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  margin-bottom: 8px;
}

.add-calendar-exception {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.calendar-exception-date {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 16px;
  border-radius: 8px;
  background: var(--secondary-background-color);
}

.calendar-exception-date ha-icon {
  flex: 0 0 auto;
}

.day[data-tooltip] {
  position: relative;
}

.day[data-tooltip]::after {
  content: attr(data-tooltip);

  position: absolute;
  left: 50%;
  bottom: calc(100% + 8px);
  transform: translateX(-50%);

  min-width: 180px;
  max-width: 280px;
  padding: 8px 10px;

  border-radius: 8px;
  background: var(--card-background-color);
  color: var(--primary-text-color);
  box-shadow: var(
    --ha-card-box-shadow,
    0 2px 8px rgba(0, 0, 0, 0.25)
  );

  white-space: pre-line;
  text-align: left;
  font-size: 13px;
  line-height: 1.4;

  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  z-index: 20;

  transition:
    opacity 0.15s ease,
    visibility 0.15s ease;

  transition-delay: 0s;
}

.day[data-tooltip]:hover::after {
  opacity: 1;
  visibility: visible;

  /* apparition après survol prolongé */
  transition-delay: 700ms;
}

.moment-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  column-gap: 16px;
  row-gap: 0;
  padding: 12px 0;
  border-bottom: 1px solid var(--divider-color);
}

.moment-content {
  grid-column: 1;
  min-width: 0;
}

.moment-buttons {
  grid-column: 2;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.moment-actions-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.moment-action-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  column-gap: 18px;

  padding: 12px 0;
  border-bottom: 1px solid var(--divider-color);
}

.moment-action-item:last-child {
  border-bottom: none;
}

.moment-action-text {
  min-width: 0;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px;
}

.moment-action-text strong {
  font-weight: 600;
}

.moment-action-id {
  color: var(--secondary-text-color);
  font-size: 0.9em;
}

.moment-action-count {
  color: var(--secondary-text-color);
  white-space: nowrap;
}

.moment-action-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

@media (max-width: 650px) {
  .moment-action-item {
    grid-template-columns: minmax(0, 1fr) auto;
    row-gap: 6px;
  }

  .moment-action-count {
    grid-column: 1;
  }

  .moment-action-buttons {
    grid-column: 2;
    grid-row: 1 / span 2;
  }
}

.moment-line-1 {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.moment-line-1 ha-icon {
  flex-shrink: 0;
}

.moment-name {
  font-weight: 600;
}

/* Partie dépliée */

.moment-details {
  grid-column: 1 / -1;
  width: 100%;
  box-sizing: border-box;

  margin-top: 12px;
  padding: 14px 8px 4px 38px;

  border-top: 1px solid var(--divider-color);
}

.moment-details-section + .moment-details-section {
  margin-top: 18px;
}

.moment-details-title {
  font-weight: 600;
  margin-bottom: 10px;
  margin-left: -28px;
}

.moment-details-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.moment-detail-chip {
  display: inline-flex;
  align-items: center;

  padding: 5px 10px;
  border-radius: 16px;

  background: var(--secondary-background-color);
  font-size: 0.9em;
}


/* Actions */

.moment-details-actions {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.moment-details-action-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.moment-details-action-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;

  padding-bottom: 6px;
}

.moment-details-action-name {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
}

.moment-details-action-name strong {
  font-weight: 600;
}

.moment-details-action-count {
  color: var(--secondary-text-color);
  font-size: 0.9em;
  white-space: nowrap;
}


/* Séquence Home Assistant */

.moment-details-sequence {
  display: flex;
  flex-direction: column;

  margin-left: 12px;

  border-left: 2px solid
    var(--divider-color);

  padding-left: 12px;
}

.moment-details-sequence-step {
  display: grid;

  grid-template-columns:
    minmax(150px, 1fr)
    minmax(180px, 1.4fr)
    auto;

  align-items: baseline;

  column-gap: 18px;

  padding: 5px 0;
}

.moment-details-entity {
  min-width: 0;
  font-weight: 500;
}

.moment-details-service-label {
  min-width: 0;
  color: var(--secondary-text-color);
}

.moment-details-step-value {
  font-weight: 500;
  white-space: nowrap;
}

.moment-details-empty {
  color: var(--secondary-text-color);
  font-size: 0.9em;
}

.moment-line-2 {
  margin-top: 4px;
  color: var(--secondary-text-color);
  font-size: 0.9em;
}

.moment-id {
  color: var(--secondary-text-color);
  font-size: 0.9em;
}


.moments-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.moments-header h2 {
  margin: 0;
}

`;
