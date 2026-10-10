import { DayPlannerApi } from './api.js';
import {
  escapeHtml,
  formatDate,
  formatLongDate,
  getLanguage,
  countActionSequenceTargets,
} from './utils.js';
import { styles } from './styles.js';
import { DayPlannerI18n } from './i18n.js';
import { renderCalendarView } from './views/calendar-view.js';
import { renderWeekSchedulesView } from './views/week-schedules-view.js';
import { renderDayTypesView } from './views/day-types-view.js';
import { renderCyclesView } from './views/cycles-view.js';
import { renderMomentsView } from './views/moments-view.js';

function validateCycleStartDate(startDate, cycles, currentCycleId = null, t) {
  const startDateObject = new Date(`${startDate}T00:00:00`);

  if (!startDate || Number.isNaN(startDateObject.getTime())) {
    return t('errors.invalid_date', 'Date invalide.');
  }

  if (startDateObject.getDay() !== 1) {
    return t('errors.cycle_start_monday', 'La date de début d’un cycle doit être un lundi.');
  }

  const duplicate = cycles.some(
    (cycle) => cycle.start_date === startDate && cycle.id !== currentCycleId
  );

  if (duplicate) {
    return t('errors.duplicate_cycle_start_date', 'Un autre cycle commence déjà à cette date.');
  }

  return null;
}

class DayPlannerCard extends HTMLElement {
  constructor() {
    super();

    this.attachShadow({
      mode: 'open',
    });

    this._hass = null;
    this._config = {};
    this._i18n = null;
    this._api = null;

    this._activeTab = 'calendar';

    const now = new Date();

    this._displayYear = now.getFullYear();

    this._displayMonth = now.getMonth();

    this._selectedDate = formatDate(now);

    this._calendar = null;
    this._configuration = null;

    this._loading = false;
    this._error = null;
    this._loadedMonthKey = null;
    this._selectedDayTypeId = null;

    this._editingScheduledMoment = null;
    this._deletingScheduledMoment = null;

    this._editingDayTypeName = false;
    this._editingDayTypeId = null;

    this._creatingDayType = false;
    this._deletingDayTypeId = null;

    this._creatingScheduledMoment = false;
    this._creatingScheduledMomentDayTypeId = null;

    this._creatingWeekSchedule = false;
    this._expandedWeekScheduleIds = new Set();
    this._editingWeekScheduleId = null;
    this._deletingWeekScheduleId = null;

    this._creatingCycle = false;
    this._editingCycleId = null;
    this._deletingCycleId = null;

    this._creatingCalendarException = false;
    this._creatingCalendarExceptionDate = null;
    this._editingCalendarExceptionId = null;
    this._deletingCalendarExceptionId = null;

    this._creatingMomentAction = false;
    this._newMomentActionSequence = [];

    this._editingMomentActionId = null;

    this._editingMomentActionSequence = [];
    this._editingMomentActionsId = null;
    this._deletingMomentActionId = null;

    this._creatingMoment = false;
    this._editingMomentId = null;
    this._deletingMomentId = null;
    this._expandedMomentIds = new Set();

    this._serviceLocalize = null;
    this._serviceTranslationsLoading = false;
  }

  setConfig(config) {
    this._config = config || {};

    this.style.display = 'block';
    this.style.width = '100%';
  }

  set hass(hass) {
    this._hass = hass;

    if (!this._api) {
      this._api = new DayPlannerApi(hass);
    } else {
      this._api.setHass(hass);
    }

    if (
      !this._serviceLocalize &&
      !this._serviceTranslationsLoading &&
      typeof hass.loadBackendTranslation === 'function'
    ) {
      this._serviceTranslationsLoading = true;

      hass
        .loadBackendTranslation('services')
        .then((localize) => {
          this._serviceLocalize = localize;
        })
        .catch((error) => {
          console.error('Day Planner service translations error', error);
        })
        .finally(() => {
          this._serviceTranslationsLoading = false;

          if (this._activeTab === 'moments') {
            this.render();
          }
        });
    }

    const monthKey = `${this._displayYear}-${String(this._displayMonth + 1).padStart(2, '0')}`;

    if (this._activeTab === 'calendar' && !this._loading && this._loadedMonthKey !== monthKey) {
      this._loadCalendar();
      return;
    }

    if (!this._i18n) {
      this._i18n = new DayPlannerI18n(hass);

      this._i18n
        .load()
        .then(() => {
          this.render();
        })
        .catch((error) => {
          console.error('Day Planner i18n error', error);
        });
    } else {
      this._i18n.setHass(hass);
    }

    /*
     * Ne pas rerendre la carte pendant qu'une fenêtre
     * d'édition est ouverte.
     */
    if (
      this._editingScheduledMoment ||
      this._editingDayTypeName ||
      this._creatingDayType ||
      this._deletingDayTypeId ||
      this._creatingScheduledMoment ||
      this._deletingScheduledMoment ||
      this._creatingWeekSchedule ||
      this._editingWeekScheduleId ||
      this._deletingWeekScheduleId ||
      this._creatingCycle ||
      this._deletingCycleId ||
      this._creatingCalendarException ||
      this._editingCalendarExceptionId ||
      this._deletingCalendarExceptionId ||
      this._creatingMomentAction ||
      this._editingMomentActionId ||
      this._deletingMomentActionId ||
      this._creatingMoment ||
      this._editingMomentId ||
      this._deletingMomentId
    ) {
      return;
    }

    this.render();
  }

  getCardSize() {
    return 8;
  }

  getGridOptions() {
    return {
      columns: 'full',
      rows: 'auto',
    };
  }

  _monthStart() {
    return new Date(this._displayYear, this._displayMonth, 1);
  }

  _monthEnd() {
    return new Date(this._displayYear, this._displayMonth + 1, 0);
  }

