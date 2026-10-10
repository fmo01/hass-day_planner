import { renderTimeline } from '../components/timeline.js';

import { dayTypeColor, escapeHtml, formatLongDate, formatTime, getLanguage } from '../utils.js';

function getWeekdayLabels(language) {
  // Un lundi connu
  const monday = new Date(2026, 8, 7);

  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(2026, 8, 7 + index);

    let label = new Intl.DateTimeFormat(language || 'en', {
      weekday: 'short',
    })
      .format(date)
      .replace(/\./g, '')
      .slice(0, 3);

    // Première lettre en majuscule
    label = label.charAt(0).toLocaleUpperCase(language) + label.slice(1);

    return label;
  });
}

export function renderLegend(card) {
  if (!card._calendar) {
    return '';
  }

  const dayTypes = new Map();

  for (const day of card._calendar.days) {
    if (day.day_type) {
      dayTypes.set(day.day_type.id, day.day_type);
    }
  }

  if (!dayTypes.size) {
    return '';
  }

  return `
    <div class="legend">
      ${[...dayTypes.values()]
        .map(
          (dayType) => `
            <div class="legend-item">
              <span
                class="legend-color"
                style="
                  background:
                    ${dayTypeColor(dayType)};
                "
              ></span>

              <span>
                ${escapeHtml(dayType.name)}
              </span>
            </div>
          `
        )
        .join('')}
    </div>
  `;
}

export function renderCalendar(card) {
  if (!card._calendar) {
    return '';
  }

  const firstDay = card._monthStart();

  const leadingEmpty = (firstDay.getDay() + 6) % 7;

  const cells = [];

  const language = getLanguage(card._hass);

  const weekdayLabels = getWeekdayLabels(language);

  for (let index = 0; index < leadingEmpty; index += 1) {
    cells.push(`<div class="day empty"></div>`);
  }

const calendarExceptions =
  card._configuration?.calendar_exceptions || [];

const t = (key, fallback) =>
  card._i18n?.t(key, fallback) ?? fallback;

  for (const day of card._calendar.days) {
    const date = new Date(`${day.date}T12:00:00`);

    const selected = day.date === card._selectedDate;

    const exception = day.calendar_exception_id ? ' exception' : '';

    const dayType = day.day_type?.name || '';

const baseDayType =
  day.base_day_type?.name || '';

const calendarException =
  day.calendar_exception_id
    ? calendarExceptions.find(
        (item) =>
          item.id === day.calendar_exception_id
      )
    : null;

let tooltip = '';

if (calendarException) {
  tooltip =
    `${t(
      'calendar_exceptions.original_day_type',
      'Type de journée d’origine'
    )} : ${baseDayType || '—'}\n` +
    `${t(
      'calendar_exceptions.exception_day_type',
      'Type de journée exceptionnel'
    )} : ${dayType || '—'}`;

  if (calendarException.description) {
    tooltip +=
      `\n${t(
        'calendar_exceptions.description',
        'Description'
      )} : ${calendarException.description}`;
  }
} else if (dayType) {
  tooltip =
    `${t(
      'calendar_exceptions.day_type',
      'Type de journée'
    )} : ${dayType}`;
}




    const color = dayTypeColor(day.day_type);

    cells.push(`
      <button
        class="day${selected ? ' selected' : ''}${exception}"
        data-date="${day.date}"
        data-tooltip="${escapeHtml(tooltip)}"
        type="button"
        style="
          --day-type-color:
            ${color};
        "
      >
        <div class="day-header">
          <span class="day-number">
            ${date.getDate()}
          </span>

          ${
            day.calendar_exception_id
              ? `
                <ha-icon
                  class="exception-icon"
                  icon="mdi:calendar-alert"
                ></ha-icon>
              `
              : ''
          }
        </div>

        ${
          dayType
            ? `
              <span class="day-type">
                ${escapeHtml(dayType)}
              </span>
            `
            : ''
        }
      </button>
    `);
  }

  return `
  <div class="weekdays">
    ${weekdayLabels
      .map(
        (label) => `
          <span>
            ${escapeHtml(label)}
          </span>
        `
      )
      .join('')}
  </div>

    <div class="calendar-grid">
      ${cells.join('')}
    </div>
  `;
}

export function renderSelectedDay(card) {
  const day = card._selectedDay();

  if (!day) {
    return '';
  }

  const label = formatLongDate(day.date, card._hass);

  const moments = day.scheduled_moments || [];

  return `
    <div class="details">
      <div class="details-title">
        ${escapeHtml(label)}
      </div>

      <div class="details-meta">
        <span>
          Type :
          <strong>
            ${day.day_type?.name ? escapeHtml(day.day_type.name) : 'Aucun'}
          </strong>
        </span>

        ${
          day.calendar_exception_id
            ? `
              <span class="exception-label">
                Exception
              </span>
            `
            : ''
        }
      </div>

      ${renderTimeline(day.scheduled_moments)}

<div class="calendar-exception-actions">
  ${
    day.calendar_exception_id
      ? `
          <button
            class="icon-button edit-calendar-exception"
            data-calendar-exception-id="${escapeHtml(day.calendar_exception_id)}"
            data-date="${escapeHtml(day.date)}"
            type="button"
            title="Modifier l'exception"
          >
            <ha-icon icon="mdi:pencil"></ha-icon>
          </button>

          <button
            class="icon-button delete-calendar-exception"
            data-calendar-exception-id="${escapeHtml(day.calendar_exception_id)}"
            type="button"
            title="Supprimer l'exception"
          >
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        `
      : `
          <button
            class="add-calendar-exception"
            data-date="${escapeHtml(day.date)}"
            type="button"
          >
            <ha-icon icon="mdi:calendar-plus"></ha-icon>
            <span>Exception</span>
          </button>
        `
  }
</div>

      ${
        moments.length
          ? `
            <div class="moments">
              ${moments
                .map(
                  (item) => `
                    <div class="moment-row">
                      <div class="moment-time">
                        ${formatTime(item.time_definition?.fixed_time)}
                      </div>

                      <div class="moment-icon">
                        ${
                          item.moment?.icon
                            ? `
                              <ha-icon
                                icon="${escapeHtml(item.moment.icon)}"
                              ></ha-icon>
                            `
                            : ''
                        }
                      </div>

                      <div class="moment-name">
                        ${escapeHtml(item.moment?.name || item.moment?.id || '')}
                      </div>
                    </div>
                  `
                )
                .join('')}
            </div>
          `
          : ''
      }
    </div>
  `;
}

export function renderCalendarView(card) {
  return `
    ${renderLegend(card)}
    ${renderCalendar(card)}
    ${renderSelectedDay(card)}
  `;
}
