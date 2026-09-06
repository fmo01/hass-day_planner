import { DayPlannerApi } from "./api.js";
import { formatDate, escapeHtml } from "./utils.js";
import { styles } from "./styles.js";
import {
  renderCalendarView,
} from "./views/calendar-view.js";
import {
  renderDayTypesView,
} from "./views/day-types-view.js";


class DayPlannerCard extends HTMLElement {
  constructor() {
    super();

    this.attachShadow({
      mode: "open",
    });

    this._hass = null;
    this._config = {};
    this._api = null;

    this._activeTab = "calendar";

    const now = new Date();

    this._displayYear =
      now.getFullYear();

    this._displayMonth =
      now.getMonth();

    this._selectedDate =
      formatDate(now);

    this._calendar = null;
    this._configuration = null;

    this._loading = false;
    this._error = null;
    this._loadedMonthKey = null;
    this._selectedDayTypeId = null;

    this._editingScheduledMoment = null;
    this._editingDayTypeName = false;
    this._editingDayTypeId = null;

    this._creatingDayType = false;
    this._deletingDayTypeId = null;
  }

  setConfig(config) {
    this._config = config || {};

    this.style.display = "block";
    this.style.width = "100%";
  }

  set hass(hass) {
    this._hass = hass;

    if (!this._api) {
      this._api =
        new DayPlannerApi(hass);
    } else {
      this._api.setHass(hass);
    }

    const monthKey =
      `${this._displayYear}-${String(
        this._displayMonth + 1
      ).padStart(2, "0")}`;

    if (
      this._activeTab === "calendar" &&
      !this._loading &&
      this._loadedMonthKey !== monthKey
    ) {
      this._loadCalendar();
      return;
    }

    this.render();
  }

  getCardSize() {
    return 8;
  }

  getGridOptions() {
    return {
      columns: "full",
      rows: "auto",
    };
  }

  _monthStart() {
    return new Date(
      this._displayYear,
      this._displayMonth,
      1
    );
  }

  _monthEnd() {
    return new Date(
      this._displayYear,
      this._displayMonth + 1,
      0
    );
  }

  async _loadCalendar() {
    if (!this._hass) {
      return;
    }

    this._loading = true;
    this._error = null;

    this.render();

    try {
      const startDate =
        formatDate(
          this._monthStart()
        );

      const endDate =
        formatDate(
          this._monthEnd()
        );

      this._calendar =
        await this._api.getCalendar(
          startDate,
          endDate
        );

      this._loadedMonthKey =
        `${this._displayYear}-${String(
          this._displayMonth + 1
        ).padStart(2, "0")}`;

      const exists =
        this._calendar.days.some(
          (day) =>
            day.date ===
            this._selectedDate
        );

      if (!exists) {
        this._selectedDate =
          this._calendar.days[0]
            ?.date ?? null;
      }
    } catch (error) {
      console.error(
        "Day Planner calendar error",
        error
      );

      this._error =
        error?.message ||
        "Impossible de charger le calendrier.";
    } finally {
      this._loading = false;
      this.render();
    }
  }

  _previousMonth() {
    if (this._displayMonth === 0) {
      this._displayMonth = 11;
      this._displayYear -= 1;
    } else {
      this._displayMonth -= 1;
    }

    this._loadedMonthKey = null;

    this._loadCalendar();
  }

  _nextMonth() {
    if (this._displayMonth === 11) {
      this._displayMonth = 0;
      this._displayYear += 1;
    } else {
      this._displayMonth += 1;
    }

    this._loadedMonthKey = null;

    this._loadCalendar();
  }

  _selectDate(date) {
    this._selectedDate = date;
    this.render();
  }

  _selectedDay() {
    if (!this._calendar) {
      return null;
    }

    return (
      this._calendar.days.find(
        (day) =>
          day.date ===
          this._selectedDate
      ) || null
    );
  }

