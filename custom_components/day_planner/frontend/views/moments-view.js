console.info('moments-view.js v2');

import {
  escapeHtml,
  countActionSequenceTargets,
} from '../utils.js';

function getEntityIds(step) {
  const entityId = step?.target?.entity_id;

  if (!entityId) {
    return [];
  }

  return Array.isArray(entityId)
    ? entityId
    : [entityId];
}

function getDeviceIds(step) {
  const deviceId = step?.target?.device_id;

  if (!deviceId) {
    return [];
  }

  return Array.isArray(deviceId)
    ? deviceId
    : [deviceId];
}


function getEntityName(card, entityId) {
  return (
    card._hass?.states?.[entityId]
      ?.attributes?.friendly_name ||
    entityId
  );
}


function getDeviceName(card, deviceId) {
  const device =
    card._hass?.devices?.[deviceId];

  return (
    device?.name_by_user ||
    device?.name ||
    deviceId
  );
}


function getHaActionLabel(card, actionName) {
  if (!actionName) {
    return '';
  }

  const parts = actionName.split('.');

  if (parts.length !== 2) {
    return actionName;
  }

  const [domain, service] = parts;

  const key =
    `component.${domain}.services.${service}.name`;

  const localize = card._serviceLocalize;

  if (!localize) {
    return actionName;
  }

  return localize(key) || actionName;
}


function getStepValue(card, step) {
  if (
    step?.data?.temperature !== undefined &&
    step?.data?.temperature !== null
  ) {
    const unit =
      card._hass?.config?.unit_system?.temperature || '';

    return `${step.data.temperature}${unit ? ` ${unit}` : ''}`;
  }

  return '';
}


