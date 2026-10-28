import { escapeHtml } from '../utils.js';

const DAYS = [
  ['monday', 'Lundi'],
  ['tuesday', 'Mardi'],
  ['wednesday', 'Mercredi'],
  ['thursday', 'Jeudi'],
  ['friday', 'Vendredi'],
  ['saturday', 'Samedi'],
  ['sunday', 'Dimanche'],
];

export function renderWeekSchedulesView(card) {
  const configuration = card._configuration;

  if (!configuration) {
    return '';
  }

  const weekSchedules = configuration.week_schedules || [];

  const dayTypes = configuration.day_types || [];

  const dayTypesById = new Map(dayTypes.map((dayType) => [dayType.id, dayType]));

  return `
    <div class="week-schedules-view">

      <div class="week-schedules-header">
        <h2>Semaines types</h2>

        <button
          id="add-week-schedule"
          class="add-button"
          type="button"
          title="Ajouter une semaine type"
          aria-label="Ajouter une semaine type"
        >
          <ha-icon
            icon="mdi:plus"
          ></ha-icon>
        </button>
      </div>
${
  weekSchedules.length
    ? weekSchedules
        .map((weekSchedule) => {
          const expanded = card._expandedWeekScheduleIds.has(weekSchedule.id);

          return `
            <div
              class="week-schedule-card"
              data-week-schedule-id="${escapeHtml(weekSchedule.id)}"
            >
              <div class="week-schedule-header">
                <strong>
                  ${escapeHtml(weekSchedule.name)}
                </strong>

                <div class="week-schedule-actions">
                  <button
                    class="icon-button edit-week-schedule"
                    data-week-schedule-id="${escapeHtml(weekSchedule.id)}"
                    type="button"
                    title="Modifier la semaine type"
                  >
                    <ha-icon
                      icon="mdi:pencil"
                    ></ha-icon>
                  </button>
                  <button
                    class="icon-button duplicate-week-schedule"
                    data-week-schedule-id="${escapeHtml(weekSchedule.id)}"
                    type="button"
                    title="Dupliquer la semaine type"
                    aria-label="Dupliquer la semaine type"
                  >
                    <ha-icon icon="mdi:content-copy"></ha-icon>
                  </button>
<button
  class="icon-button danger delete-week-schedule"
  data-week-schedule-id="${escapeHtml(weekSchedule.id)}"
  type="button"
  title="Supprimer la semaine type"
>
  <ha-icon
    icon="mdi:close"
  ></ha-icon>
</button>
                  <button
                    class="icon-button toggle-week-schedule"
                    data-week-schedule-id="${escapeHtml(weekSchedule.id)}"
                    type="button"
                    title="${expanded ? 'Replier' : 'Déplier'}"
                  >
                    <ha-icon
                      icon="${expanded ? 'mdi:chevron-down' : 'mdi:chevron-right'}"
                    ></ha-icon>
                  </button>
                </div>
              </div>

              ${
                expanded
                  ? `
                    <div class="week-schedule-days">
                      ${DAYS.map(([key, label]) => {
                        const dayType = dayTypesById.get(weekSchedule[key]);

                        return `
                          <div
                            class="week-schedule-day"
                          >
                            <span
                              class="week-schedule-day-name"
                            >
                              ${label}
                            </span>

                            <span
                              class="week-schedule-day-type"
                            >
                              ${escapeHtml(dayType?.name || weekSchedule[key] || '—')}
                            </span>
                          </div>
                        `;
                      }).join('')}
                    </div>
                  `
                  : ''
              }
            </div>
          `;
        })
        .join('')
    : `
        <div class="week-schedules-empty">
          Aucune semaine type configurée.
        </div>
      `
}
    </div>
  `;
}


console.info(
  '%c WEEK-SCHEDULES-VIEW  %c v0.1.0',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);