  _monthLabel() {
    return new Intl.DateTimeFormat(
      this._hass?.locale?.language ||
        "fr-FR",
      {
        month: "long",
        year: "numeric",
      }
    ).format(
      this._monthStart()
    );
  }

async _setActiveTab(tab) {
  this._activeTab = tab;

  if (
    tab === "day_types" &&
    this._configuration === null
  ) {
    await this._loadConfiguration();
    return;
  }

  this.render();
}

async _loadConfiguration() {
  if (!this._hass) {
    return;
  }

  this._loading = true;
  this._error = null;

  this.render();

  try {
    this._configuration =
      await this._api.getConfiguration();

      if (
        this._selectedDayTypeId === null &&
        this._configuration.day_types?.length
      ) {
        this._selectedDayTypeId =
          this._configuration.day_types[0].id;
      }
  } catch (error) {
    console.error(
      "Day Planner configuration error",
      error
    );

    this._error =
      error?.message ||
      "Impossible de charger la configuration.";
  } finally {
    this._loading = false;
    this.render();
  }
}

  _renderTabs() {
    return `
      <div class="tabs">
        <button
          class="tab ${
            this._activeTab === "calendar"
              ? "active"
              : ""
          }"
          data-tab="calendar"
          type="button"
        >
          Calendrier
        </button>

        <button
          class="tab ${
            this._activeTab === "day_types"
              ? "active"
              : ""
          }"
          data-tab="day_types"
          type="button"
        >
          Types de journée
        </button>
      </div>
    `;
  }

  _renderActiveView() {
    switch (this._activeTab) {
      case "day_types":
        return renderDayTypesView(this);

      case "calendar":
      default:
        return renderCalendarView(this);
    }
  }

  _bindEvents() {
    this.shadowRoot
      .querySelector(
        "#previous-month"
      )
      ?.addEventListener(
        "click",
        () => this._previousMonth()
      );

    this.shadowRoot
      .querySelector(
        "#next-month"
      )
      ?.addEventListener(
        "click",
        () => this._nextMonth()
      );

    this.shadowRoot
      .querySelectorAll(
        ".day[data-date]"
      )
      .forEach((element) => {
        element.addEventListener(
          "click",
          () => {
            this._selectDate(
              element.dataset.date
            );
          }
        );
      });

    this.shadowRoot
      .querySelectorAll(
        ".tab[data-tab]"
      )
      .forEach((element) => {
        element.addEventListener(
          "click",
          () => {
            this._setActiveTab(
              element.dataset.tab
            );
          }
        );
      });

    this.shadowRoot
      .querySelectorAll(
        ".day-type-item[data-day-type-id]"
      )
      .forEach((element) => {
        element.addEventListener(
          "click",
          () => {
            this._selectedDayTypeId =
              element.dataset.dayTypeId;

            this.render();
          }
        );
      });

    this.shadowRoot
      .querySelectorAll(
        ".timeline-marker.editable[data-moment-id]"
      )
      .forEach((element) => {
        element.addEventListener(
          "click",
          () => {
            this._editScheduledMoment(
              element.dataset.momentId,
              element.dataset.time
            );
          }
        );
      });
    this.shadowRoot
      .querySelector(
        "#cancel-scheduled-moment"
     )
     ?.addEventListener(
       "click",
       () => {
         this._editingScheduledMoment = null;
         this.render();
       }
     );

    this.shadowRoot
      .querySelector(
        "#save-scheduled-moment"
      )
      ?.addEventListener(
        "click",
        async () => {
          await this._saveScheduledMoment();
        }
      );

  this.shadowRoot
    .querySelectorAll(
      ".edit-day-type-name[data-day-type-id]"
    )
    .forEach((element) => {
      element.addEventListener(
        "click",
        (event) => {
          event.stopPropagation();

          this._editDayTypeName(
            element.dataset.dayTypeId
          );
        }
      );
    });

    this.shadowRoot
      .querySelector(
        "#cancel-day-type-name"
      )
      ?.addEventListener(
        "click",
        () => {
          this._editingDayTypeName = false;
          this.render();
        }
      );

    this.shadowRoot
      .querySelector(
        "#save-day-type-name"
      )
      ?.addEventListener(
        "click",
        async () => {
          await this._saveDayTypeName();
        }
      );


    this.shadowRoot
      .querySelector(
        "#cancel-day-type-name"
      )
      ?.addEventListener(
        "click",
        () => {
          this._editingDayTypeName = false;
          this._editingDayTypeId = null;

          this.render();
        }
      );

    this.shadowRoot
      .querySelector(
        "#save-day-type-name"
      )
      ?.addEventListener(
        "click",
        async () => {
          await this._saveDayTypeName();
        }
      );

this.shadowRoot
  .querySelector(
    "#add-day-type"
  )
  ?.addEventListener(
    "click",
    () => {
      this._openCreateDayTypeDialog();
    }
  );

this.shadowRoot
  .querySelector(
    "#cancel-create-day-type"
  )
  ?.addEventListener(
    "click",
    () => {
      this._creatingDayType = false;
      this.render();
    }
  );

this.shadowRoot
  .querySelector(
    "#save-create-day-type"
  )
  ?.addEventListener(
    "click",
    async () => {
      await this._saveCreateDayType();
    }
  );


this.shadowRoot
  .querySelectorAll(
    ".delete-day-type[data-day-type-id]"
  )
  .forEach((element) => {
    element.addEventListener(
      "click",
      (event) => {
        event.stopPropagation();

        this._openDeleteDayTypeDialog(
          element.dataset.dayTypeId
        );
      }
    );
  });

this.shadowRoot
  .querySelector(
    "#cancel-delete-day-type"
  )
  ?.addEventListener(
    "click",
    () => {
      this._deletingDayTypeId = null;
      this.render();
    }
  );

this.shadowRoot
  .querySelector(
    "#confirm-delete-day-type"
  )
  ?.addEventListener(
    "click",
    async () => {
      await this._deleteDayType();
    }
  );this.shadowRoot
  .querySelectorAll(
    ".delete-day-type[data-day-type-id]"
  )
  .forEach((element) => {
    element.addEventListener(
      "click",
      (event) => {
        event.stopPropagation();

        this._openDeleteDayTypeDialog(
          element.dataset.dayTypeId
        );
      }
    );
  });

this.shadowRoot
  .querySelector(
    "#cancel-delete-day-type"
  )
  ?.addEventListener(
    "click",
    () => {
      this._deletingDayTypeId = null;
      this.render();
    }
  );

    }