  async _loadCalendar() {
    if (this._configuration === null) {
      await this._loadConfiguration();
    }

    if (!this._hass) {
      return;
    }

    this._loading = true;
    this._error = null;

    this.render();

    try {
      const startDate = formatDate(this._monthStart());

      const endDate = formatDate(this._monthEnd());

      this._calendar = await this._api.getCalendar(startDate, endDate);

      this._loadedMonthKey = `${this._displayYear}-${String(this._displayMonth + 1).padStart(
        2,
        '0'
      )}`;

      const exists = this._calendar.days.some((day) => day.date === this._selectedDate);

      if (!exists) {
        this._selectedDate = this._calendar.days[0]?.date ?? null;
      }
    } catch (error) {
      console.error('Day Planner calendar error', error);

      this._error = error?.message || 'Impossible de charger le calendrier.';
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

    return this._calendar.days.find((day) => day.date === this._selectedDate) || null;
  }

  _monthLabel() {
    const language = getLanguage(this._hass);

    return new Intl.DateTimeFormat(language, {
      month: 'long',
      year: 'numeric',
    }).format(this._monthStart());
  }

  async _setActiveTab(tab) {
    this._activeTab = tab;

    this._error = null;

    if (
      (tab === 'day_types' || tab === 'week_schedules' || tab === 'cycles' || tab === 'moments') &&
      this._configuration === null
    ) {
      await this._loadConfiguration();
      return;
    }

    if (tab === 'calendar' && !this._loading) {
      await this._loadCalendar();
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
      this._configuration = await this._api.getConfiguration();

      if (this._selectedDayTypeId === null && this._configuration.day_types?.length) {
        this._selectedDayTypeId = this._configuration.day_types[0].id;
      }
    } catch (error) {
      console.error('Day Planner configuration error', error);

      this._error = error?.message || 'Impossible de charger la configuration.';
    } finally {
      this._loading = false;
      this.render();
    }
  }

  _renderTabs() {
    return /* html */ `
      <div class="tabs">
        <button
          class="tab ${this._activeTab === 'calendar' ? 'active' : ''}"
          data-tab="calendar"
          type="button"
        >
          Calendrier
        </button>

<button
  class="tab ${this._activeTab === 'week_schedules' ? 'active' : ''}"
  data-tab="week_schedules"
  type="button"
>
  Semaines types
</button>
<button
  class="tab ${this._activeTab === 'cycles' ? 'active' : ''}"
  data-tab="cycles"
  type="button"
>
  ${escapeHtml(this._i18n?.t('cycles.title', 'Cycles') ?? 'Cycles')}
</button>


        <button
          class="tab ${this._activeTab === 'day_types' ? 'active' : ''}"
          data-tab="day_types"
          type="button"
        >
          Types de journée
        </button>
<button
  class="tab ${this._activeTab === 'moments' ? 'active' : ''}"
  data-tab="moments"
  type="button"
>
  Moments
</button>

      </div>
    `;
  }

  _renderActiveView() {
    switch (this._activeTab) {
      case 'week_schedules':
        return renderWeekSchedulesView(this);

      case 'cycles':
        return renderCyclesView(this);

      case 'day_types':
        return renderDayTypesView(this);

      case 'moments':
        return renderMomentsView(this);

      case 'calendar':
      default:
        return renderCalendarView(this);
    }
  }

  _bindEvents() {
    this.shadowRoot
      .querySelector('#previous-month')
      ?.addEventListener('click', () => this._previousMonth());

    this.shadowRoot
      .querySelector('#next-month')
      ?.addEventListener('click', () => this._nextMonth());

    this.shadowRoot.querySelectorAll('.day[data-date]').forEach((element) => {
      element.addEventListener('click', () => {
        this._selectDate(element.dataset.date);
      });
    });

    this.shadowRoot.querySelectorAll('.tab[data-tab]').forEach((element) => {
      element.addEventListener('click', () => {
        this._setActiveTab(element.dataset.tab);
      });
    });

    this.shadowRoot.querySelectorAll('.day-type-item[data-day-type-id]').forEach((element) => {
      element.addEventListener('click', () => {
        this._selectedDayTypeId = element.dataset.dayTypeId;

        this.render();
      });
    });

    this.shadowRoot
      .querySelectorAll('.timeline-marker.editable[data-moment-id]')
      .forEach((element) => {
        element.addEventListener('click', () => {
          this._editScheduledMoment(element.dataset.momentId, element.dataset.time);
        });
      });
    this.shadowRoot.querySelector('#cancel-scheduled-moment')?.addEventListener('click', () => {
      this._editingScheduledMoment = null;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelector('#save-scheduled-moment')?.addEventListener('click', async () => {
      await this._saveScheduledMoment();
    });

    this.shadowRoot.querySelectorAll('.edit-day-type-name[data-day-type-id]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.stopPropagation();

        this._editDayTypeName(element.dataset.dayTypeId);
      });
    });

    this.shadowRoot.querySelector('#cancel-day-type-name')?.addEventListener('click', () => {
      this._editingDayTypeName = false;
      this._editingDayTypeId = null;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelector('#save-day-type-name')?.addEventListener('click', async () => {
      await this._saveDayTypeName();
    });

    this.shadowRoot.querySelector('#add-day-type')?.addEventListener('click', () => {
      this._openCreateDayTypeDialog();
    });

    this.shadowRoot.querySelector('#cancel-create-day-type')?.addEventListener('click', () => {
      this._creatingDayType = false;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelector('#save-create-day-type')?.addEventListener('click', async () => {
      await this._saveCreateDayType();
    });

    this.shadowRoot
      .querySelector('#confirm-delete-day-type')
      ?.addEventListener('click', async () => {
        await this._deleteDayType();
      });
    this.shadowRoot.querySelectorAll('.delete-day-type[data-day-type-id]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.stopPropagation();

        this._openDeleteDayTypeDialog(element.dataset.dayTypeId);
      });
    });

    this.shadowRoot.querySelector('#cancel-delete-day-type')?.addEventListener('click', () => {
      this._deletingDayTypeId = null;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelector('.add-scheduled-moment')?.addEventListener('click', (event) => {
      event.stopPropagation();

      this._creatingScheduledMomentDayTypeId = event.currentTarget.dataset.dayTypeId;

      this._error = null;
      this._creatingScheduledMoment = true;

      this.render();
    });

    this.shadowRoot
      .querySelector('#cancel-create-scheduled-moment')
      ?.addEventListener('click', () => {
        this._creatingScheduledMoment = false;
        this._creatingScheduledMomentDayTypeId = null;
        this._error = null;
        this.render();
      });

    this.shadowRoot
      .querySelector('#save-create-scheduled-moment')
      ?.addEventListener('click', async () => {
        await this._saveCreateScheduledMoment();
      });
    this.shadowRoot.querySelector('#delete-scheduled-moment')?.addEventListener('click', () => {
      this._openDeleteScheduledMomentDialog();
    });

    this.shadowRoot
      .querySelector('#cancel-delete-scheduled-moment')
      ?.addEventListener('click', () => {
        this._deletingScheduledMoment = null;
        this._error = null;
        this.render();
      });

    this.shadowRoot
      .querySelector('#confirm-delete-scheduled-moment')
      ?.addEventListener('click', async () => {
        await this._deleteScheduledMoment();
      });

    this.shadowRoot.querySelector('#add-week-schedule')?.addEventListener('click', () => {
      this._creatingWeekSchedule = true;
      this.render();
    });

    this.shadowRoot.querySelector('#cancel-create-week-schedule')?.addEventListener('click', () => {
      this._creatingWeekSchedule = false;
      this._error = null;
      this.render();
    });

    this.shadowRoot
      .querySelector('#save-create-week-schedule')
      ?.addEventListener('click', async () => {
        await this._saveCreateWeekSchedule();
      });

    this.shadowRoot
      .querySelectorAll('.toggle-week-schedule[data-week-schedule-id]')
      .forEach((element) => {
        element.addEventListener('click', (event) => {
          event.stopPropagation();

          this._toggleWeekSchedule(element.dataset.weekScheduleId);
        });
      });

    this.shadowRoot
      .querySelectorAll('.edit-week-schedule[data-week-schedule-id]')
      .forEach((element) => {
        element.addEventListener('click', (event) => {
          event.stopPropagation();

          this._editingWeekScheduleId = element.dataset.weekScheduleId;

          this.render();
        });
      });

    this.shadowRoot.querySelector('#cancel-edit-week-schedule')?.addEventListener('click', () => {
      this._editingWeekScheduleId = null;
      this._error = null;
      this.render();
    });

    this.shadowRoot
      .querySelector('#save-edit-week-schedule')
      ?.addEventListener('click', async () => {
        await this._saveEditWeekSchedule();
      });

    this.shadowRoot
      .querySelectorAll('.delete-week-schedule[data-week-schedule-id]')
      .forEach((element) => {
        element.addEventListener('click', (event) => {
          event.stopPropagation();

          this._deletingWeekScheduleId = element.dataset.weekScheduleId;

          this.render();
        });
      });

    this.shadowRoot.querySelector('#cancel-delete-week-schedule')?.addEventListener('click', () => {
      this._deletingWeekScheduleId = null;
      this._error = null;
      this.render();
    });

    this.shadowRoot
      .querySelector('#confirm-delete-week-schedule')
      ?.addEventListener('click', async () => {
        await this._deleteWeekSchedule();
      });

    this.shadowRoot.querySelector('#add-cycle')?.addEventListener('click', () => {
      this._creatingCycle = true;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelector('#cancel-create-cycle')?.addEventListener('click', () => {
      this._creatingCycle = false;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelector('#save-create-cycle')?.addEventListener('click', async () => {
      await this._saveCreateCycle();
    });

    this.shadowRoot.querySelectorAll('.edit-cycle[data-cycle-id]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.stopPropagation();

        this._error = null;

        this._editingCycleId = element.dataset.cycleId;

        this.render();
      });
    });

    this.shadowRoot.querySelectorAll('.delete-cycle[data-cycle-id]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.stopPropagation();

        this._deletingCycleId = element.dataset.cycleId;

        this.render();
      });
    });

    this.shadowRoot.querySelector('#cancel-edit-cycle')?.addEventListener('click', () => {
      this._editingCycleId = null;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelector('#save-edit-cycle')?.addEventListener('click', async () => {
      await this._saveEditCycle();
    });

    this.shadowRoot.querySelector('#cancel-delete-cycle')?.addEventListener('click', () => {
      this._deletingCycleId = null;
      this.render();
    });

    this.shadowRoot.querySelector('#confirm-delete-cycle')?.addEventListener('click', async () => {
      await this._deleteCycle();
    });

    this.shadowRoot.querySelectorAll('.delete-cycle[data-cycle-id]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.stopPropagation();

        this._deletingCycleId = element.dataset.cycleId;

        this.render();
      });
    });

    this.shadowRoot.querySelector('.add-calendar-exception')?.addEventListener('click', (event) => {
      event.stopPropagation();

      this._creatingCalendarExceptionDate = event.currentTarget.dataset.date;

      this._creatingCalendarException = true;
      this._error = null;

      this.render();
    });

    this.shadowRoot
      .querySelector('.edit-calendar-exception')
      ?.addEventListener('click', (event) => {
        event.stopPropagation();

        this._editingCalendarExceptionId = event.currentTarget.dataset.calendarExceptionId;

        this._error = null;

        this.render();
      });

    this.shadowRoot
      .querySelector('.delete-calendar-exception')
      ?.addEventListener('click', (event) => {
        event.stopPropagation();

        this._deletingCalendarExceptionId = event.currentTarget.dataset.calendarExceptionId;

        this._error = null;

        this.render();
      });

    this.shadowRoot
      .querySelector('#cancel-create-calendar-exception')
      ?.addEventListener('click', () => {
        this._creatingCalendarException = false;
        this._creatingCalendarExceptionDate = null;
        this._error = null;

        this.render();
      });

    this.shadowRoot
      .querySelector('#save-create-calendar-exception')
      ?.addEventListener('click', async () => {
        await this._saveCreateCalendarException();
      });

    this.shadowRoot
      .querySelector('#cancel-edit-calendar-exception')
      ?.addEventListener('click', () => {
        this._editingCalendarExceptionId = null;
        this._error = null;
        this.render();
      });

    this.shadowRoot
      .querySelector('#save-edit-calendar-exception')
      ?.addEventListener('click', async () => {
        await this._saveEditCalendarException();
      });

    this.shadowRoot
      .querySelector('#cancel-delete-calendar-exception')
      ?.addEventListener('click', () => {
        this._deletingCalendarExceptionId = null;
        this._error = null;
        this.render();
      });

    this.shadowRoot
      .querySelector('#confirm-delete-calendar-exception')
      ?.addEventListener('click', async () => {
        await this._deleteCalendarException();
      });

    this.shadowRoot.querySelector('#close-moment-actions')?.addEventListener('click', () => {
      this._editingMomentActionsId = null;

      this.render();
    });

    this.shadowRoot.querySelector('#add-moment-action')?.addEventListener('click', async () => {
      await this._ensureActionSelectorLoaded();

      this._creatingMomentAction = true;
      this._newMomentActionSequence = [];

      this.render();
    });

    this.shadowRoot.querySelector('#cancel-create-moment-action')?.addEventListener('click', () => {
      this._creatingMomentAction = false;
      this._newMomentActionSequence = [];

      this.render();
    });

    this.shadowRoot
      .querySelector('#save-create-moment-action')
      ?.addEventListener('click', async () => {
        await this._saveCreateMomentAction();
      });

    const actionSelector = this.shadowRoot.querySelector('#moment-action-sequence');

    if (actionSelector) {
      actionSelector.hass = this._hass;

      actionSelector.selector = {
        action: {},
      };
      actionSelector.value = this._newMomentActionSequence || [];

      actionSelector.addEventListener('value-changed', (event) => {
        const value = event.detail?.value || [];

        this._newMomentActionSequence = value;

        queueMicrotask(() => {
          if (actionSelector.isConnected) {
            actionSelector.value = value;
          }
        });
      });
    }

    const editActionSelectorContainer = this.shadowRoot.querySelector(
      '#edit-moment-action-sequence-container'
    );

    if (editActionSelectorContainer && this._editingMomentActionId) {
      const editActionSelector = document.createElement('ha-selector');

      editActionSelector.id = 'edit-moment-action-sequence';

      editActionSelector.hass = this._hass;

      editActionSelector.selector = {
        action: {},
      };

      editActionSelector.value = structuredClone(this._editingMomentActionSequence || []);

      editActionSelector.addEventListener('value-changed', (event) => {
        const value = event.detail?.value || [];

        this._editingMomentActionSequence = value;

        queueMicrotask(() => {
          if (editActionSelector.isConnected) {
            editActionSelector.value = value;
          }
        });
      });

      editActionSelectorContainer.appendChild(editActionSelector);
    }

    this.shadowRoot.querySelector('#cancel-edit-moment-action')?.addEventListener('click', () => {
      this._editingMomentActionId = null;
      this._editingMomentActionSequence = [];
      this._error = null;

      this.render();
    });

    this.shadowRoot
      .querySelector('#save-edit-moment-action')
      ?.addEventListener('click', async () => {
        await this._saveEditMomentAction();
      });

    this.shadowRoot
      .querySelectorAll('.manage-moment-actions[data-moment-id]')
      .forEach((element) => {
        element.addEventListener('click', () => {
          this._editingMomentActionsId = element.dataset.momentId;

          this.render();
        });
      });

    this.shadowRoot.querySelectorAll('.edit-moment-action[data-action-id]').forEach((element) => {
      element.addEventListener('click', async (event) => {
        event.stopPropagation();

        const moment = this._configuration?.moments?.find(
          (item) => item.id === this._editingMomentActionsId
        );

        const action = moment?.actions?.find((item) => item.id === element.dataset.actionId);

        if (!action) {
          return;
        }

        await this._ensureActionSelectorLoaded();

        this._editingMomentActionId = action.id;

        this._editingMomentActionSequence = structuredClone(action.sequence || []);

        this._error = null;

        this.render();
      });
    });

    this.shadowRoot.querySelectorAll('.delete-moment-action[data-action-id]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.stopPropagation();

        this._deletingMomentActionId = element.dataset.actionId;

        this._error = null;

        this.render();
      });
    });

    this.shadowRoot.querySelector('#cancel-delete-moment-action')?.addEventListener('click', () => {
      this._deletingMomentActionId = null;
      this._error = null;

      this.render();
    });

    this.shadowRoot
      .querySelector('#confirm-delete-moment-action')
      ?.addEventListener('click', async () => {
        await this._deleteMomentAction();
      });

    this.shadowRoot
      .querySelectorAll('.toggle-moment-details[data-moment-id]')
      .forEach((element) => {
        element.addEventListener('click', (event) => {
          event.stopPropagation();

          const momentId = element.dataset.momentId;

          if (this._expandedMomentIds.has(momentId)) {
            this._expandedMomentIds.delete(momentId);
          } else {
            this._expandedMomentIds.add(momentId);
          }

          this.render();
        });
      });

    this.shadowRoot.querySelector('#add-moment')?.addEventListener('click', () => {
      this._creatingMoment = true;

      this.render();
    });

    this.shadowRoot.querySelectorAll('.edit-moment[data-moment-id]').forEach((element) => {
      element.addEventListener('click', () => {
        this._editingMomentId = element.dataset.momentId;

        this.render();
      });
    });

    this.shadowRoot.querySelectorAll('.delete-moment[data-moment-id]').forEach((element) => {
      element.addEventListener('click', () => {
        this._deletingMomentId = element.dataset.momentId;

        this.render();
      });
    });

    this.shadowRoot.querySelector('#cancel-create-moment')?.addEventListener('click', () => {
      this._creatingMoment = false;

      this.render();
    });

    this.shadowRoot.querySelector('#save-create-moment')?.addEventListener('click', async () => {
      await this._saveCreateMoment();
    });

    this.shadowRoot.querySelector('#cancel-edit-moment')?.addEventListener('click', () => {
      this._editingMomentId = null;

      this.render();
    });

    this.shadowRoot.querySelector('#save-edit-moment')?.addEventListener('click', async () => {
      await this._saveEditMoment();
    });

    this.shadowRoot.querySelector('#cancel-delete-moment')?.addEventListener('click', () => {
      this._deletingMomentId = null;

      this.render();
    });

    this.shadowRoot.querySelector('#confirm-delete-moment')?.addEventListener('click', async () => {
      await this._deleteMoment();
    });

    const newMomentIconPicker = this.shadowRoot.querySelector('#new-moment-icon');

    if (newMomentIconPicker) {
      newMomentIconPicker.hass = this._hass;
      newMomentIconPicker.value = '';

      newMomentIconPicker.addEventListener('value-changed', (event) => {
        newMomentIconPicker.value = event.detail?.value || '';
      });
    }

    const editMomentIconPicker = this.shadowRoot.querySelector('#edit-moment-icon');

    if (editMomentIconPicker && this._editingMomentId) {
      const moment = this._configuration?.moments?.find(
        (item) => item.id === this._editingMomentId
      );

      editMomentIconPicker.hass = this._hass;
      editMomentIconPicker.value = moment?.icon || '';

      editMomentIconPicker.addEventListener('value-changed', (event) => {
        editMomentIconPicker.value = event.detail?.value || '';
      });
    }
    /* fin de _bindEvents */
  }

  async _saveEditMomentAction() {
    const momentId = this._editingMomentActionsId;
    const actionId = this._editingMomentActionId;

    if (!momentId || !actionId) {
      return;
    }

    const label = this.shadowRoot.querySelector('#edit-moment-action-label')?.value?.trim();

    const sequence = this._editingMomentActionSequence || [];

    if (!label) {
      return;
    }

    if (sequence.length === 0) {
      this._error =
        this._i18n?.t(
          'moments.action_group_requires_action',
          'Ajoutez au moins une action Home Assistant.'
        ) ?? 'Ajoutez au moins une action Home Assistant.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.updateMomentAction(momentId, actionId, label, sequence);

      this._configuration = await this._api.getConfiguration();

      this._editingMomentActionId = null;
      this._editingMomentActionSequence = [];

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner update moment action error', error);

      this._error =
        error?.message ||
        (this._i18n?.t(
          'moments.update_action_group_error',
          "Impossible de modifier le groupe d'actions."
        ) ??
          "Impossible de modifier le groupe d'actions.");
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _deleteMomentAction() {
    const momentId = this._editingMomentActionsId;
    const actionId = this._deletingMomentActionId;

    if (!momentId || !actionId) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.removeMomentAction(momentId, actionId);

      this._configuration = await this._api.getConfiguration();

      this._deletingMomentActionId = null;

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner remove moment action error', error);

      this._error =
        error?.message ||
        (this._i18n?.t(
          'moments.delete_action_group_error',
          "Impossible de supprimer le groupe d'actions."
        ) ??
          "Impossible de supprimer le groupe d'actions.");
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _ensureActionSelectorLoaded() {
    if (customElements.get('ha-automation-action')) {
      return;
    }

    const selector = document.createElement('ha-selector');

    selector.hass = this._hass;
    selector.selector = {
      action: {},
    };
    selector.value = [];

    selector.style.display = 'none';

    document.body.appendChild(selector);

    try {
      await customElements.whenDefined('ha-automation-action');
    } finally {
      selector.remove();
    }
  }

  async _saveEditWeekSchedule() {
    const weekScheduleId = this._editingWeekScheduleId;

    if (!weekScheduleId) {
      return;
    }

    const getValue = (id) => this.shadowRoot.querySelector(`#${id}`)?.value?.trim();

    const name = getValue('edit-week-schedule-name');

    const monday = getValue('edit-week-schedule-monday');

    const tuesday = getValue('edit-week-schedule-tuesday');

    const wednesday = getValue('edit-week-schedule-wednesday');

    const thursday = getValue('edit-week-schedule-thursday');

    const friday = getValue('edit-week-schedule-friday');

    const saturday = getValue('edit-week-schedule-saturday');

    const sunday = getValue('edit-week-schedule-sunday');

    if (
      !name ||
      !monday ||
      !tuesday ||
      !wednesday ||
      !thursday ||
      !friday ||
      !saturday ||
      !sunday
    ) {
      this._error = 'Tous les champs de la semaine type sont obligatoires.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.updateWeekSchedule(
        weekScheduleId,
        name,
        monday,
        tuesday,
        wednesday,
        thursday,
        friday,
        saturday,
        sunday
      );

      this._editingWeekScheduleId = null;

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner update week schedule error', error);

      this._error = error?.message || 'Impossible de modifier la semaine type.';
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _deleteWeekSchedule() {
    const weekScheduleId = this._deletingWeekScheduleId;

    if (!weekScheduleId) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.removeWeekSchedule(weekScheduleId);

      this._deletingWeekScheduleId = null;

      this._expandedWeekScheduleIds.delete(weekScheduleId);

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner remove week schedule error', error);

      const message = error?.message || '';

      if (message === 'Cannot remove a week schedule used by a cycle') {
        this._error =
          'Impossible de supprimer cette semaine type : elle est utilisée par un cycle.';
      } else if (message.startsWith('Week schedule not found:')) {
        this._error = "Impossible de supprimer cette semaine type : elle n'existe plus.";
      } else {
        this._error = 'Impossible de supprimer la semaine type.';
      }

      this._deletingWeekScheduleId = null;
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _deleteScheduledMoment() {
    const deleting = this._deletingScheduledMoment;

    if (!deleting) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.removeScheduledMoment(deleting.dayTypeId, deleting.momentId);

      this._deletingScheduledMoment = null;

      this._configuration = await this._api.getConfiguration();

      // Forcer le prochain chargement du calendrier.
      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner remove scheduled moment error', error);

        this._error =
          error?.message ||
          (this._i18n?.t(
            'day_types.delete_scheduled_moment_error',
            'Impossible de supprimer le moment.'
          ) ?? 'Impossible de supprimer le moment.');
    } finally {
      this._loading = false;
      this.render();
    }
  }

  _renderScheduledMomentDialog() {
    const editing = this._editingScheduledMoment;

    if (!editing) {
      return '';
    }
    const moment = this._configuration?.moments?.find((item) => item.id === editing.momentId);

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
              ${escapeHtml(
                this._i18n?.t(
                  'day_types.edit_scheduled_moment',
                  'Modifier le moment'
                ) ?? 'Modifier le moment'
              )}
            </div>

          ${
            this._error
              ? /* html */ `
                  <div class="modal-error">
                    ${escapeHtml(this._error)}
                  </div>
                `
              : ''
          }
            <div class="modal-moment-name">
              ${
                moment?.icon
                  ? `
                    <ha-icon
                      icon="${escapeHtml(moment.icon)}"
                    ></ha-icon>
                  `
                  : ''
              }

              <strong>
                ${escapeHtml(moment?.name || editing.momentId)}
              </strong>
            </div>

            <label class="modal-field">
              <span>
                ${escapeHtml(
                  this._i18n?.t(
                    'day_types.time',
                    'Heure'
                  ) ?? 'Heure'
                )}
              </span>

              <input
                id="scheduled-moment-time"
                type="time"
                value="${escapeHtml(editing.time)}"
              />
            </label>

            <div class="modal-actions">
              <button
                id="cancel-scheduled-moment"
                class="editor-button"
                type="button"
              >
                ${escapeHtml(
                  this._i18n?.t(
                    'common.cancel',
                    'Annuler'
                  ) ?? 'Annuler'
                )}
              </button>

              <button
                id="delete-scheduled-moment"
                class="danger-button"
                type="button"
              >
                ${escapeHtml(
                  this._i18n?.t(
                    'common.delete',
                    'Supprimer'
                  ) ?? 'Supprimer'
                )}
              </button>

              <button
                id="save-scheduled-moment"
                class="editor-button primary"
                type="button"
              >
                ${escapeHtml(
                  this._i18n?.t(
                    'common.save',
                    'Enregistrer'
                  ) ?? 'Enregistrer'
                )}
              </button>
            </div>
          </div>
        </div>
      `;
  }

  /* fin de _renderScheduledMomentDialog */

  _renderMomentActionsDialog() {
    const momentId = this._editingMomentActionsId;

    if (
      !momentId ||
      this._creatingMomentAction ||
      this._editingMomentActionId ||
      this._deletingMomentActionId
    ) {
      return '';
    }

    const moment = this._configuration?.moments?.find((item) => item.id === momentId);

    if (!moment) {
      return '';
    }

    const actions = moment.actions || [];

    return `
      <div class="modal-backdrop">
        <div
          class="modal-dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="moment-actions-dialog-title"
        >
          <div
            id="moment-actions-dialog-title"
            class="modal-title"
          >
            ${escapeHtml(
              this._i18n?.t('moments.action_groups_title', "Groupes d'actions du moment") ??
                "Groupes d'actions du moment"
            )}
          </div>
  
          <div class="modal-moment-name">
            ${
              moment.icon
                ? `
                  <ha-icon
                    icon="${escapeHtml(moment.icon)}"
                  ></ha-icon>
                `
                : ''
            }
  
            <strong>
              ${escapeHtml(moment.name)}
            </strong>
          </div>
  
          ${
            actions.length === 0
              ? `
                <div class="empty-state">
                  ${escapeHtml(
                    this._i18n?.t(
                      'moments.no_action_group_configured',
                      "Aucun groupe d'actions configuré."
                    ) ?? "Aucun groupe d'actions configuré."
                  )}
                </div>
              `
              : `
                <div class="moment-actions-list">
                  ${actions
                    .map((action) => {
                      const actionCount = countActionSequenceTargets(action.sequence);

                      return `
                        <div
                          class="moment-action-item"
                          data-action-id="${escapeHtml(action.id)}"
                        >

                          <div class="moment-action-text">
                            <strong>
                              ${escapeHtml(action.label || action.id)}
                            </strong>

                            <span class="moment-action-id">
                              ${escapeHtml(action.id)}
                            </span>
                          </div>
 
                          <span class="moment-action-count">
                            ${actionCount}
                            ${escapeHtml(
                              this._i18n?.t(
                                actionCount === 1 ? 'moments.action' : 'moments.actions_count',
                                actionCount === 1 ? 'action' : 'actions'
                              ) ?? (actionCount === 1 ? 'action' : 'actions')
                            )}
                          </span>

                          <div class="moment-action-buttons">
                            <button
                              class="icon-button edit-moment-action"
                              data-action-id="${escapeHtml(action.id)}"
                              type="button"
                              title="${escapeHtml(
                                this._i18n?.t(
                                  'moments.edit_action_group',
                                  "Modifier le groupe d'actions"
                                ) ?? "Modifier le groupe d'actions"
                              )}"
                              aria-label="${escapeHtml(
                                this._i18n?.t(
                                  'moments.edit_action_group',
                                  "Modifier le groupe d'actions"
                                ) ?? "Modifier le groupe d'actions"
                              )}"
                            >
                              <ha-icon icon="mdi:pencil"></ha-icon>
                            </button>

                            <button
                              class="icon-button danger delete-moment-action"
                              data-action-id="${escapeHtml(action.id)}"
                              type="button"
                              title="${escapeHtml(
                                this._i18n?.t(
                                  'moments.delete_action_group',
                                  "Supprimer le groupe d'actions"
                                ) ?? "Supprimer le groupe d'actions"
                              )}"
                              aria-label="${escapeHtml(
                                this._i18n?.t(
                                  'moments.delete_action_group',
                                  "Supprimer le groupe d'actions"
                                ) ?? "Supprimer le groupe d'actions"
                              )}"
                            >
                              <ha-icon icon="mdi:close"></ha-icon>
                            </button>
                          </div>

                        </div>
                      `;
                    })
                    .join('')}
                </div>
              `
          }
  
          <div class="modal-actions">
            <button
              id="close-moment-actions"
              class="editor-button"
              type="button"
            >
              ${escapeHtml(this._i18n?.t('common.back', 'Retour') ?? 'Retour')}
            </button>

            <button
              id="add-moment-action"
              class="editor-button primary"
              type="button"
            >
              ${escapeHtml(
                this._i18n?.t('moments.add_action_group', "Ajouter un groupe d'actions") ??
                  "Ajouter un groupe d'actions"
              )}
            </button>
        </div>
       </div>
     </div>
  `;
  }

  _renderCreateMomentActionDialog() {
    if (!this._creatingMomentAction) {
      return '';
    }

    const moment = this._configuration?.moments?.find(
      (item) => item.id === this._editingMomentActionsId
    );

    if (!moment) {
      return '';
    }

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-moment-action-dialog-title"
      >
        <div
          id="create-moment-action-dialog-title"
          class="modal-title"
        >
          ${escapeHtml(
            this._i18n?.t('moments.add_action_group', "Ajouter un groupe d'actions") ??
              "Ajouter un groupe d'actions"
          )}
        </div>

        <div class="modal-moment-name">
          ${
            moment.icon
              ? `
                <ha-icon
                  icon="${escapeHtml(moment.icon)}"
                ></ha-icon>
              `
              : ''
          }

          <strong>
            ${escapeHtml(moment.name)}
          </strong>
        </div>

        <label class="modal-field">
          <span>
            ${escapeHtml(this._i18n?.t('moments.action_group_id', 'Identifiant') ?? 'Identifiant')}
          </span>

          <input
            id="new-moment-action-id"
            type="text"
            placeholder="ex: allumer_salon"
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(this._i18n?.t('moments.action_group_label', 'Libellé') ?? 'Libellé')}
          </span>

          <input
            id="new-moment-action-label"
            type="text"
            placeholder="ex: Ouvrir les volets du matin"
          />
        </label>


        <div class="modal-field">
          <span>
            ${escapeHtml(
              this._i18n?.t('moments.home_assistant_actions', 'Actions Home Assistant') ??
                'Actions Home Assistant'
            )}
          </span>

          <ha-selector
            id="moment-action-sequence"
          ></ha-selector>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-create-moment-action"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.cancel', 'Annuler') ?? 'Annuler')}
          </button>

          <button
            id="save-create-moment-action"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.save', 'Enregistrer') ?? 'Enregistrer')}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  _renderEditMomentActionDialog() {
    const actionId = this._editingMomentActionId;

    if (!actionId) {
      return '';
    }

    const moment = this._configuration?.moments?.find(
      (item) => item.id === this._editingMomentActionsId
    );

    const action = moment?.actions?.find((item) => item.id === actionId);

    if (!moment || !action) {
      return '';
    }

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-moment-action-dialog-title"
      >
        <div
          id="edit-moment-action-dialog-title"
          class="modal-title"
        >
          ${escapeHtml(
            this._i18n?.t('moments.edit_action_group', "Modifier le groupe d'actions") ??
              "Modifier le groupe d'actions"
          )}
        </div>

        <div class="modal-moment-name">
          ${
            moment.icon
              ? `
                  <ha-icon
                    icon="${escapeHtml(moment.icon)}"
                  ></ha-icon>
                `
              : ''
          }

          <strong>
            ${escapeHtml(moment.name)}
          </strong>
        </div>

        <div class="modal-field">
          <span>
            ${escapeHtml(this._i18n?.t('moments.action_group_id', 'Identifiant') ?? 'Identifiant')}
          </span>

          <strong>
            ${escapeHtml(action.id)}
          </strong>
        </div>

        <label class="modal-field">
          <span>
            ${escapeHtml(this._i18n?.t('moments.action_group_label', 'Libellé') ?? 'Libellé')}
          </span>

          <input
            id="edit-moment-action-label"
            type="text"
            value="${escapeHtml(action.label || action.id)}"
          />
        </label>

        <div class="modal-field">
          <span>
            ${escapeHtml(
              this._i18n?.t('moments.home_assistant_actions', 'Actions Home Assistant') ??
                'Actions Home Assistant'
            )}
          </span>

          <div
            id="edit-moment-action-sequence-container"
          ></div>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-edit-moment-action"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.cancel', 'Annuler') ?? 'Annuler')}
          </button>

          <button
            id="save-edit-moment-action"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.save', 'Enregistrer') ?? 'Enregistrer')}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  _renderDeleteMomentActionDialog() {
    const actionId = this._deletingMomentActionId;

    if (!actionId) {
      return '';
    }

    const moment = this._configuration?.moments?.find(
      (item) => item.id === this._editingMomentActionsId
    );

    const action = moment?.actions?.find((item) => item.id === actionId);

    if (!moment || !action) {
      return '';
    }

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-moment-action-dialog-title"
      >
        <div
          id="delete-moment-action-dialog-title"
          class="modal-title"
        >
          ${escapeHtml(
            this._i18n?.t('moments.delete_action_group', "Supprimer le groupe d'actions") ??
              "Supprimer le groupe d'actions"
          )}
        </div>

        <div class="modal-moment-name">
          ${
            moment.icon
              ? `
                  <ha-icon
                    icon="${escapeHtml(moment.icon)}"
                  ></ha-icon>
                `
              : ''
          }

          <strong>
            ${escapeHtml(moment.name)}
          </strong>
        </div>

        <div class="modal-message">
          ${escapeHtml(
            this._i18n?.t(
              'moments.delete_action_group_confirm',
              "Voulez-vous vraiment supprimer ce groupe d'actions ?"
            ) ?? "Voulez-vous vraiment supprimer ce groupe d'actions ?"
          )}
        </div>

        <div class="modal-message">
          <strong>
            ${escapeHtml(action.label || action.id)}
          </strong>

          <span class="moment-action-id">
            ${escapeHtml(action.id)}
          </span>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-delete-moment-action"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.cancel', 'Annuler') ?? 'Annuler')}
          </button>

          <button
            id="confirm-delete-moment-action"
            class="editor-button danger"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.delete', 'Supprimer') ?? 'Supprimer')}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  _renderCreateMomentDialog() {
    if (!this._creatingMoment) {
      return '';
    }

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-moment-dialog-title"
      >
        <div class="modal-dialog-content">
          <div
            id="create-moment-dialog-title"
            class="modal-title"
          >
            ${escapeHtml(this._i18n?.t('moments.add', 'Ajouter un moment') ?? 'Ajouter un moment')}
          </div>

          <label class="modal-field">
            <span>
              ${escapeHtml(this._i18n?.t('moments.id', 'Identifiant') ?? 'Identifiant')}
            </span>

            <input
              id="new-moment-id"
              type="text"
              placeholder="ex: wake_up"
            />
          </label>

          <label class="modal-field">
            <span>
              ${escapeHtml(this._i18n?.t('moments.name', 'Libellé') ?? 'Libellé')}
            </span>

            <input
              id="new-moment-name"
              type="text"
              placeholder="ex: Réveil"
            />
          </label>

          <div class="modal-field">
            <span>
              ${escapeHtml(this._i18n?.t('moments.icon', 'Icône') ?? 'Icône')}
            </span>

              <ha-icon-picker
                id="new-moment-icon"
              ></ha-icon-picker>
          </div>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-create-moment"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.cancel', 'Annuler') ?? 'Annuler')}
          </button>

          <button
            id="save-create-moment"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.save', 'Enregistrer') ?? 'Enregistrer')}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  _renderEditMomentDialog() {
    if (!this._editingMomentId) {
      return '';
    }

    const moment = this._configuration?.moments?.find((item) => item.id === this._editingMomentId);

    if (!moment) {
      return '';
    }

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-moment-dialog-title"
      >
        <div class="modal-dialog-content">
          <div
            id="edit-moment-dialog-title"
            class="modal-title"
          >
            ${escapeHtml(
              this._i18n?.t('moments.edit', 'Modifier le moment') ?? 'Modifier le moment'
            )}
          </div>

          <div class="modal-field">
            <span>
              ${escapeHtml(this._i18n?.t('moments.id', 'Identifiant') ?? 'Identifiant')}
            </span>

            <strong>
              ${escapeHtml(moment.id)}
            </strong>
          </div>

          <label class="modal-field">
            <span>
              ${escapeHtml(this._i18n?.t('moments.name', 'Libellé') ?? 'Libellé')}
            </span>

            <input
              id="edit-moment-name"
              type="text"
              value="${escapeHtml(moment.name)}"
            />
          </label>

          <label class="modal-field">
            <span>
              ${escapeHtml(this._i18n?.t('moments.icon', 'Icône') ?? 'Icône')}
            </span>

              <ha-icon-picker
                id="edit-moment-icon"
              ></ha-icon-picker>
          </label>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-edit-moment"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.cancel', 'Annuler') ?? 'Annuler')}
          </button>

          <button
            id="save-edit-moment"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.save', 'Enregistrer') ?? 'Enregistrer')}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  _renderDeleteMomentDialog() {
    if (!this._deletingMomentId) {
      return '';
    }

    const moment = this._configuration?.moments?.find((item) => item.id === this._deletingMomentId);

    if (!moment) {
      return '';
    }

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-moment-dialog-title"
      >
        <div
          id="delete-moment-dialog-title"
          class="modal-title"
        >
          ${escapeHtml(this._i18n?.t('common.delete', 'Supprimer') ?? 'Supprimer')}
        </div>

        <div class="modal-message">
          ${escapeHtml(
            this._i18n?.t('moments.delete_confirm', 'Voulez-vous vraiment supprimer ce moment ?') ??
              'Voulez-vous vraiment supprimer ce moment ?'
          )}

          <strong>
            ${escapeHtml(moment.name)}
          </strong>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-delete-moment"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(this._i18n?.t('common.cancel', 'Annuler') ?? 'Annuler')}
          </button>

          <button
            id="confirm-delete-moment"
            class="editor-button danger"
            type="button"
          >
           ${escapeHtml(this._i18n?.t('common.delete', 'Supprimer') ?? 'Supprimer')}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  async _saveScheduledMoment() {
    const editing = this._editingScheduledMoment;

    if (!editing) {
      return;
    }

    const input = this.shadowRoot.querySelector('#scheduled-moment-time');

    const time = input?.value;

    if (!time) {
      this._error =
        this._i18n?.t(
          'day_types.time_required',
          'Veuillez renseigner une heure.'
        ) ?? 'Veuillez renseigner une heure.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    this.render();

    try {
      await this._api.updateScheduledMoment(editing.dayTypeId, editing.momentId, time);

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;

      this._editingScheduledMoment = null;
    } catch (error) {
      console.error('Day Planner scheduled moment update error', error);

      this._error =
        error?.message ||
        (this._i18n?.t(
          'day_types.update_scheduled_moment_error',
          'Impossible de modifier le moment.'
        ) ?? 'Impossible de modifier le moment.');

    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveDayTypeName() {
    const input = this.shadowRoot.querySelector('#day-type-name');

    const name = input?.value?.trim();

    if (!this._editingDayTypeId) {
      return;
    }

    if (!name) {
      this._error =
        this._i18n?.t(
          'day_types.required_fields',
          'Veuillez renseigner tous les champs obligatoires.'
        ) ?? 'Veuillez renseigner tous les champs obligatoires.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.updateDayType(this._editingDayTypeId, name);

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;

      this._editingDayTypeName = false;
      this._editingDayTypeId = null;
    } catch (error) {
      console.error('Day Planner day type update error', error);

      this._error =
        error?.message ||
        (this._i18n?.t(
          'day_types.update_error',
          'Impossible de modifier le type de journée.'
        ) ?? 'Impossible de modifier le type de journée.');

    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveCreateMomentAction() {
    const momentId = this._editingMomentActionsId;

    const actionId = this.shadowRoot.querySelector('#new-moment-action-id')?.value?.trim();

    const label = this.shadowRoot.querySelector('#new-moment-action-label')?.value?.trim();

    const sequence = this._newMomentActionSequence || [];

    if (!momentId || !actionId || !label) {
      return;
    }

    if (sequence.length === 0) {
      this._error =
        this._i18n?.t(
          'moments.action_group_requires_action',
          'Ajoutez au moins une action Home Assistant.'
        ) ?? 'Ajoutez au moins une action Home Assistant.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.addMomentAction(momentId, actionId, label, sequence);

      this._configuration = await this._api.getConfiguration();

      this._creatingMomentAction = false;
      this._newMomentActionSequence = [];

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner add moment action error', error);

      this._error =
        error?.message ||
        (this._i18n?.t(
          'moments.add_action_group_error',
          "Impossible d'ajouter le groupe d'actions."
        ) ??
          "Impossible d'ajouter le groupe d'actions.");
    } finally {
      this._loading = false;
      this.render();
    }
  }

  _openCreateDayTypeDialog() {
    this._error = null;
    this._creatingDayType = true;
    this.render();
  }

  _renderCreateDayTypeDialog() {
    if (!this._creatingDayType) {
      return '';
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
          ${escapeHtml(
            this._i18n?.t(
              'day_types.add',
              'Ajouter un type de journée'
            ) ?? 'Ajouter un type de journée'
          )}
        </div>
        ${
          this._error
            ? /* html */ `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }
        <label class="modal-field">
          <span>
            ${escapeHtml(
              this._i18n?.t(
                'day_types.id',
                'Identifiant'
              ) ?? 'Identifiant'
            )}
          </span>

          <input
            id="new-day-type-id"
            type="text"
            placeholder="ex : jour_maison"
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(
              this._i18n?.t(
                'day_types.name',
                'Libellé'
              ) ?? 'Libellé'
            )}
          </span>

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
            ${escapeHtml(
              this._i18n?.t(
                'common.cancel',
                'Annuler'
              ) ?? 'Annuler'
            )}
          </button>

          <button
            id="save-create-day-type"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.create',
                'Créer'
              ) ?? 'Créer'
            )}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  _renderCreateScheduledMomentDialog() {
    if (!this._creatingScheduledMoment || !this._creatingScheduledMomentDayTypeId) {
      return '';
    }

    const moments = this._configuration?.moments || [];

    const dayType = this._configuration?.day_types?.find(
      (item) => item.id === this._creatingScheduledMomentDayTypeId
    );

    const usedMomentIds = new Set((dayType?.scheduled_moments || []).map((item) => item.moment_id));

    const availableMoments = moments.filter((moment) => !usedMomentIds.has(moment.id));

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(
            this._i18n?.t(
              'day_types.add_scheduled_moment',
              'Ajouter un moment'
            ) ?? 'Ajouter un moment'
          )}
        </div>

        ${
          this._error
            ? /* html */ `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }

        ${
          availableMoments.length
            ? `
              <label class="modal-field">
                <span>
                  ${escapeHtml(
                    this._i18n?.t(
                      'day_types.moment',
                      'Moment'
                    ) ?? 'Moment'
                  )}
                </span>

                <select id="scheduled-moment-id">
                  ${availableMoments
                    .map(
                      (moment) => `
                        <option
                          value="${escapeHtml(moment.id)}"
                        >
                          ${escapeHtml(moment.name)}
                        </option>
                      `
                    )
                    .join('')}
                </select>
              </label>

              <label class="modal-field">
                <span>
                  ${escapeHtml(
                    this._i18n?.t(
                      'day_types.time',
                      'Heure'
                    ) ?? 'Heure'
                  )}
                </span>

                <input
                  id="new-scheduled-moment-time"
                  type="time"
                  value="08:00"
                  required
                >
              </label>
            `
            : `
              <div>
                ${escapeHtml(
                  this._i18n?.t(
                    'day_types.all_moments_used',
                    'Tous les moments sont déjà utilisés dans ce type de journée.'
                  ) ?? 'Tous les moments sont déjà utilisés dans ce type de journée.'
                )}
              </div>
            `
        }

        <div class="modal-actions">
          <button
            id="cancel-create-scheduled-moment"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.cancel',
                'Annuler'
              ) ?? 'Annuler'
            )}
          </button>

          ${
            availableMoments.length
              ? `
                <button
                  id="save-create-scheduled-moment"
                  type="button"
                >
                  ${escapeHtml(
                    this._i18n?.t(
                      'day_types.add_scheduled_moment',
                      'Ajouter un moment'
                    ) ?? 'Ajouter un moment'
                  )}
                </button>
              `
              : ''
          }
        </div>

      </div>
    </div>
  `;
  }

  async _saveCreateDayType() {
    const idInput = this.shadowRoot.querySelector('#new-day-type-id');

    const nameInput = this.shadowRoot.querySelector('#new-day-type-name');

    const dayTypeId = idInput?.value?.trim();

    const name = nameInput?.value?.trim();

    if (!dayTypeId || !name) {
      this._error =
        this._i18n?.t(
          'day_types.required_fields',
          'Veuillez renseigner tous les champs obligatoires.'
        ) ?? 'Veuillez renseigner tous les champs obligatoires.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.addDayType(dayTypeId, name);

      this._configuration = await this._api.getConfiguration();

      this._selectedDayTypeId = dayTypeId;

      this._loadedMonthKey = null;
      this._creatingDayType = false;
    } catch (error) {
      console.error('Day Planner add day type error', error);

      this._error =
        error?.message ||
        (this._i18n?.t(
          'day_types.add_error',
          "Impossible d'ajouter le type de journée."
        ) ?? "Impossible d'ajouter le type de journée.");

          } finally {
            this._loading = false;
            this.render();
          }
        }

  _toggleWeekSchedule(weekScheduleId) {
    if (this._expandedWeekScheduleIds.has(weekScheduleId)) {
      this._expandedWeekScheduleIds.delete(weekScheduleId);
    } else {
      this._expandedWeekScheduleIds.add(weekScheduleId);
    }

    this.render();
  }

  async _saveCreateWeekSchedule() {
    const getValue = (id) => this.shadowRoot.querySelector(`#${id}`)?.value?.trim();

    const weekScheduleId = getValue('create-week-schedule-id');

    const name = getValue('create-week-schedule-name');

    const monday = getValue('create-week-schedule-monday');

    const tuesday = getValue('create-week-schedule-tuesday');

    const wednesday = getValue('create-week-schedule-wednesday');

    const thursday = getValue('create-week-schedule-thursday');

    const friday = getValue('create-week-schedule-friday');

    const saturday = getValue('create-week-schedule-saturday');

    const sunday = getValue('create-week-schedule-sunday');

    if (
      !weekScheduleId ||
      !name ||
      !monday ||
      !tuesday ||
      !wednesday ||
      !thursday ||
      !friday ||
      !saturday ||
      !sunday
    ) {
      this._error = 'Tous les champs de la semaine type sont obligatoires.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.addWeekSchedule(
        weekScheduleId,
        name,
        monday,
        tuesday,
        wednesday,
        thursday,
        friday,
        saturday,
        sunday
      );

      this._creatingWeekSchedule = false;

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner create week schedule error', error);

      this._error = error?.message || 'Impossible de créer la semaine type.';
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveCreateScheduledMoment() {
    const dayTypeId = this._creatingScheduledMomentDayTypeId;

    const momentId =
      this.shadowRoot.querySelector('#scheduled-moment-id')?.value;

    const time =
      this.shadowRoot.querySelector('#new-scheduled-moment-time')?.value;

    if (!dayTypeId || !momentId || !time) {
      this._error =
        this._i18n?.t(
          'day_types.required_fields',
          'Veuillez renseigner tous les champs obligatoires.'
        ) ?? 'Veuillez renseigner tous les champs obligatoires.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    this.render();

    try {
      await this._api.addScheduledMoment(
        dayTypeId,
        momentId,
        time
      );

      this._creatingScheduledMoment = false;
      this._creatingScheduledMomentDayTypeId = null;

      await this._loadConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error(
        'Day Planner add scheduled moment error',
        error
      );

      this._error =
        error?.message ||
        (this._i18n?.t(
          'day_types.add_scheduled_moment_error',
          "Impossible d'ajouter le moment."
        ) ?? "Impossible d'ajouter le moment.");
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveCreateCycle() {
    const getValue = (id) => this.shadowRoot.querySelector(`#${id}`)?.value?.trim();

    const cycleId = getValue('create-cycle-id');

    const name = getValue('create-cycle-name');

    const startDate = getValue('create-cycle-start-date');

    const validationError = validateCycleStartDate(
      startDate,
      this._configuration?.cycles || [],
      null,
      (key, fallback) => this._i18n?.t(key, fallback) ?? fallback
    );

    if (validationError) {
      this._error = validationError;
      this.render();
      return;
    }
    const weekScheduleIds = [
      getValue('create-cycle-week-1'),
      getValue('create-cycle-week-2'),
      getValue('create-cycle-week-3'),
      getValue('create-cycle-week-4'),
    ].filter(Boolean);

    if (
      !cycleId ||
      !name ||
      !startDate ||
      weekScheduleIds.length < 1 ||
      weekScheduleIds.length > 4
    ) {
      this._error =
        this._i18n?.t(
          'errors.invalid_week_count',
          'Un cycle doit contenir entre 1 et 4 semaines types.'
        ) ?? 'Un cycle doit contenir entre 1 et 4 semaines types.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.addCycle(cycleId, name, startDate, weekScheduleIds);

      this._creatingCycle = false;

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner create cycle error', error);

      const message = error?.message || '';

      if (message === 'Invalid start date format') {
        this._error =
          this._i18n?.t('errors.invalid_start_date', 'La date de début est invalide.') ??
          'La date de début est invalide.';
      } else if (message === 'A cycle must contain between 1 and 4 week schedules') {
        this._error =
          this._i18n?.t(
            'errors.invalid_week_count',
            'Un cycle doit contenir entre 1 et 4 semaines types.'
          ) ?? 'Un cycle doit contenir entre 1 et 4 semaines types.';
      } else if (message.startsWith('Duplicate cycle start date:')) {
        this._error =
          this._i18n?.t(
            'errors.duplicate_cycle_start_date',
            'Un autre cycle commence déjà à cette date.'
          ) ?? 'Un autre cycle commence déjà à cette date.';
      } else {
        this._error =
          this._i18n?.t('errors.generic', 'Une erreur est survenue.') ?? 'Une erreur est survenue.';
      }
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveEditCycle() {
    const cycleId = this._editingCycleId;

    if (!cycleId) {
      return;
    }

    const getValue = (id) => this.shadowRoot.querySelector(`#${id}`)?.value?.trim();

    const name = getValue('edit-cycle-name');

    const startDate = getValue('edit-cycle-start-date');

    const validationError = validateCycleStartDate(
      startDate,
      this._configuration?.cycles || [],
      cycleId,
      (key, fallback) => this._i18n?.t(key, fallback) ?? fallback
    );

    if (validationError) {
      this._error = validationError;
      this.render();
      return;
    }

    const weekScheduleIds = [
      getValue('edit-cycle-week-1'),
      getValue('edit-cycle-week-2'),
      getValue('edit-cycle-week-3'),
      getValue('edit-cycle-week-4'),
    ].filter(Boolean);

    if (!name || !startDate || weekScheduleIds.length < 1 || weekScheduleIds.length > 4) {
      this._error =
        this._i18n?.t(
          'errors.invalid_week_count',
          'Un cycle doit contenir entre 1 et 4 semaines types.'
        ) ?? 'Un cycle doit contenir entre 1 et 4 semaines types.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.updateCycle(cycleId, name, startDate, weekScheduleIds);

      this._editingCycleId = null;

      this._configuration = await this._api.getConfiguration();

      // Le cycle peut modifier la résolution
      // des jours du calendrier.
      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner update cycle error', error);

      const message = error?.message || '';

      if (message === 'Invalid start date format') {
        this._error =
          this._i18n?.t('errors.invalid_start_date', 'La date de début est invalide.') ??
          'La date de début est invalide.';
      } else if (message === 'A cycle must contain between 1 and 4 week schedules') {
        this._error =
          this._i18n?.t(
            'errors.invalid_week_count',
            'Un cycle doit contenir entre 1 et 4 semaines types.'
          ) ?? 'Un cycle doit contenir entre 1 et 4 semaines types.';
      } else if (message.startsWith('Duplicate cycle start date:')) {
        this._error =
          this._i18n?.t(
            'errors.duplicate_cycle_start_date',
            'Un autre cycle commence déjà à cette date.'
          ) ?? 'Un autre cycle commence déjà à cette date.';
      } else {
        this._error =
          error?.message ||
          this._i18n?.t('errors.generic', 'Une erreur est survenue.') ||
          'Une erreur est survenue.';
      }
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
            this._activeTab === 'calendar'
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
                      ${escapeHtml(this._monthLabel())}
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
              : ''
          }
${
  this._loading
    ? `
        <div class="loading">
          Chargement…
        </div>
      `
    : `
        ${
          this._error
            ? `
              <div class="error">
                ${escapeHtml(this._error)}
              </div>
            `
            : ''
        }

        ${this._renderActiveView()}
      `
}

      </ha-card>

      ${this._renderDayTypeNameDialog()}
      ${this._renderScheduledMomentDialog()}
      ${this._renderCreateDayTypeDialog()}
      ${this._renderDeleteDayTypeDialog()}
      ${this._renderCreateScheduledMomentDialog()}
      ${this._renderDeleteScheduledMomentDialog()}
      ${this._renderCreateWeekScheduleDialog()}
      ${this._renderEditWeekScheduleDialog()}
      ${this._renderDeleteWeekScheduleDialog()}
      ${this._renderCreateCycleDialog()}
      ${this._renderEditCycleDialog()}
      ${this._renderDeleteCycleDialog()}
      ${this._renderCreateCalendarExceptionDialog()}
      ${this._renderEditCalendarExceptionDialog()}
      ${this._renderDeleteCalendarExceptionDialog()}
      ${this._renderMomentActionsDialog()}
      ${this._renderCreateMomentActionDialog()}
      ${this._renderEditMomentActionDialog()}
      ${this._renderDeleteMomentActionDialog()}
      ${this._renderCreateMomentDialog()}
      ${this._renderEditMomentDialog()}
      ${this._renderDeleteMomentDialog()}

    `;

    this._bindEvents();
  }

  _editScheduledMoment(momentId, time) {
    this._error = null;
    this._editingScheduledMoment = {
      dayTypeId: this._selectedDayTypeId,
      momentId,
      time,
    };

    this.render();
  }

  _editDayTypeName(dayTypeId) {
    this._error = null;
    this._editingDayTypeId = dayTypeId;
    this._editingDayTypeName = true;

    this.render();
  }

  _openDeleteDayTypeDialog(dayTypeId) {
    this._error = null;
    this._deletingDayTypeId = dayTypeId;

    this.render();
  }
  _renderDeleteDayTypeDialog() {
    if (!this._deletingDayTypeId) {
      return '';
    }

    const dayType = this._configuration?.day_types?.find(
      (item) => item.id === this._deletingDayTypeId
    );

    if (!dayType) {
      return '';
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
            ${escapeHtml(
              this._i18n?.t(
                'day_types.delete',
                'Supprimer le type de journée'
              ) ?? 'Supprimer le type de journée'
            )}
        </div>

        ${
          this._error
            ? /* html */ `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }

        <div class="modal-message">
          ${escapeHtml(
            this._i18n?.t(
              'day_types.delete_confirm',
              'Voulez-vous vraiment supprimer ce type de journée ?'
            ) ?? 'Voulez-vous vraiment supprimer ce type de journée ?'
          )}
          <strong>
            ${escapeHtml(dayType.name)}
          </strong>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-delete-day-type"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.cancel',
                'Annuler'
              ) ?? 'Annuler'
            )}
          </button>

          <button
            id="confirm-delete-day-type"
            class="editor-button danger"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.delete',
                'Supprimer'
              ) ?? 'Supprimer'
            )}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  async _deleteDayType() {
    const dayTypeId = this._deletingDayTypeId;

    if (!dayTypeId) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.removeDayType(dayTypeId);

      this._configuration = await this._api.getConfiguration();

      this._deletingDayTypeId = null;

      const remaining = this._configuration.day_types || [];

      this._selectedDayTypeId = remaining[0]?.id ?? null;

      this._loadedMonthKey = null;
    } catch (error) {
      console.error('Day Planner remove day type error', error);

      this._error =
        error?.message ||
        (this._i18n?.t(
          'day_types.delete_error',
          'Impossible de supprimer le type de journée.'
        ) ?? 'Impossible de supprimer le type de journée.');

    } finally {
      this._loading = false;
      this.render();
    }
  }

  _renderDayTypeNameDialog() {
    if (!this._editingDayTypeName) {
      return '';
    }

    const dayType = this._configuration?.day_types?.find(
      (item) => item.id === this._editingDayTypeId
    );

    if (!dayType) {
      return '';
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
          ${escapeHtml(
            this._i18n?.t(
              'day_types.edit',
              'Modifier le type de journée'
            ) ?? 'Modifier le type de journée'
          )}
        </div>
        ${
          this._error
            ? /* html */ `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }

        <label class="modal-field">
          <span>
            ${escapeHtml(
              this._i18n?.t(
                'day_types.name',
                'Libellé'
              ) ?? 'Libellé'
            )}
          </span>

          <input
            id="day-type-name"
            type="text"
            value="${escapeHtml(dayType.name)}"
          />
        </label>

        <div class="modal-actions">
          <button
            id="cancel-day-type-name"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.cancel',
                'Annuler'
              ) ?? 'Annuler'
            )}
          </button>

          <button
            id="save-day-type-name"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.save',
                'Enregistrer'
              ) ?? 'Enregistrer'
            )}
          </button>
        </div>
      </div>
    </div>
  `;
  }

  _openDeleteScheduledMomentDialog() {
    if (!this._editingScheduledMoment) {
      return;
    }
    this._error = null;

    this._deletingScheduledMoment = {
      ...this._editingScheduledMoment,
    };

    this._editingScheduledMoment = null;

    this.render();
  }

  _renderDeleteScheduledMomentDialog() {
    const deleting = this._deletingScheduledMoment;

    if (!deleting) {
      return '';
    }

    const moment = this._configuration?.moments?.find((item) => item.id === deleting.momentId);

    const name = moment?.name || deleting.momentId;

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(
            this._i18n?.t(
              'day_types.delete_scheduled_moment',
              'Supprimer le moment'
            ) ?? 'Supprimer le moment'
          )}
        </div>
        ${
          this._error
            ? /* html */ `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }

        <div class="modal-message">
          ${escapeHtml(
            this._i18n?.t(
              'day_types.delete_scheduled_moment_confirm',
              'Voulez-vous vraiment supprimer ce moment planifié ?'
            ) ?? 'Voulez-vous vraiment supprimer ce moment planifié ?'
          )}
        </div>

        <div class="modal-moment-name">
          ${
            moment?.icon
              ? /* html */ `
                  <ha-icon
                    icon="${escapeHtml(moment.icon)}"
                  ></ha-icon>
                `
              : ''
          }

          <strong>
            ${escapeHtml(name)}
          </strong>
        </div>

        <div class="modal-actions">
          <button
            id="cancel-delete-scheduled-moment"
            class="secondary-button"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.cancel',
                'Annuler'
              ) ?? 'Annuler'
            )}
          </button>

          <button
            id="confirm-delete-scheduled-moment"
            class="danger-button"
            type="button"
          >
            ${escapeHtml(
              this._i18n?.t(
                'common.delete',
                'Supprimer'
              ) ?? 'Supprimer'
            )}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  _renderCreateWeekScheduleDialog() {
    if (!this._creatingWeekSchedule) {
      return '';
    }

    const dayTypes = this._configuration?.day_types || [];

    const renderDayTypeOptions = () =>
      dayTypes
        .map(
          (dayType) => `
          <option value="${escapeHtml(dayType.id)}">
            ${escapeHtml(dayType.name)}
          </option>
        `
        )
        .join('');

    const renderDaySelect = (id, label) => `
    <label class="modal-field">
      <span>${label}</span>

      <select id="${id}">
        ${renderDayTypeOptions()}
      </select>
    </label>
  `;

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          Créer une semaine type
        </div>

        <label class="modal-field">
          <span>Identifiant</span>

          <input
            id="create-week-schedule-id"
            type="text"
            autocomplete="off"
          />
        </label>

        <label class="modal-field">
          <span>Libellé</span>

          <input
            id="create-week-schedule-name"
            type="text"
            autocomplete="off"
          />
        </label>

        ${renderDaySelect('create-week-schedule-monday', 'Lundi')}

        ${renderDaySelect('create-week-schedule-tuesday', 'Mardi')}

        ${renderDaySelect('create-week-schedule-wednesday', 'Mercredi')}

        ${renderDaySelect('create-week-schedule-thursday', 'Jeudi')}

        ${renderDaySelect('create-week-schedule-friday', 'Vendredi')}

        ${renderDaySelect('create-week-schedule-saturday', 'Samedi')}

        ${renderDaySelect('create-week-schedule-sunday', 'Dimanche')}

        <div class="modal-actions">
          <button
            id="cancel-create-week-schedule"
            class="editor-button"
            type="button"
          >
            Annuler
          </button>

          <button
            id="save-create-week-schedule"
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

  _renderEditWeekScheduleDialog() {
    if (!this._editingWeekScheduleId) {
      return '';
    }

    const weekSchedule = this._configuration?.week_schedules?.find(
      (item) => item.id === this._editingWeekScheduleId
    );

    if (!weekSchedule) {
      return '';
    }

    const dayTypes = this._configuration?.day_types || [];

    const renderDayTypeOptions = (selectedId) =>
      dayTypes
        .map(
          (dayType) => `
          <option
            value="${escapeHtml(dayType.id)}"
            ${dayType.id === selectedId ? 'selected' : ''}
          >
            ${escapeHtml(dayType.name)}
          </option>
        `
        )
        .join('');

    const renderDaySelect = (id, label, selectedId) => `
    <label class="modal-field">
      <span>${label}</span>

      <select id="${id}">
        ${renderDayTypeOptions(selectedId)}
      </select>
    </label>
  `;

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          Modifier la semaine type
        </div>

        <label class="modal-field">
          <span>Identifiant</span>

          <input
            type="text"
            value="${escapeHtml(weekSchedule.id)}"
            disabled
          />
        </label>

        <label class="modal-field">
          <span>Libellé</span>

          <input
            id="edit-week-schedule-name"
            type="text"
            value="${escapeHtml(weekSchedule.name)}"
          />
        </label>

        ${renderDaySelect('edit-week-schedule-monday', 'Lundi', weekSchedule.monday)}

        ${renderDaySelect('edit-week-schedule-tuesday', 'Mardi', weekSchedule.tuesday)}

        ${renderDaySelect('edit-week-schedule-wednesday', 'Mercredi', weekSchedule.wednesday)}

        ${renderDaySelect('edit-week-schedule-thursday', 'Jeudi', weekSchedule.thursday)}

        ${renderDaySelect('edit-week-schedule-friday', 'Vendredi', weekSchedule.friday)}

        ${renderDaySelect('edit-week-schedule-saturday', 'Samedi', weekSchedule.saturday)}

        ${renderDaySelect('edit-week-schedule-sunday', 'Dimanche', weekSchedule.sunday)}

        <div class="modal-actions">
          <button
            id="cancel-edit-week-schedule"
            class="editor-button"
            type="button"
          >
            Annuler
          </button>

          <button
            id="save-edit-week-schedule"
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

  _renderEditCycleDialog() {
    const cycleId = this._editingCycleId;

    if (!cycleId) {
      return '';
    }

    const cycle = this._configuration?.cycles?.find((item) => item.id === cycleId);

    if (!cycle) {
      return '';
    }

    const weekSchedules = this._configuration?.week_schedules || [];

    const weekIds = cycle.week_schedule_ids || [];

    const t = (key, fallback) => this._i18n?.t(key, fallback) ?? fallback;

    const renderWeekOptions = (selectedId) =>
      weekSchedules
        .map(
          (weekSchedule) => `
          <option
            value="${escapeHtml(weekSchedule.id)}"
            ${weekSchedule.id === selectedId ? 'selected' : ''}
          >
            ${escapeHtml(weekSchedule.name)}
          </option>
        `
        )
        .join('');

    const renderWeekSelect = (id, label, selectedId, required = false) => `
    <label class="modal-field">
      <span>
        ${escapeHtml(label)}
      </span>

      <select
        id="${id}"
        ${required ? 'required' : ''}
      >
        ${
          required
            ? ''
            : `
              <option
                value=""
                ${!selectedId ? 'selected' : ''}
              >
                —
              </option>
            `
        }

        ${renderWeekOptions(selectedId)}
      </select>
    </label>
  `;

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(t('cycles.edit_title', 'Modifier le cycle'))}
        </div>
${
  this._error
    ? `
      <div class="modal-error">
        ${escapeHtml(this._error)}
      </div>
    `
    : ''
}
        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.id', 'Identifiant'))}
          </span>

          <input
            type="text"
            value="${escapeHtml(cycle.id)}"
            disabled
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.name', 'Libellé'))}
          </span>

          <input
            id="edit-cycle-name"
            type="text"
            value="${escapeHtml(cycle.name)}"
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.start_date', 'Date de début'))}
          </span>

          <input
            id="edit-cycle-start-date"
            type="date"
            value="${escapeHtml(cycle.start_date)}"
          />
        </label>

        ${renderWeekSelect(
          'edit-cycle-week-1',
          `${t('cycles.week', 'Semaine')} 1`,
          weekIds[0],
          true
        )}

        ${renderWeekSelect('edit-cycle-week-2', `${t('cycles.week', 'Semaine')} 2`, weekIds[1])}

        ${renderWeekSelect('edit-cycle-week-3', `${t('cycles.week', 'Semaine')} 3`, weekIds[2])}

        ${renderWeekSelect('edit-cycle-week-4', `${t('cycles.week', 'Semaine')} 4`, weekIds[3])}

        <div class="modal-actions">
          <button
            id="cancel-edit-cycle"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(t('common.cancel', 'Annuler'))}
          </button>

          <button
            id="save-edit-cycle"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(t('common.save', 'Enregistrer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  _renderDeleteCycleDialog() {
    const cycleId = this._deletingCycleId;

    if (!cycleId) {
      return '';
    }

    const cycle = this._configuration?.cycles?.find((item) => item.id === cycleId);

    if (!cycle) {
      return '';
    }

    const t = (key, fallback) => this._i18n?.t(key, fallback) ?? fallback;

    return /* html */ `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(t('cycles.delete_title', 'Supprimer le cycle'))}
        </div>

        <div class="modal-message">
          ${escapeHtml(t('cycles.delete_confirm', 'Voulez-vous vraiment supprimer le cycle'))}

          <strong>
            ${escapeHtml(cycle.name)}
          </strong>
          ?
        </div>

        <div class="modal-actions">
          <button
            id="cancel-delete-cycle"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(t('common.cancel', 'Annuler'))}
          </button>

          <button
            id="confirm-delete-cycle"
            class="editor-button danger"
            type="button"
          >
            ${escapeHtml(t('common.delete', 'Supprimer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  async _deleteCycle() {
    const cycleId = this._deletingCycleId;

    if (!cycleId) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.removeCycle(cycleId);

      this._deletingCycleId = null;

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner remove cycle error', error);

      const message = error?.message || '';

      if (message.startsWith('Cycle not found:')) {
        this._error =
          this._i18n?.t('errors.cycle_not_found', "Ce cycle n'existe plus.") ??
          "Ce cycle n'existe plus.";
      } else {
        this._error =
          this._i18n?.t('errors.generic', 'Une erreur est survenue.') ?? 'Une erreur est survenue.';
      }

      this._deletingCycleId = null;
    } finally {
      this._loading = false;
      this.render();
    }
  }

  _renderDeleteWeekScheduleDialog() {
    if (!this._deletingWeekScheduleId) {
      return '';
    }

    const weekSchedule = this._configuration?.week_schedules?.find(
      (item) => item.id === this._deletingWeekScheduleId
    );

    if (!weekSchedule) {
      return '';
    }

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          Supprimer la semaine type
        </div>

        <p>
          Voulez-vous vraiment supprimer
          <strong>
            ${escapeHtml(weekSchedule.name)}
          </strong>
          ?
        </p>

        <div class="modal-actions">
          <button
            id="cancel-delete-week-schedule"
            class="editor-button"
            type="button"
          >
            Annuler
          </button>

          <button
            id="confirm-delete-week-schedule"
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

  _renderCreateCycleDialog() {
    if (!this._creatingCycle) {
      return '';
    }

    const weekSchedules = this._configuration?.week_schedules || [];

    const t = (key, fallback) => this._i18n?.t(key, fallback) ?? fallback;

    const renderWeekOptions = () =>
      weekSchedules
        .map(
          (weekSchedule) => `
          <option
            value="${escapeHtml(weekSchedule.id)}"
          >
            ${escapeHtml(weekSchedule.name)}
          </option>
        `
        )
        .join('');

    const renderWeekSelect = (id, label, required = false) => `
    <label class="modal-field">
      <span>${escapeHtml(label)}</span>

      <select
        id="${id}"
        ${required ? 'required' : ''}
      >
        ${
          required
            ? ''
            : `
              <option value="">
                —
              </option>
            `
        }

        ${renderWeekOptions()}
      </select>
    </label>
  `;

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(t('cycles.create_title', 'Créer un cycle'))}
        </div>
${
  this._error
    ? `
      <div class="modal-error">
        ${escapeHtml(this._error)}
      </div>
    `
    : ''
}
        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.id', 'Identifiant'))}
          </span>

          <input
            id="create-cycle-id"
            type="text"
            autocomplete="off"
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.name', 'Libellé'))}
          </span>

          <input
            id="create-cycle-name"
            type="text"
            autocomplete="off"
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.start_date', 'Date de début'))}
          </span>

          <input
            id="create-cycle-start-date"
            type="date"
          />
        </label>

        ${renderWeekSelect('create-cycle-week-1', `${t('cycles.week', 'Semaine')} 1`, true)}

        ${renderWeekSelect('create-cycle-week-2', `${t('cycles.week', 'Semaine')} 2`)}

        ${renderWeekSelect('create-cycle-week-3', `${t('cycles.week', 'Semaine')} 3`)}

        ${renderWeekSelect('create-cycle-week-4', `${t('cycles.week', 'Semaine')} 4`)}

        <div class="modal-actions">
          <button
            id="cancel-create-cycle"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(t('common.cancel', 'Annuler'))}
          </button>

          <button
            id="save-create-cycle"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(t('common.create', 'Créer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  _renderCreateCalendarExceptionDialog() {
    if (!this._creatingCalendarException || !this._creatingCalendarExceptionDate) {
      return '';
    }

    const date = this._creatingCalendarExceptionDate;

    const dayTypes = this._configuration?.day_types || [];

    const dateLabel = formatLongDate(this._creatingCalendarExceptionDate, this._hass);

    const t = (key, fallback) => this._i18n?.t(key, fallback) ?? fallback;

    return /* html */ `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(t('calendar_exceptions.create_title', 'Créer une exception'))}
        </div>

        ${
          this._error
            ? `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }

<div class="calendar-exception-date">
  <ha-icon
    icon="mdi:calendar"
  ></ha-icon>

  <strong>
    ${escapeHtml(dateLabel)}
  </strong>
</div>

        <div class="editor-field">
          <label for="create-calendar-exception-day-type">
            ${escapeHtml(t('calendar_exceptions.day_type', 'Type de journée'))}
          </label>

          <select
            id="create-calendar-exception-day-type"
          >
            <option value="">
              ${escapeHtml(
                t('calendar_exceptions.select_day_type', 'Sélectionner un type de journée')
              )}
            </option>

            ${dayTypes
              .map(
                (dayType) => `
                  <option
                    value="${escapeHtml(dayType.id)}"
                  >
                    ${escapeHtml(dayType.name)}
                  </option>
                `
              )
              .join('')}
          </select>
        </div>

        <div class="editor-field">
          <label for="create-calendar-exception-description">
            ${escapeHtml(t('calendar_exceptions.description', 'Description'))}
          </label>

          <input
            id="create-calendar-exception-description"
            type="text"
            placeholder="${escapeHtml(t('calendar_exceptions.description_optional', 'Facultatif'))}"
          />
        </div>

        <div class="modal-actions">
          <button
            id="cancel-create-calendar-exception"
            class="editor-button"
            type="button"
          >
            ${escapeHtml(t('common.cancel', 'Annuler'))}
          </button>

          <button
            id="save-create-calendar-exception"
            class="editor-button primary"
            type="button"
          >
            ${escapeHtml(t('common.create', 'Créer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  _renderEditCalendarExceptionDialog() {
    const exceptionId = this._editingCalendarExceptionId;

    if (!exceptionId) {
      return '';
    }

    const calendarException = (this._configuration?.calendar_exceptions || []).find(
      (item) => item.id === exceptionId
    );

    if (!calendarException) {
      return '';
    }

    const dayTypes = this._configuration?.day_types || [];

    const dateLabel = formatLongDate(calendarException.date, this._hass);

    const t = (key, fallback) => this._i18n?.t(key, fallback) ?? fallback;

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(t('calendar_exceptions.edit_title', 'Modifier l’exception'))}
        </div>

        ${
          this._error
            ? `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }

        <div class="calendar-exception-date">
          <ha-icon
            icon="mdi:calendar"
          ></ha-icon>

          <strong>
            ${escapeHtml(dateLabel)}
          </strong>
        </div>

        <div class="editor-field">
          <label
            for="edit-calendar-exception-day-type"
          >
            ${escapeHtml(t('calendar_exceptions.day_type', 'Type de journée'))}
          </label>

          <select
            id="edit-calendar-exception-day-type"
          >
            ${dayTypes
              .map(
                (dayType) => `
                  <option
                    value="${escapeHtml(dayType.id)}"
                    ${dayType.id === calendarException.day_type_id ? 'selected' : ''}
                  >
                    ${escapeHtml(dayType.name)}
                  </option>
                `
              )
              .join('')}
          </select>
        </div>

        <div class="editor-field">
          <label
            for="edit-calendar-exception-description"
          >
            ${escapeHtml(t('calendar_exceptions.description', 'Description'))}
          </label>

          <input
            id="edit-calendar-exception-description"
            type="text"
            value="${escapeHtml(calendarException.description || '')}"
          />
        </div>

        <div class="modal-actions">
          <button
            id="cancel-edit-calendar-exception"
            type="button"
          >
            ${escapeHtml(t('common.cancel', 'Annuler'))}
          </button>

          <button
            id="save-edit-calendar-exception"
            type="button"
          >
            ${escapeHtml(t('common.save', 'Enregistrer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  async _refreshCalendarConfiguration() {
    this._configuration = await this._api.getConfiguration();

    this._loadedMonthKey = null;

    await this._loadCalendar();
  }

  _getGenericErrorMessage() {
    return (
      this._i18n?.t('errors.generic', 'Une erreur est survenue.') ?? 'Une erreur est survenue.'
    );
  }

  async _saveCreateCalendarException() {
    const date = this._creatingCalendarExceptionDate;

    if (!date) {
      return;
    }

    const dayTypeId = this.shadowRoot
      .querySelector('#create-calendar-exception-day-type')
      ?.value?.trim();

    const description =
      this.shadowRoot.querySelector('#create-calendar-exception-description')?.value?.trim() ||
      null;

    if (!dayTypeId) {
      this._error =
        this._i18n?.t(
          'errors.calendar_exception_day_type_required',
          'Veuillez sélectionner un type de journée.'
        ) ?? 'Veuillez sélectionner un type de journée.';

      this.render();
      return;
    }

    const calendarExceptionId = `exception-${date}`;

    this._loading = true;
    this._error = null;

    try {
      await this._api.addCalendarException(calendarExceptionId, date, dayTypeId, description);

      this._creatingCalendarException = false;
      this._creatingCalendarExceptionDate = null;

      await this._refreshCalendarConfiguration();

      return;
    } catch (error) {
      console.error('Day Planner create calendar exception error', error);

      this._error = error?.message || this._getGenericErrorMessage();
    } finally {
      this._loading = false;
    }

    this.render();
  }

  async _saveCreateMoment() {
    const momentId = this.shadowRoot.querySelector('#new-moment-id')?.value?.trim();

    const name = this.shadowRoot.querySelector('#new-moment-name')?.value?.trim();

    const iconPicker = this.shadowRoot.querySelector('#new-moment-icon');

    const iconValue = iconPicker?.value?.trim?.() || '';

    const icon = iconValue || null;

    if (!momentId || !name) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.addMoment(momentId, name, icon);

      this._configuration = await this._api.getConfiguration();

      this._creatingMoment = false;

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner add moment error', error);

      this._error = error?.message || "Impossible d'ajouter le moment.";
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveEditMoment() {
    const momentId = this._editingMomentId;

    const name = this.shadowRoot.querySelector('#edit-moment-name')?.value?.trim();

    const iconPicker = this.shadowRoot.querySelector('#edit-moment-icon');

    const iconValue = iconPicker?.value?.trim?.() || '';

    const icon = iconValue || null;

    if (!momentId || !name) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.updateMoment(momentId, name, icon);

      this._configuration = await this._api.getConfiguration();

      this._editingMomentId = null;

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner update moment error', error);

      this._error = error?.message || 'Impossible de modifier le moment.';
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _deleteMoment() {
    const momentId = this._deletingMomentId;

    if (!momentId) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.removeMoment(momentId);

      this._configuration = await this._api.getConfiguration();

      this._deletingMomentId = null;

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner remove moment error', error);

      this._error = error?.message || 'Impossible de supprimer le moment.';
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveEditCalendarException() {
    const calendarExceptionId = this._editingCalendarExceptionId;

    if (!calendarExceptionId) {
      return;
    }

    const calendarException = (this._configuration?.calendar_exceptions || []).find(
      (item) => item.id === calendarExceptionId
    );

    if (!calendarException) {
      return;
    }

    const dayTypeId = this.shadowRoot
      .querySelector('#edit-calendar-exception-day-type')
      ?.value?.trim();

    const description =
      this.shadowRoot.querySelector('#edit-calendar-exception-description')?.value?.trim() || null;

    if (!dayTypeId) {
      this._error =
        this._i18n?.t(
          'errors.calendar_exception_day_type_required',
          'Veuillez sélectionner un type de journée.'
        ) ?? 'Veuillez sélectionner un type de journée.';

      this.render();
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.updateCalendarException(
        calendarExceptionId,
        calendarException.date,
        dayTypeId,
        description
      );

      this._editingCalendarExceptionId = null;

      await this._refreshCalendarConfiguration();

      return;
    } catch (error) {
      console.error('Day Planner update calendar exception error', error);

      this._error = error?.message || this._getGenericErrorMessage();
    } finally {
      this._loading = false;
    }

    this.render();
  }

  _renderDeleteCalendarExceptionDialog() {
    const exceptionId = this._deletingCalendarExceptionId;

    if (!exceptionId) {
      return '';
    }

    const calendarException = (this._configuration?.calendar_exceptions || []).find(
      (item) => item.id === exceptionId
    );

    if (!calendarException) {
      return '';
    }

    const dateLabel = formatLongDate(calendarException.date, this._hass);

    const t = (key, fallback) => this._i18n?.t(key, fallback) ?? fallback;

    return `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(t('calendar_exceptions.delete_title', 'Supprimer l’exception'))}
        </div>

        ${
          this._error
            ? `
                <div class="modal-error">
                  ${escapeHtml(this._error)}
                </div>
              `
            : ''
        }

        <div class="calendar-exception-date">
          <ha-icon
            icon="mdi:calendar"
          ></ha-icon>

          <strong>
            ${escapeHtml(dateLabel)}
          </strong>
        </div>

        <p>
          ${escapeHtml(
            t('calendar_exceptions.delete_confirm', 'Voulez-vous supprimer cette exception ?')
          )}
        </p>

        <div class="modal-actions">
          <button
            id="cancel-delete-calendar-exception"
            type="button"
          >
            ${escapeHtml(t('common.cancel', 'Annuler'))}
          </button>

          <button
            id="confirm-delete-calendar-exception"
            type="button"
          >
            ${escapeHtml(t('common.delete', 'Supprimer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  async _deleteCalendarException() {
    const calendarExceptionId = this._deletingCalendarExceptionId;

    if (!calendarExceptionId) {
      return;
    }

    this._loading = true;
    this._error = null;

    try {
      await this._api.removeCalendarException(calendarExceptionId);

      this._deletingCalendarExceptionId = null;

      await this._refreshCalendarConfiguration();

      return;
    } catch (error) {
      console.error('Day Planner remove calendar exception error', error);

      this._error = error?.message || this._getGenericErrorMessage();
    } finally {
      this._loading = false;
    }

    this.render();
  }
}

customElements.define('day-planner-card', DayPlannerCard);

console.info(
  '%c DAY-PLANNER-CARD %c v0.0.3',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);

window.customCards = window.customCards || [];

window.customCards.push({
  type: 'day-planner-card',
  name: 'Day Planner',
  description: 'Graphical Day Planner configuration card',
});
