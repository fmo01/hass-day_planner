console.info('day-types-view.js v 1.1');
import { dayTypeColor, escapeHtml } from '../utils.js';

import { renderTimeline } from '../components/timeline.js';

export function renderDayTypesView(card) {
  const configuration = card._configuration;

  const t = (key, fallback) => card._i18n?.t(key, fallback) ?? fallback;

  if (!configuration) {
    return '';
  }

  const dayTypes = configuration.day_types || [];

  const selectedDayType =
    dayTypes.find((dayType) => dayType.id === card._selectedDayTypeId) || dayTypes[0];

  const scheduledMoments = selectedDayType
    ? resolveScheduledMoments(configuration, selectedDayType)
    : [];

  return /* html */ `
    <div class="day-types-view">
      <div class="day-types-header">
        <h2>
          ${escapeHtml(t('day_types.title', 'Types de journée'))}
        </h2>

        <button
          id="add-day-type"
          class="add-button"
          type="button"
          title="${escapeHtml(t('day_types.add', 'Ajouter un type de journée'))}"
          aria-label="${escapeHtml(t('day_types.add', 'Ajouter un type de journée'))}"

        >
          <ha-icon
            icon="mdi:plus"
          ></ha-icon>
        </button>
      </div>

        ${
          dayTypes.length
            ? /* html */ `
              <div class="day-types-list">
                ${dayTypes
                  .map((dayType) =>
                    renderDayTypeItem(
                      dayType,
                      selectedDayType,
                      t
                    )
                  )
                  .join('')}
              </div>
            `
            : `
              <div class="day-types-empty">
                ${escapeHtml(t('day_types.empty', 'Aucun type de journée configuré.'))}
              </div>
            `
        }
      ${
        selectedDayType
          ? renderDayTypeDetails(
              selectedDayType,
              scheduledMoments,
              t
            )
          : ''
      }
    </div>
  `;
}

function renderDayTypeItem(dayType, selectedDayType, t) {
  const count = dayType.scheduled_moments?.length || 0;
  const selected = dayType.id === selectedDayType?.id;

  return /* html */ `
    <div
      class="day-type-item ${selected ? 'selected' : ''}"
      data-day-type-id="${escapeHtml(dayType.id)}"
    >
      <span
        class="legend-color"
        style="
          background:
            ${dayTypeColor(dayType)};
        "
      ></span>

      <span class="day-type-name">
        ${escapeHtml(dayType.name)}
      </span>

      <span class="day-type-count">
        ${count}
        ${escapeHtml(
          t(
            count === 1
              ? 'day_types.scheduled_moment'
              : 'day_types.scheduled_moments',
            count === 1 ? 'moment' : 'moments'
          )
        )}
      </span>

      ${
        selected
          ? /* html */ `
              <div class="day-type-actions">
                <button
                  class="icon-button edit-day-type-name"
                  data-day-type-id="${escapeHtml(dayType.id)}"
                  type="button"
                  title="${escapeHtml(
                    t(
                      'day_types.edit_name',
                      'Modifier le libellé'
                    )
                  )}"
                  aria-label="${escapeHtml(
                    t(
                      'day_types.edit_name',
                      'Modifier le libellé'
                    )
                  )}"
                >
                  <ha-icon icon="mdi:pencil"></ha-icon>
                </button>

                ${
                  count === 0
                    ? /* html */ `
                        <button
                          class="icon-button danger delete-day-type"
                          data-day-type-id="${escapeHtml(dayType.id)}"
                          type="button"
                          title="${escapeHtml(
                            t(
                              'day_types.delete',
                              'Supprimer le type de journée'
                            )
                          )}"
                          aria-label="${escapeHtml(
                            t(
                              'day_types.delete',
                              'Supprimer le type de journée'
                            )
                          )}"
                        >
                          <ha-icon icon="mdi:close"></ha-icon>
                        </button>
                      `
                    : ''
                }
              </div>
            `
          : ''
      }
    </div>
  `;
}

function renderDayTypeDetails(
  selectedDayType,
  scheduledMoments,
  t
) {
  return /* html */ `
    <div class="day-type-details">
      <div class="day-type-details-header">
        <span
          class="legend-color"
          style="
            background:
              ${dayTypeColor(selectedDayType)};
          "
        ></span>

        <strong>
          ${escapeHtml(selectedDayType.name)}
        </strong>

        <button
          class="add-button add-scheduled-moment"
          data-day-type-id="${escapeHtml(selectedDayType.id)}"
          type="button"
          title="${escapeHtml(
            t(
              'day_types.add_scheduled_moment',
              'Ajouter un moment'
            )
          )}"
          aria-label="${escapeHtml(
            t(
              'day_types.add_scheduled_moment',
              'Ajouter un moment'
            )
          )}"
        >
          <ha-icon icon="mdi:plus"></ha-icon>
        </button>
      </div>

      ${renderTimeline(scheduledMoments, {
        editable: true,
        emptyLabel: t(
          'day_types.no_scheduled_moment',
          'Aucun moment programmé.'
        ),
      })}
    </div>
  `;
}



function resolveScheduledMoments(configuration, dayType) {
  const momentsById = new Map((configuration.moments || []).map((moment) => [moment.id, moment]));

  return (dayType.scheduled_moments || []).map((scheduled) => ({
    moment: momentsById.get(scheduled.moment_id) || {
      id: scheduled.moment_id,
      name: scheduled.moment_id,
      icon: null,
    },

    time_definition: scheduled.time_definition,
  }));
}