    _renderScheduledMomentDialog() {
      const editing =
        this._editingScheduledMoment;

      if (!editing) {
        return "";
      }

      const moment =
        this._configuration?.moments?.find(
          (item) =>
            item.id === editing.momentId
        );

      return `
        <div class="modal-backdrop">
          <div
            class="modal-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="scheduled-moment-dialog-title"
          >
            <div
              id="scheduled-moment-dialog-title"
              class="modal-title"
            >
              Modifier le moment
            </div>

            <div class="modal-moment-name">
              ${
                moment?.icon
                  ? `
                    <ha-icon
                      icon="${escapeHtml(
                        moment.icon
                      )}"
                    ></ha-icon>
                  `
                  : ""
              }

              <strong>
                ${escapeHtml(
                  moment?.name ||
                  editing.momentId
                )}
              </strong>
            </div>

            <label class="modal-field">
              <span>Heure</span>

              <input
                id="scheduled-moment-time"
                type="time"
                value="${escapeHtml(
                  editing.time
                )}"
              />
            </label>

            <div class="modal-actions">
              <button
                id="cancel-scheduled-moment"
                class="editor-button"
                type="button"
              >
                Annuler
              </button>

              <button
                id="save-scheduled-moment"
                class="editor-button primary"
                type="button"
              >
                Enregistrer
              </button>
            </div>
          </div>
        </div>
      `;
    }


    async _saveScheduledMoment() {
      const editing =
        this._editingScheduledMoment;

      if (!editing) {
        return;
      }

      const input =
        this.shadowRoot.querySelector(
          "#scheduled-moment-time"
        );

      const time =
        input?.value;

      if (!time) {
        return;
      }

      this._loading = true;
      this._error = null;

      this.render();

      try {
        await this._api.updateScheduledMoment(
          editing.dayTypeId,
          editing.momentId,
          time
        );

        this._configuration =
          await this._api.getConfiguration();

        this._loadedMonthKey = null;

        this._editingScheduledMoment = null;
      } catch (error) {
        console.error(
          "Day Planner scheduled moment update error",
          error
        );

        this._error =
          error?.message ||
          "Impossible de modifier le moment.";
      } finally {
        this._loading = false;
        this.render();
      }
    }


