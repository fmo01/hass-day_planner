console.info('timeline.js v0.1');
import { escapeHtml, formatTime, timeToPercent } from '../utils.js';

export function renderTimeline(scheduledMoments, options = {}) {
  const moments = scheduledMoments || [];
  const editable = options.editable === true;
  const emptyLabel = options.emptyLabel || 'Aucun moment programmé.';

  if (!moments.length) {
    return `
      <div class="timeline-empty">
        ${escapeHtml(emptyLabel)}
      </div>
    `;
  }

  const hours = [];

  for (let hour = 0; hour <= 24; hour += 2) {
    hours.push(`
      <span
        class="timeline-hour"
        style="
          left: ${(hour / 24) * 100}%;
        "
      >
        ${String(hour).padStart(2, '0')}
      </span>
    `);
  }

  const labelLanes = [];
  const minLabelDistance = 12;

  const positionedMoments = moments
    .map((item) => ({
      item,
      position: timeToPercent(item.time_definition?.fixed_time),
    }))
    .sort((a, b) => a.position - b.position);

  for (const positioned of positionedMoments) {
    let lane = 0;

    while (
      labelLanes[lane] !== undefined &&
      positioned.position - labelLanes[lane] < minLabelDistance
    ) {
      lane += 1;
    }

    positioned.lane = lane;
    labelLanes[lane] = positioned.position;
  }

  const maxLane = Math.max(
    0,
    ...positionedMoments.map((item) => item.lane)
  );

  const markers = positionedMoments
    .map(({ item, position, lane }) => {
      const time = item.time_definition?.fixed_time;

      const momentId = item.moment?.id || '';

      const edgeClass =
        position <= 5
          ? ' edge-start'
          : position >= 95
            ? ' edge-end'
            : '';

      const editableClass = editable ? ' editable' : '';

      const editableAttributes = editable
        ? `
            data-moment-id="${escapeHtml(momentId)}"
            data-time="${escapeHtml(formatTime(time))}"
          `
        : '';
      return `
        <div
          class="timeline-marker${editableClass}${edgeClass}"
          ${editableAttributes}
          style="
            left: ${position}%;
            --timeline-label-lane: ${lane};
          "
          title="${escapeHtml(`${formatTime(time)} - ${item.moment?.name || ''}`)}"
        >
          <div class="timeline-dot">
          </div>

          <div class="timeline-label">
            ${
              item.moment?.icon
                ? `
                  <ha-icon
                    icon="${escapeHtml(item.moment.icon)}"
                  ></ha-icon>
                `
                : ''
            }

            <span>
              ${escapeHtml(item.moment?.name || item.moment?.id || '')}
            </span>

            <strong>
              ${formatTime(time)}
            </strong>
          </div>
        </div>
      `;
    })
    .join('');

  return `
    <div class="timeline-wrapper"
           style="
             --timeline-max-lane: ${maxLane};
           "
    >
      <div class="timeline-hours">
        ${hours.join('')}
      </div>

      <div class="timeline">
        ${markers}
      </div>
    </div>
  `;
}
