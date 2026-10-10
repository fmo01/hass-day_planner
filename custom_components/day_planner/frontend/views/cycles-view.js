console.info('cycles-view.js v1');

import { escapeHtml, formatLongDate, getLanguage } from '../utils.js';

export function renderCyclesView(card) {
  const configuration = card._configuration;

  if (!configuration) {
    return '';
  }
  const language = getLanguage(card._hass);

  const cycles = configuration.cycles || [];

  const weekSchedules = configuration.week_schedules || [];

  const weekSchedulesById = new Map(
    weekSchedules.map((weekSchedule) => [weekSchedule.id, weekSchedule])
  );

  const t = (key, fallback) => card._i18n?.t(key, fallback) ?? fallback;

  return /* html */ `
    <div class="cycles-view">

      <div class="cycles-header">
        <h2> ${escapeHtml(t('cycles.title', 'Cycles'))} </h2>

        <button
          id="add-cycle"
          class="add-button"
          type="button"
          title="${escapeHtml(t('cycles.create_title', 'Créer un cycle'))}"
        >
          <ha-icon
            icon="mdi:plus"
          ></ha-icon>
        </button>
      </div>

      ${
        cycles.length
          ? cycles
              .map(
                (cycle) => `
                <div
                  class="cycle-card"
                  data-cycle-id="${escapeHtml(cycle.id)}"
                >
                  <div class="cycle-header">
                    <strong>
                      ${escapeHtml(cycle.name)}
                    </strong>
  <div class="cycle-actions">
    <button
      class="icon-button edit-cycle"
      data-cycle-id="${escapeHtml(cycle.id)}"
      type="button"
      title="${escapeHtml(t('common.edit', 'Modifier'))}"
    >
      <ha-icon
        icon="mdi:pencil"
      ></ha-icon>
    </button>

    <button
      class="icon-button delete-cycle"
      data-cycle-id="${escapeHtml(cycle.id)}"
      type="button"
      title="${escapeHtml(t('common.delete', 'Supprimer'))}"
    >
      <ha-icon
        icon="mdi:close"
      ></ha-icon>
    </button>
  </div>
                  </div>

                  <div class="cycle-start-date">
                    ${escapeHtml(t('cycles.start_date', 'Date de début'))} :
${escapeHtml(formatLongDate(cycle.start_date, card._hass ))}
                  </div>

                  <div class="cycle-weeks">
                    ${(cycle.week_schedule_ids || [])
                      .map((weekScheduleId, index) => {
                        const weekSchedule = weekSchedulesById.get(weekScheduleId);

                        return `
                            <div class="cycle-week">
                              <span class="cycle-week-number">
                                ${index + 1}.
                              </span>

                              <span>
                                ${escapeHtml(weekSchedule?.name || weekScheduleId)}
                              </span>
                            </div>
                          `;
                      })
                      .join('')}
                  </div>
                </div>
              `
              )
              .join('')
          : `
              <div class="cycles-empty">
                ${escapeHtml(t('cycles.empty', 'Aucun cycle configuré.'))}
              </div>
            `
      }

    </div>
  `;
}
