import {
  renderTimeline,
} from "../components/timeline.js";

import {
  dayTypeColor,
  escapeHtml,
  formatTime,
} from "../utils.js";

export function renderLegend(card) {
  if (!card._calendar) {
    return "";
  }

  const dayTypes = new Map();

  for (const day of card._calendar.days) {
    if (day.day_type) {
      dayTypes.set(
        day.day_type.id,
        day.day_type
      );
    }
  }

  if (!dayTypes.size) {
    return "";
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
                ${escapeHtml(
                  dayType.name
                )}
              </span>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}


export function renderCalendar(card) {
  if (!card._calendar) {
    return "";
  }

  const firstDay =
    card._monthStart();

  const leadingEmpty =
    (firstDay.getDay() + 6) % 7;

  const cells = [];

  for (
    let index = 0;
    index < leadingEmpty;
    index += 1
  ) {
    cells.push(
      `<div class="day empty"></div>`
    );
  }

  for (const day of card._calendar.days) {
    const date = new Date(
      `${day.date}T12:00:00`
    );

    const selected =
      day.date === card._selectedDate;

    const exception =
      day.calendar_exception_id
        ? " exception"
        : "";

    const dayType =
      day.day_type?.name || "";

    const color =
      dayTypeColor(day.day_type);

    cells.push(`
      <button
        class="day${selected ? " selected" : ""}${exception}"
        data-date="${day.date}"
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
              : ""
          }
        </div>

        ${
          dayType
            ? `
              <span class="day-type">
                ${escapeHtml(dayType)}
              </span>
            `
            : ""
        }
      </button>
    `);
  }

  return `
    <div class="weekdays">
      <span>Lun</span>
      <span>Mar</span>
      <span>Mer</span>
      <span>Jeu</span>
      <span>Ven</span>
      <span>Sam</span>
      <span>Dim</span>
    </div>

    <div class="calendar-grid">
      ${cells.join("")}
    </div>
  `;
}


export function renderSelectedDay(card) {
  const day = card._selectedDay();

  if (!day) {
    return "";
  }

  const label =
    new Intl.DateTimeFormat(
      card._hass?.locale?.language ||
        "fr-FR",
      {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
      }
    ).format(
      new Date(
        `${day.date}T12:00:00`
      )
    );

  const moments =
    day.scheduled_moments || [];

  return `
    <div class="details">
      <div class="details-title">
        ${escapeHtml(label)}
      </div>

      <div class="details-meta">
        <span>
          Type :
          <strong>
            ${
              day.day_type?.name
                ? escapeHtml(
                    day.day_type.name
                  )
                : "Aucun"
            }
          </strong>
        </span>

        ${
          day.calendar_exception_id
            ? `
              <span class="exception-label">
                Exception
              </span>
            `
            : ""
        }
      </div>

      ${renderTimeline(day.scheduled_moments)}

      ${
        moments.length
          ? `
            <div class="moments">
              ${moments
                .map(
                  (item) => `
                    <div class="moment-row">
                      <div class="moment-time">
                        ${formatTime(
                          item.time_definition
                            ?.fixed_time
                        )}
                      </div>

                      <div class="moment-icon">
                        ${
                          item.moment?.icon
                            ? `
                              <ha-icon
                                icon="${escapeHtml(
                                  item.moment.icon
                                )}"
                              ></ha-icon>
                            `
                            : ""
                        }
                      </div>

                      <div class="moment-name">
                        ${escapeHtml(
                          item.moment?.name ||
                          item.moment?.id ||
                          ""
                        )}
                      </div>
                    </div>
                  `
                )
                .join("")}
            </div>
          `
          : ""
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