async _saveDayTypeName() {
  const input =
    this.shadowRoot.querySelector(
      "#day-type-name"
    );

  const name =
    input?.value?.trim();

  if (
    !name ||
    !this._editingDayTypeId
  ) {
    return;
  }

  this._loading = true;
  this._error = null;

  try {
    await this._api.updateDayType(
      this._editingDayTypeId,
      name
    );

    this._configuration =
      await this._api.getConfiguration();

    this._loadedMonthKey = null;

    this._editingDayTypeName = false;
    this._editingDayTypeId = null;
  } catch (error) {
    console.error(
      "Day Planner day type update error",
      error
    );

    this._error =
      error?.message ||
      "Impossible de modifier le type de journée.";
  } finally {
    this._loading = false;
    this.render();
  }
}

_openCreateDayTypeDialog() {
  this._creatingDayType = true;
  this.render();
}


_renderCreateDayTypeDialog() {
  if (!this._creatingDayType) {
    return "";
  }

  return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-day-type-dialog-title"
      >
        <div
          id="create-day-type-dialog-title"
          class="modal-title"
        >
          Créer un type de journée
        </div>

        <label class="modal-field">
          <span>Identifiant</span>

          <input
            id="new-day-type-id"
            type="text"
            placeholder="ex : jour_maison"
          />
        </label>

        <label class="modal-field">
          <span>Libellé</span>

          <input
            id="new-day-type-name"
            type="text"
            placeholder="ex : Journée Maison"
          />
        </label>

        <div class="modal-actions">
          <button
            id="cancel-create-day-type"
            class="editor-button"
            type="button"
          >
            Annuler
          </button>

          <button
            id="save-create-day-type"
            class="editor-button primary"
            type="button"
          >
            Créer
          </button>
        </div>
      </div>
    </div>
  `;
}

async _saveCreateDayType() {
  const idInput =
    this.shadowRoot.querySelector(
      "#new-day-type-id"
    );

  const nameInput =
    this.shadowRoot.querySelector(
      "#new-day-type-name"
    );

  const dayTypeId =
    idInput?.value?.trim();

  const name =
    nameInput?.value?.trim();

  if (!dayTypeId || !name) {
    return;
  }

  this._loading = true;
  this._error = null;

  try {
    await this._api.addDayType(
      dayTypeId,
      name
    );

    this._configuration =
      await this._api.getConfiguration();

    this._selectedDayTypeId =
      dayTypeId;

    this._loadedMonthKey = null;
    this._creatingDayType = false;
  } catch (error) {
    console.error(
      "Day Planner add day type error",
      error
    );

    this._error =
      error?.message ||
      "Impossible de créer le type de journée.";
  } finally {
    this._loading = false;
    this.render();
  }
}

  render() {
    if (!this._hass) {
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        ${styles}

        .tabs {
          display: flex;
          gap: 4px;
          padding:
            10px 16px 0;
          border-bottom:
            1px solid
            var(--divider-color);
        }

        .tab {
          border: 0;
          background: transparent;
          color:
            var(--secondary-text-color);
          cursor: pointer;
          padding: 10px 14px;
          border-bottom:
            2px solid transparent;
          font: inherit;
        }

        .tab.active {
          color:
            var(--primary-color);
          border-bottom-color:
            var(--primary-color);
        }
      </style>

      <ha-card>
        ${this._renderTabs()}

        <div class="container">
          ${
            this._activeTab ===
              "calendar"
              ? `
                <div class="header">
                  <div class="title">
                    Day Planner
                  </div>

                  <div
                    class="month-navigation"
                  >
                    <button
                      id="previous-month"
                      class="navigation-button"
                      type="button"
                    >
                      <ha-icon
                        icon="mdi:chevron-left"
                      ></ha-icon>
                    </button>

                    <div
                      class="month-label"
                    >
                      ${escapeHtml(
                        this._monthLabel()
                      )}
                    </div>

                    <button
                      id="next-month"
                      class="navigation-button"
                      type="button"
                    >
                      <ha-icon
                        icon="mdi:chevron-right"
                      ></ha-icon>
                    </button>
                  </div>
                </div>
              `
              : ""
          }

          ${
            this._loading
              ? `
                <div class="loading">
                  Chargement…
                </div>
              `
              : this._error
                ? `
                  <div class="error">
                    ${escapeHtml(
                      this._error
                    )}
                  </div>
                `
                : this._renderActiveView()
	  }
        </div>
      </ha-card>

      ${this._renderDayTypeNameDialog()}
      ${this._renderScheduledMomentDialog()}
      ${this._renderCreateDayTypeDialog()}
      ${this._renderDeleteDayTypeDialog()}

    `;

    this._bindEvents();
  }

  _editScheduledMoment(
    momentId,
    time
  ) {
    this._editingScheduledMoment = {
      dayTypeId:
        this._selectedDayTypeId,
      momentId,
      time,
    };

    this.render();
  }

  _editDayTypeName(dayTypeId) {
    this._editingDayTypeId = dayTypeId;
    this._editingDayTypeName = true;

    this.render();
  }

