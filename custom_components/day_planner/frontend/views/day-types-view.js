console.info("day-types-view.js v1")
import {
  dayTypeColor,
  escapeHtml,
} from "../utils.js";

import {
  renderTimeline,
} from "../components/timeline.js";

export function renderDayTypesView(card) {
  const configuration =
    card._configuration;

  if (!configuration) {
    return "";
  }

  const dayTypes =
    configuration.day_types || [];

  const selectedDayType =
    dayTypes.find(
      (dayType) =>
        dayType.id ===
        card._selectedDayTypeId
    ) || dayTypes[0];

  const scheduledMoments =
    selectedDayType
      ? resolveScheduledMoments(
          configuration,
          selectedDayType
        )
      : [];


  if (!dayTypes.length) {
    return `
      <div class="day-types-empty">
        Aucun type de journée configuré.
      </div>
    `;
  }

  return `
    <div class="day-types-view">
      <div class="day-types-header">
        <h2>Types de journée</h2>

        <button
          id="add-day-type"
          class="add-button"
          type="button"
          title="Ajouter un type de journée"
          aria-label="Ajouter un type de journée"
        >
          <ha-icon
            icon="mdi:plus"
          ></ha-icon>
        </button>
      </div>

      <div class="day-types-list">
        ${dayTypes
          .map(
            (dayType) => `
              <div
                class="day-type-item ${
                  dayType.id === selectedDayType?.id
                    ? "selected"
                    : ""
                }"
                data-day-type-id="${escapeHtml(
                  dayType.id
                )}"
              >
                <span
                  class="legend-color"
                  style="
                    background:
                      ${dayTypeColor(dayType)};
                  "
                ></span>

                <span class="day-type-name">
                  ${escapeHtml(
                    dayType.name
                  )}
                </span>
<span class="day-type-count">
  ${
    dayType
      .scheduled_moments
      ?.length || 0
  }
  moment(s)
</span>

${
  dayType.id === selectedDayType?.id
    ? `
      <div class="day-type-actions">
        <button
          class="icon-button edit-day-type-name"
          data-day-type-id="${escapeHtml(
            dayType.id
          )}"
          type="button"
          title="Modifier le libellé"
        >
          <ha-icon
            icon="mdi:pencil"
          ></ha-icon>
        </button>

        ${
          (dayType.scheduled_moments?.length || 0) === 0
            ? `
              <button
                class="icon-button delete-day-type"
                data-day-type-id="${escapeHtml(
                  dayType.id
                )}"
                type="button"
                title="Supprimer le type de journée"
              >
                <ha-icon
                  icon="mdi:close"
                ></ha-icon>
              </button>
            `
            : ""
        }
      </div>
    `
    : ""
}
</div>
`
          )
          .join("")}
      </div>

      ${
        selectedDayType
          ? `
            <div class="day-type-details">
    <div class="day-type-details-header">
      <span
        class="legend-color"
        style="
          background:
            ${dayTypeColor(
              selectedDayType
            )};
        "
      ></span>

      <strong>
        ${escapeHtml(
          selectedDayType.name
        )}
      </strong>
    </div>

    ${renderTimeline(
      scheduledMoments,
      {
        editable: true,
      }
    )}
  </div>
`
          : ""
      }
    </div>
  `;
}

function resolveScheduledMoments(
  configuration,
  dayType
) {
  const momentsById = new Map(
    (configuration.moments || []).map(
      (moment) => [
        moment.id,
        moment,
      ]
    )
  );

  return (
    dayType.scheduled_moments || []
  ).map((scheduled) => ({
    moment:
      momentsById.get(
        scheduled.moment_id
      ) || {
        id: scheduled.moment_id,
        name: scheduled.moment_id,
        icon: null,
      },

    time_definition:
      scheduled.time_definition,
  }));
}