export function renderMomentsView(card) {
  const configuration = card._configuration;

  const t = (key, fallback) => card._i18n?.t(key, fallback) ?? fallback;

  if (!configuration) {
    return '';
  }

  const moments = configuration.moments || [];
  const dayTypes = configuration.day_types || [];

  return `
    <div class="moments-view">
      <div class="moments-header">
        <h2>
          ${escapeHtml(
            t('moments.title', 'Moments')
          )}
        </h2>

        <button
          id="add-moment"
          class="add-button"
          type="button"
          title="${escapeHtml(
            t('moments.add', 'Ajouter un moment')
          )}"
          aria-label="${escapeHtml(
            t('moments.add', 'Ajouter un moment')
          )}"
        >
          <ha-icon
            icon="mdi:plus"
          ></ha-icon>
        </button>
      </div>

      ${
        moments.length === 0
          ? `
            <div class="moments-empty">
              ${escapeHtml(
                t(
                  'moments.no_moment',
                  'Aucun moment configuré.'
                )
              )}
            </div>
          `
          : `
            <div class="moments-list">
              ${moments
                .map((moment) => {
                  const dayTypesUsingMoment = dayTypes.filter(
                    (dayType) =>
                      (dayType.scheduled_moments || []).some(
                        (scheduled) =>
                          scheduled.moment_id === moment.id
                      )
                  );

                  const usageCount =
                    dayTypesUsingMoment.length;

                  const actionGroups =
                    moment.actions || [];

                  const actionGroupCount =
                    actionGroups.length;

                  const actionCount = actionGroups.reduce(
                    (total, action) =>
                      total +
                      countActionSequenceTargets(action.sequence),
                    0
                  );

                  const isExpanded =
                    card._expandedMomentIds?.has(moment.id) || false;

                  return `
                    <div
                      class="moment-item"
                      data-moment-id="${escapeHtml(moment.id)}"
                    >
<div class="moment-content">
  <div class="moment-line-1">
    <button
      class="icon-button toggle-moment-details"
      data-moment-id="${escapeHtml(moment.id)}"
      type="button"
      title="${
        isExpanded
          ? escapeHtml(
              t('moments.hide_details', 'Masquer les détails')
            )
          : escapeHtml(
              t('moments.show_details', 'Afficher les détails')
            )
      }"
      aria-label="${
        isExpanded
          ? escapeHtml(
              t('moments.hide_details', 'Masquer les détails')
            )
          : escapeHtml(
              t('moments.show_details', 'Afficher les détails')
            )
      }"
    >
      <ha-icon
        icon="${isExpanded ? 'mdi:chevron-up' : 'mdi:chevron-down'}"
      ></ha-icon>
    </button>
    
    ${
      moment.icon
        ? `
          <ha-icon
            icon="${escapeHtml(moment.icon)}"
          ></ha-icon>
        `
        : ''
    }

    <strong class="moment-name">
      ${escapeHtml(moment.name)}
    </strong>

    <span class="moment-id">
      ${escapeHtml(moment.id)}
    </span>
  </div>

  <div class="moment-line-2">
    ${escapeHtml(
      t('moments.used_in', 'Présent dans')
    )}
    ${usageCount}
    ${escapeHtml(
      t(
        usageCount === 1
          ? 'moments.day_type'
          : 'moments.day_types_count',
        usageCount === 1
          ? 'type de journée'
          : 'types de journée'
      )
    )},
    ${actionGroupCount}
    ${escapeHtml(
      t(
        actionGroupCount === 1
          ? 'moments.action_group'
          : 'moments.action_groups',
        actionGroupCount === 1
          ? "groupe d'action"
          : "groupes d'action"
      )
    )},
    ${actionCount}
    ${escapeHtml(
      t(
        actionCount === 1
          ? 'moments.action'
          : 'moments.actions_count',
        actionCount === 1
          ? 'action'
          : 'actions'
      )
    )}
  </div>
</div>

<div class="moment-buttons">
  <button
    class="icon-button manage-moment-actions"
    data-moment-id="${escapeHtml(moment.id)}"
    type="button"
    title="${escapeHtml(
      t('moments.manage_actions', 'Gérer les actions')
    )}"
    aria-label="${escapeHtml(
      t('moments.manage_actions', 'Gérer les actions')
    )}"
  >
    <ha-icon
      icon="mdi:playlist-edit"
    ></ha-icon>
  </button>

  <button
    class="icon-button edit-moment"
    data-moment-id="${escapeHtml(moment.id)}"
    type="button"
    title="${escapeHtml(
      t('moments.edit', 'Modifier le moment')
    )}"
    aria-label="${escapeHtml(
      t('moments.edit', 'Modifier le moment')
    )}"
  >
    <ha-icon
      icon="mdi:pencil"
    ></ha-icon>
  </button>

  ${
    usageCount === 0
      ? `
        <button
          class="icon-button danger delete-moment"
          data-moment-id="${escapeHtml(moment.id)}"
          type="button"
          title="${escapeHtml(
            t('moments.delete', 'Supprimer le moment')
          )}"
          aria-label="${escapeHtml(
            t('moments.delete', 'Supprimer le moment')
          )}"
        >
          <ha-icon
            icon="mdi:close"
          ></ha-icon>
        </button>
      `
      : ''
  }
</div>

${
  isExpanded
    ? `
      <div class="moment-details">

        <div class="moment-details-section">
          <div class="moment-details-title">
              ${escapeHtml(
                t('moments.day_types', 'Types de journée')
              )}
          </div>

          ${
            dayTypesUsingMoment.length
              ? `
                <div class="moment-details-chips">
                  ${dayTypesUsingMoment
                    .map(
                      (dayType) => `
                        <span class="moment-detail-chip">
                          ${escapeHtml(dayType.name)}
                        </span>
                      `
                    )
                    .join('')}
                </div>
              `
              : `
                <div class="moment-details-empty">
                  ${escapeHtml(
                    t('moments.no_day_type', 'Aucun type de journée')
                  )}
                </div>
              `
          }
        </div>

        <div class="moment-details-section">
  <div class="moment-details-title">
    ${escapeHtml(
      t('moments.actions', 'Actions')
    )}
    
  </div>

  ${
    actionGroups.length
      ? `
        <div class="moment-details-actions">
          ${actionGroups
            .map((action) => {
              const sequence =
                action.sequence || [];

              const targetCount =
                countActionSequenceTargets(action.sequence);

              return `
                <div class="moment-details-action-group">

                  <div class="moment-details-action-header">

                    <div class="moment-details-action-name">
                      <strong>
                        ${escapeHtml(
                          action.label || action.id
                        )}
                      </strong>

                      <span class="moment-action-id">
                        ${escapeHtml(action.id)}
                      </span>
                    </div>

                    <span class="moment-details-action-count">
                      ${targetCount}
                        ${escapeHtml(
                          t(
                            targetCount === 1
                              ? 'moments.action'
                              : 'moments.actions_count',
                            targetCount === 1
                              ? 'action'
                              : 'actions'
                          )
                        )}
                    </span>

                  </div>


                  <div class="moment-details-sequence">

                    ${sequence
                      .map((step) => {
                        const entityIds =
                          getEntityIds(step);

                        const deviceIds =
                          getDeviceIds(step);

                        const actionLabel =
                          getHaActionLabel(
                            card,
                            step.action
                          );

                        const value =
                          getStepValue(card, step);

const targets = [
  ...entityIds.map((entityId) => ({
    name: getEntityName(
      card,
      entityId
    ),
  })),

  ...deviceIds.map((deviceId) => ({
    name: getDeviceName(
      card,
      deviceId
    ),
  })),
];

if (targets.length === 0) {
  return `
    <div
      class="moment-details-sequence-step"
    >
      <span
        class="moment-details-entity"
      >
        —
      </span>

      <span
        class="moment-details-service-label"
      >
        ${escapeHtml(actionLabel)}
      </span>

      <span
        class="moment-details-step-value"
      >
        ${escapeHtml(value)}
      </span>
    </div>
  `;
}

return targets
  .map(
    (target) => `
      <div
        class="moment-details-sequence-step"
      >
        <span
          class="moment-details-entity"
        >
          ${escapeHtml(target.name)}
        </span>

        <span
          class="moment-details-service-label"
        >
          ${escapeHtml(actionLabel)}
        </span>

        <span
          class="moment-details-step-value"
        >
          ${escapeHtml(value)}
        </span>
      </div>
    `
  )
  .join('');

                      })
                      .join('')}

                  </div>
                </div>
              `;
            })
            .join('')}
        </div>
      `
      : `
        <div class="moment-details-empty">
          ${escapeHtml(
            t('moments.no_action_group', "Aucun groupe d'action")
          )}
        </div>
      `
  }
        </div>

      </div>
    `
    : ''
}




                    </div>
                  `;
                })
                .join('')}
            </div>
          `
      }
    </div>
  `;
}