_openDeleteDayTypeDialog(
  dayTypeId
) {
  this._deletingDayTypeId =
    dayTypeId;

  this.render();
}
_renderDeleteDayTypeDialog() {
  if (!this._deletingDayTypeId) {
    return "";
  }

  const dayType =
    this._configuration?.day_types?.find(
      (item) =>
        item.id ===
        this._deletingDayTypeId
    );

  if (!dayType) {
    return "";
  }

  return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-day-type-dialog-title"
      >
        <div
          id="delete-day-type-dialog-title"
          class="modal-title"
        >
          Supprimer le type de journée
        </div>

        <div class="modal-message">
          Supprimer
          <strong>
            ${escapeHtml(
              dayType.name
            )}
          </strong>
          ?
        </div>

        <div class="modal-actions">
          <button
            id="cancel-delete-day-type"
            class="editor-button"
            type="button"
          >
            Annuler
          </button>

          <button
            id="confirm-delete-day-type"
            class="editor-button danger"
            type="button"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  `;
}

async _deleteDayType() {
  const dayTypeId =
    this._deletingDayTypeId;

  if (!dayTypeId) {
    return;
  }

  this._loading = true;
  this._error = null;

  try {
    await this._api.removeDayType(
      dayTypeId
    );

    this._configuration =
      await this._api.getConfiguration();

    this._deletingDayTypeId = null;

    const remaining =
      this._configuration.day_types || [];

    this._selectedDayTypeId =
      remaining[0]?.id ?? null;

    this._loadedMonthKey = null;
  } catch (error) {
    console.error(
      "Day Planner remove day type error",
      error
    );

    this._error =
      error?.message ||
      "Impossible de supprimer le type de journée.";
  } finally {
    this._loading = false;
    this.render();
  }
}

_renderDayTypeNameDialog() {
  if (!this._editingDayTypeName) {
    return "";
  }

  const dayType =
    this._configuration?.day_types?.find(
      (item) =>
        item.id === this._editingDayTypeId
    );

  if (!dayType) {
    return "";
  }

  return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="day-type-dialog-title"
      >
        <div
          id="day-type-dialog-title"
          class="modal-title"
        >
          Modifier le type de journée
        </div>

        <label class="modal-field">
          <span>Libellé</span>

          <input
            id="day-type-name"
            type="text"
            value="${escapeHtml(
              dayType.name
            )}"
          />
        </label>

        <div class="modal-actions">
          <button
            id="cancel-day-type-name"
            class="editor-button"
            type="button"
          >
            Annuler
          </button>

          <button
            id="save-day-type-name"
            class="editor-button primary"
            type="button"
          >
            Enregistrer
          </button>
        </div>
      </div>
    </div>
  `;
}
}


customElements.define(
  "day-planner-card",
  DayPlannerCard
);

console.info(
  "%c DAY-PLANNER-CARD %c v0.0.2b",
  "color: orange; font-weight: bold; background: black",
  "color: white; font-weight: bold; background: dimgray"
);

window.customCards =
  window.customCards || [];

window.customCards.push({
  type: "day-planner-card",
  name: "Day Planner",
  description:
    "Graphical Day Planner configuration card",
});
