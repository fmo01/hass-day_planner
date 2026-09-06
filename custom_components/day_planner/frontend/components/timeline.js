import {
  escapeHtml,
  formatTime,
  timeToPercent,
} from "../utils.js";


export function renderTimeline(
  scheduledMoments,
  options = {}
) {
  const moments =
    scheduledMoments || [];
  const editable =
    options.editable === true;


  if (!moments.length) {
    return `
      <div class="timeline-empty">
        Aucun moment programmé.
      </div>
    `;
  }

  const hours = [];

  for (
    let hour = 0;
    hour <= 24;
    hour += 2
  ) {
    hours.push(`
      <span
        class="timeline-hour"
        style="
          left: ${(hour / 24) * 100}%;
        "
      >
        ${String(hour).padStart(2, "0")}
      </span>
    `);
  }

  const markers = moments
    .map((item) => {
      const time =
        item.time_definition?.fixed_time;

      const position =
        timeToPercent(time);
      const momentId =
        item.moment?.id || "";

      const editableClass =
        editable ? " editable" : "";

      const editableAttributes =
        editable
          ? `
            data-moment-id="${escapeHtml(momentId)}"
            data-time="${escapeHtml(
              formatTime(time)
            )}"
          `
        : "";
      return `
        <div
          class="timeline-marker${editableClass}"
          ${editableAttributes}
          style="
            left: ${position}%;
          "
          title="${escapeHtml(
            `${formatTime(time)} - ${
              item.moment?.name || ""
            }`
          )}"
        >
          <div class="timeline-dot">
          </div>

          <div class="timeline-label">
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

            <span>
              ${escapeHtml(
                item.moment?.name ||
                item.moment?.id ||
                ""
              )}
            </span>

            <strong>
              ${formatTime(time)}
            </strong>
          </div>
        </div>
      `;
    })
    .join("");

  return `
    <div class="timeline-wrapper">
      <div class="timeline-hours">
        ${hours.join("")}
      </div>

      <div class="timeline">
        ${markers}
      </div>
    </div>
  `;
}
