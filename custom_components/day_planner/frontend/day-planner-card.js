import { DayPlannerApi } from './api.js';
import {
  escapeHtml,
  formatDate,
  formatLongDate,
  getLanguage,
  countActionSequenceTargets,
  getDayTypeDependencies,
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
    this._duplicatingDayTypeSourceId = null;
    this._deletingDayTypeId = null;

    this._creatingScheduledMoment = false;
    this._creatingScheduledMomentDayTypeId = null;

    this._creatingWeekSchedule = false;
    this._duplicatingWeekScheduleSourceId = null;
    this._expandedWeekScheduleIds = new Set();
    this._editingWeekScheduleId = null;
    this._deletingWeekScheduleId = null;

    this._creatingCycle = false;
    this._duplicatingCycleSourceId = null;
    this._editingCycleId = null;
    this._deletingCycleId = null;

    this._creatingCalendarException = false;
    this._creatingCalendarExceptionDate = null;
    this._duplicatingCalendarExceptionSourceId = null;
    this._editingCalendarExceptionId = null;
    this._deletingCalendarExceptionId = null;

    this._creatingMomentAction = false;
    this._newMomentActionSequence = [];
    this._duplicatingMomentActionSourceId = null;
    this._creatingMomentActionDraft = null;

    this._editingMomentActionId = null;

    this._editingMomentActionSequence = [];
    this._editingMomentActionsId = null;
    this._deletingMomentActionId = null;

    this._creatingMoment = false;
    this._duplicatingMomentSourceId = null;
    this._creatingMomentDraft = null;
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
      this._editingCycleId ||
      this._deletingCycleId ||
      this._creatingCalendarException ||
      this._editingCalendarExceptionId ||
      this._deletingCalendarExceptionId ||
      this._creatingMomentAction ||
      this._editingMomentActionId ||
      this._editingMomentActionsId ||
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

      const dayTypes = this._configuration.day_types || [];

      if (!dayTypes.some((dayType) => dayType.id === this._selectedDayTypeId)) {
        this._selectedDayTypeId = dayTypes[0]?.id ?? null;
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

    const dayTypeUsageHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    this.shadowRoot.querySelectorAll('.day-type-usage-details').forEach((element) => {
      const summary = element.querySelector('summary');

      element.addEventListener('click', (event) => {
        event.stopPropagation();
        // On desktop the detail opens on hover; do not toggle it on mouse click.
        if (dayTypeUsageHover && event.detail > 0 && event.target.closest('summary')) {
          event.preventDefault();
        }
      });

      if (!dayTypeUsageHover || !summary) {
        return; // Keep native <details> tap-to-toggle behaviour on touch screens.
      }

      element.addEventListener('pointerenter', (event) => {
        if (event.pointerType === 'mouse') {
          element.open = true;
        }
      });
      element.addEventListener('pointerleave', (event) => {
        if (event.pointerType === 'mouse' && !summary.matches(':focus-visible')) {
          element.open = false;
        }
      });
      summary.addEventListener('focus', () => {
        element.open = true; // Tab / Shift+Tab exposes the detail for keyboard users.
      });
      summary.addEventListener('blur', () => {
        if (!element.matches(':hover')) {
          element.open = false;
        }
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

    this.shadowRoot.querySelectorAll('.duplicate-day-type[data-day-type-id]')
      .forEach((element) => {
        element.addEventListener('click', (event) => {
          event.stopPropagation();
          this._openDuplicateDayTypeDialog(element.dataset.dayTypeId);
        });
      });

    this.shadowRoot.querySelector('#cancel-create-day-type')?.addEventListener('click', () => {
      this._creatingDayType = false;
      this._duplicatingDayTypeSourceId = null;
      this._creatingDayTypeDraft = null;
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
      this._creatingScheduledMomentDraft = {
        momentId: null,
        time: '08:00',
      };

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
      this._duplicatingWeekScheduleSourceId = null;
      this._creatingWeekScheduleDraft = null;
      this._error = null;
      this._creatingWeekSchedule = true;
      this.render();
    });

    this.shadowRoot.querySelectorAll('.duplicate-week-schedule[data-week-schedule-id]')
      .forEach((element) => {
        element.addEventListener('click', (event) => {
          event.stopPropagation();
          this._openDuplicateWeekScheduleDialog(element.dataset.weekScheduleId);
        });
      });

    this.shadowRoot.querySelector('#cancel-create-week-schedule')?.addEventListener('click', () => {
      this._creatingWeekSchedule = false;
      this._duplicatingWeekScheduleSourceId = null;
      this._error = null;
      this._creatingWeekScheduleDraft = null;
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
          this._editingWeekScheduleDraft = null;
          this._error = null;

          this.render();
        });
      });

    this.shadowRoot.querySelector('#cancel-edit-week-schedule')?.addEventListener('click', () => {
      this._editingWeekScheduleId = null;
      this._error = null;
      this._editingWeekScheduleDraft = null;
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
      this._duplicatingCycleSourceId = null;
      this._creatingCycle = true;
      this._error = null;
      this._creatingCycleDraft = null;
      this.render();
    });

    this.shadowRoot.querySelectorAll('.duplicate-cycle[data-cycle-id]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.stopPropagation();
        this._openDuplicateCycleDialog(element.dataset.cycleId);
      });
    });

    this.shadowRoot.querySelector('#cancel-create-cycle')?.addEventListener('click', () => {
      this._duplicatingCycleSourceId = null;
      this._creatingCycle = false;
      this._error = null;
      this._creatingCycleDraft = null;
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
        this._editingCycleDraft = null;
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
      this._editingCycleDraft = null;
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

    this.shadowRoot.querySelector('.add-calendar-exception')?.addEventListener('click', (event) => {
      event.stopPropagation();

      this._creatingCalendarExceptionDate = event.currentTarget.dataset.date;
      this._duplicatingCalendarExceptionSourceId = null;

      this._creatingCalendarException = true;
      this._error = null;
      this._creatingCalendarExceptionDraft = null;
      this.render();
    });

    this.shadowRoot
      .querySelector('.duplicate-calendar-exception')
      ?.addEventListener('click', (event) => {
        event.stopPropagation();
        this._openDuplicateCalendarExceptionDialog(event.currentTarget.dataset.calendarExceptionId);
      });

    this.shadowRoot
      .querySelector('.edit-calendar-exception')
      ?.addEventListener('click', (event) => {
        event.stopPropagation();
        this._editingCalendarExceptionId = event.currentTarget.dataset.calendarExceptionId;
        this._error = null;
        this._editingCalendarExceptionDraft = null;
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
        this._duplicatingCalendarExceptionSourceId = null;
        this._error = null;
        this._creatingCalendarExceptionDraft = null;
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
        this._editingCalendarExceptionDraft = null;
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
      this._duplicatingMomentActionSourceId = null;
      this._creatingMomentActionDraft = null;
      this._newMomentActionSequence = [];
      this._error = null;

      this.render();
    });

    this.shadowRoot.querySelectorAll('.duplicate-moment-action[data-action-id]')
      .forEach((element) => {
        element.addEventListener('click', async (event) => {
          event.stopPropagation();
          const moment = this._configuration?.moments?.find(
            (item) => item.id === this._editingMomentActionsId
          );
          const action = moment?.actions?.find(
            (item) => item.id === element.dataset.actionId
          );
          if (!action) {
            return;
          }

          await this._ensureActionSelectorLoaded();

          this._duplicatingMomentActionSourceId = action.id;
          this._creatingMomentActionDraft = {
            id: this._nextCopyId(
              action.id,
              new Set((moment.actions || []).map((item) => item.id))
            ),
            label: `${action.label || action.id} (copie)`,
          };
          this._newMomentActionSequence = structuredClone(action.sequence || []);
          this._creatingMomentAction = true;
          this._error = null;
          this.render();
        });
      });

    this.shadowRoot.querySelector('#cancel-create-moment-action')?.addEventListener('click', () => {
      this._creatingMomentAction = false;
      this._duplicatingMomentActionSourceId = null;
      this._creatingMomentActionDraft = null;
      this._newMomentActionSequence = [];
      this._error = null;

      this.render();
    });

    if (this._duplicatingMomentActionSourceId) {
      for (const [selector, key] of [
        ['#new-moment-action-id', 'id'],
        ['#new-moment-action-label', 'label'],
      ]) {
        this.shadowRoot.querySelector(selector)?.addEventListener('input', (event) => {
          if (this._creatingMomentActionDraft) {
            this._creatingMomentActionDraft[key] = event.target.value;
          }
        });
      }
    }

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
      this._duplicatingMomentSourceId = null;
      this._creatingMomentDraft = null;
      this._error = null;
      this.render();
    });

    this.shadowRoot.querySelectorAll('.duplicate-moment[data-moment-id]').forEach((element) => {
      element.addEventListener('click', () => {
        this._openDuplicateMomentDialog(element.dataset.momentId);
      });
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
      this._duplicatingMomentSourceId = null;
      this._creatingMomentDraft = null;
      this._error = null;
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

    // Préserver les champs de copie, notamment après une erreur WebSocket.
    if (this._duplicatingMomentSourceId) {
      for (const [selector, key] of [
        ['#new-moment-id', 'id'],
        ['#new-moment-name', 'name'],
      ]) {
        this.shadowRoot.querySelector(selector)?.addEventListener('input', (event) => {
          if (this._creatingMomentDraft) {
            this._creatingMomentDraft[key] = event.target.value;
          }
        });
      }
    }

    const newMomentIconPicker = this.shadowRoot.querySelector('#new-moment-icon');

    if (newMomentIconPicker) {
      newMomentIconPicker.hass = this._hass;
      newMomentIconPicker.value = this._creatingMomentDraft?.icon || '';

      newMomentIconPicker.addEventListener('value-changed', (event) => {
        const icon = event.detail?.value || '';
        newMomentIconPicker.value = icon;
        if (this._creatingMomentDraft) {
          this._creatingMomentDraft.icon = icon;
        }
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
    if (this._loading) {
      return;
    }
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

    this._editingWeekScheduleDraft = {
      name: name ?? '',
      monday: monday ?? '',
      tuesday: tuesday ?? '',
      wednesday: wednesday ?? '',
      thursday: thursday ?? '',
      friday: friday ?? '',
      saturday: saturday ?? '',
      sunday: sunday ?? '',
    };

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
    this.render();

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
      this._editingWeekScheduleDraft = null;

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
    if (this._loading) {
      return;
    }
    const weekScheduleId = this._deletingWeekScheduleId;

    if (!weekScheduleId) {
      return;
    }

    this._loading = true;
    this._error = null;
    this.render();

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
    if (this._loading) {
      return;
    }
    const deleting = this._deletingScheduledMoment;

    if (!deleting) {
      return;
    }

    this._loading = true;
    this._error = null;
    this.render();

    try {
      await this._api.removeScheduledMoment(deleting.dayTypeId, deleting.momentId);

      this._deletingScheduledMoment = null;

      this._configuration = await this._api.getConfiguration();

      // Forcer le prochain chargement du calendrier.
      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner remove scheduled moment error', error);

      this._error = this._dayTypeError(
        error, 'delete_scheduled_moment_error', 'Impossible de supprimer le moment.'
      );
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
                ${this._loading ? 'disabled' : ''}
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
                              class="icon-button duplicate-moment-action"
                              data-action-id="${escapeHtml(action.id)}"
                              type="button"
                              title="${escapeHtml(
                                this._i18n?.t(
                                  'moments.duplicate_action_group',
                                  "Dupliquer le groupe d'actions"
                                ) ?? "Dupliquer le groupe d'actions"
                              )}"
                              aria-label="${escapeHtml(
                                this._i18n?.t(
                                  'moments.duplicate_action_group',
                                  "Dupliquer le groupe d'actions"
                                ) ?? "Dupliquer le groupe d'actions"
                              )}"
                            >
                              <ha-icon icon="mdi:content-copy"></ha-icon>
                            </button>

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

    const isCopy = Boolean(this._duplicatingMomentActionSourceId);
    const draft = this._creatingMomentActionDraft || {};

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
          ${escapeHtml(isCopy
            ? (this._i18n?.t(
              'moments.duplicate_action_group',
              "Dupliquer le groupe d'actions"
            ) ?? "Dupliquer le groupe d'actions")
            : (this._i18n?.t(
              'moments.add_action_group',
              "Ajouter un groupe d'actions"
            ) ?? "Ajouter un groupe d'actions"))}
        </div>

        ${isCopy && this._error ? `
          <div class="modal-error" role="alert">${escapeHtml(this._error)}</div>
        ` : ''}

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
            value="${escapeHtml(draft.id || '')}"
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
            value="${escapeHtml(draft.label || '')}"
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
            ${escapeHtml(isCopy
              ? (this._i18n?.t('common.duplicate', 'Dupliquer') ?? 'Dupliquer')
              : (this._i18n?.t('common.save', 'Enregistrer') ?? 'Enregistrer'))}
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

    const isCopy = Boolean(this._duplicatingMomentSourceId);
    const draft = this._creatingMomentDraft || {};

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
            ${escapeHtml(isCopy
              ? (this._i18n?.t('moments.duplicate', 'Dupliquer le moment') ?? 'Dupliquer le moment')
              : (this._i18n?.t('moments.add', 'Ajouter un moment') ?? 'Ajouter un moment'))}
          </div>

          ${isCopy && this._error ? `
            <div class="modal-error" role="alert">${escapeHtml(this._error)}</div>
          ` : ''}

          ${isCopy ? `
            <div class="modal-message">
              Les actions seront copiées avec de nouveaux identifiants.
              Les journées existantes resteront liées au moment d’origine.
            </div>
          ` : ''}

          <label class="modal-field">
            <span>
              ${escapeHtml(this._i18n?.t('moments.id', 'Identifiant') ?? 'Identifiant')}
            </span>

            <input
              id="new-moment-id"
              type="text"
              value="${escapeHtml(draft.id || '')}"
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
              value="${escapeHtml(draft.name || '')}"
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
            ${escapeHtml(isCopy
              ? (this._i18n?.t('common.duplicate', 'Dupliquer') ?? 'Dupliquer')
              : (this._i18n?.t('common.save', 'Enregistrer') ?? 'Enregistrer'))}
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
    if (this._loading) {
      return;
    }
    const editing = this._editingScheduledMoment;

    if (!editing) {
      return;
    }

    const input = this.shadowRoot.querySelector('#scheduled-moment-time');

    const time = input?.value;
    editing.time = time ?? '';

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

      this._error = this._dayTypeError(
        error, 'update_scheduled_moment_error', 'Impossible de modifier le moment.'
      );

    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveDayTypeName() {
    if (this._loading) {
      return;
    }
    const input = this.shadowRoot.querySelector('#day-type-name');

    const name = input?.value?.trim();
    this._editingDayTypeNameDraft = name ?? '';

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
    this.render();

    try {
      await this._api.updateDayType(this._editingDayTypeId, name);

      this._configuration = await this._api.getConfiguration();

      this._loadedMonthKey = null;

      this._editingDayTypeName = false;
      this._editingDayTypeId = null;
      this._editingDayTypeNameDraft = null;
    } catch (error) {
      console.error('Day Planner day type update error', error);

      this._error = this._dayTypeError(
        error, 'update_error', 'Impossible de modifier le type de journée.'
      );

    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveCreateMomentAction() {
    if (this._loading) {
      return;
    }

    const momentId = this._editingMomentActionsId;

    const actionId = this.shadowRoot.querySelector('#new-moment-action-id')?.value?.trim();

    const label = this.shadowRoot.querySelector('#new-moment-action-label')?.value?.trim();

    const sequence = this._newMomentActionSequence || [];
    const isCopy = Boolean(this._duplicatingMomentActionSourceId);
    if (isCopy) {
      this._creatingMomentActionDraft = { id: actionId || '', label: label || '' };
    }

    if (!momentId || !actionId || !label) {
      if (isCopy) {
        this._error = this._i18n?.t('day_types.id_name_required', 'L’identifiant et le libellé sont obligatoires.');
        this.render();
      }
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
    let created = false;

    try {
      await this._api.addMomentAction(momentId, actionId, label, sequence);
      created = true;

      this._configuration = await this._api.getConfiguration();

      this._creatingMomentAction = false;
      this._duplicatingMomentActionSourceId = null;
      this._creatingMomentActionDraft = null;
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

      if (created) {
        // L'ajout a réussi mais pas le rafraîchissement : ne pas proposer
        // une deuxième création accidentelle avec le même identifiant.
        this._error = `Le groupe d'actions « ${actionId} » a été créé, ` +
          `mais l'affichage n'a pas été actualisé : ${this._error}`;
        this._creatingMomentAction = false;
        this._duplicatingMomentActionSourceId = null;
        this._creatingMomentActionDraft = null;
        this._newMomentActionSequence = [];
        this._loadedMonthKey = null;
      }
    } finally {
      this._loading = false;
      this.render();
    }
  }

  _dayTypeError(error, key, fallback) {
    const message = String(error?.message || '');
    const mappings = [
      [/Cannot remove a day type used by a week schedule/, 'used_by_week'],
      [/Cannot remove a day type used by a calendar exception/, 'used_by_exception'],
      [/Day type not found:/, 'not_found'],
      [/Duplicate (?:day type|id)|already exists/i, 'duplicate_id_error'],
      [/Duplicate moment in day type/, 'duplicate_moment_error'],
      [/Scheduled moment not found/, 'scheduled_moment_not_found'],
    ];
    const match = mappings.find(([pattern]) => pattern.test(message));
    return this._i18n?.t(`day_types.${match ? match[1] : key}`, fallback) ?? fallback;
  }

  _openCreateDayTypeDialog() {
    this._error = null;
    this._duplicatingDayTypeSourceId = null;
    this._creatingDayTypeDraft = {
      id: '',
      name: '',
    };
    this._creatingDayType = true;
    this.render();
  }

  _openDuplicateDayTypeDialog(sourceId) {
    const source = this._configuration?.day_types?.find((item) => item.id === sourceId);
    if (!source) {
      return;
    }

    this._duplicatingDayTypeSourceId = source.id;
    this._creatingDayTypeDraft = {
      id: this._nextCopyId(
        source.id,
        new Set((this._configuration?.day_types || []).map((item) => item.id))
      ),
      name: `${source.name} ${this._i18n?.t('day_types.copy_suffix', '(copie)') ?? '(copie)'}`,
    };
    this._error = null;
    this._creatingDayType = true;
    this.render();
  }

  _renderCreateDayTypeDialog() {
    if (!this._creatingDayType) {
      return '';
    }

    const duplicateSource = this._configuration?.day_types?.find(
      (item) => item.id === this._duplicatingDayTypeSourceId
    );

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
              duplicateSource ? 'day_types.duplicate' : 'day_types.add',
              duplicateSource ? 'Dupliquer un type de journée' : 'Ajouter un type de journée'
            ) ?? (duplicateSource ? 'Dupliquer un type de journée' : 'Ajouter un type de journée')
          )}
        </div>
        ${
          duplicateSource
            ? `<p>${escapeHtml(
                (this._i18n?.t(
                  duplicateSource.scheduled_moments?.length === 1
                    ? 'day_types.copy_information_one'
                    : 'day_types.copy_information_other',
                  '{count} moments planifiés seront recopiés avec leurs horaires. Les Moments et leurs Actions resteront partagés.'
                ) ?? '{count} moments planifiés seront recopiés avec leurs horaires. Les Moments et leurs Actions resteront partagés.')
                  .replace('{count}', duplicateSource.scheduled_moments?.length || 0)
              )}</p>`
            : ''
        }
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
            value="${escapeHtml(this._creatingDayTypeDraft?.id ?? '')}"
            placeholder="${escapeHtml(this._i18n?.t('day_types.id_example', 'ex : jour_maison') ?? 'ex : jour_maison')}"
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
            value="${escapeHtml(this._creatingDayTypeDraft?.name ?? '')}"
            placeholder="${escapeHtml(this._i18n?.t('day_types.name_example', 'ex : Journée Maison') ?? 'ex : Journée Maison')}"
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
            ${this._loading ? 'disabled' : ''}
          >
            ${escapeHtml(
              this._i18n?.t(
                duplicateSource ? 'common.duplicate' : 'common.create',
                duplicateSource ? 'Dupliquer' : 'Créer'
              ) ?? (duplicateSource ? 'Dupliquer' : 'Créer')
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

    const collator = new Intl.Collator(getLanguage(this._hass), {
      sensitivity: 'base',
      numeric: true,
    });
    const availableMoments = moments
      .filter((moment) => !usedMomentIds.has(moment.id))
      .sort((a, b) => collator.compare(a.name || a.id, b.name || b.id));

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-scheduled-moment-dialog-title"
      >
        <div
          id="create-scheduled-moment-dialog-title"
          class="modal-title"
        >
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
                          ${
                            moment.id === this._creatingScheduledMomentDraft?.momentId
                              ? 'selected'
                              : ''
                          }
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
                  value="${escapeHtml(this._creatingScheduledMomentDraft?.time ?? '08:00')}"
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
                  ${this._loading ? 'disabled' : ''}
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

  async _saveDuplicateDayType() {
    if (this._loading) {
      return;
    }

    const source = this._configuration?.day_types?.find(
      (item) => item.id === this._duplicatingDayTypeSourceId
    );
    if (!source) {
      this._error = this._i18n?.t('day_types.source_missing', 'Le type de journée source est introuvable.');
      this.render();
      return;
    }

    const dayTypeId = this.shadowRoot.querySelector('#new-day-type-id')?.value?.trim() || '';
    const name = this.shadowRoot.querySelector('#new-day-type-name')?.value?.trim() || '';
    this._creatingDayTypeDraft = { id: dayTypeId, name };
    if (!dayTypeId || !name) {
      this._error = 'L’identifiant et le libellé sont obligatoires.';
      this.render();
      return;
    }

    // Les moments référencés restent les mêmes : seuls le type de journée
    // et ses affectations horaires sont recréés.
    const scheduled = structuredClone(source.scheduled_moments || []);
    if (scheduled.some((item) => !item.moment_id || !item.time_definition?.fixed_time)) {
      this._error = this._i18n?.t('day_types.copy_schedule_invalid', 'Impossible de copier les moments : horaire ou identifiant absent.');
      this.render();
      return;
    }

    this._loading = true;
    this._error = null;
    this.render();
    let dayTypeCreated = false;
    let schedulesCopied = false;

    try {
      await this._api.addDayType(dayTypeId, name);
      dayTypeCreated = true;
      for (const item of scheduled) {
        await this._api.addScheduledMoment(
          dayTypeId,
          item.moment_id,
          item.time_definition.fixed_time
        );
      }
      schedulesCopied = true;
      this._configuration = await this._api.getConfiguration();
      this._selectedDayTypeId = dayTypeId;
      this._loadedMonthKey = null;
      this._calendarKey = null;
      this._creatingDayType = false;
      this._duplicatingDayTypeSourceId = null;
      this._creatingDayTypeDraft = null;
    } catch (error) {
      console.error('Day Planner duplicate day type error', error);
      let message = this._dayTypeError(error, 'copy_error', 'Impossible de dupliquer le type de journée.');
      if (dayTypeCreated && !schedulesCopied) {
        try {
          await this._api.removeDayType(dayTypeId);
        } catch (rollbackError) {
          console.error('Day Planner duplicate day type rollback error', rollbackError);
          message += ' ' + (this._i18n?.t(
            'day_types.copy_rollback_error',
            'Impossible de supprimer la copie incomplète « {id} ». Vérifiez les types de journée.'
          ) ?? 'Impossible de supprimer la copie incomplète « {id} ». Vérifiez les types de journée.')
            .replace('{id}', dayTypeId);
        }
      } else if (schedulesCopied) {
        message = (this._i18n?.t(
          'day_types.copy_refresh_error',
          'Le type de journée « {id} » a été copié, mais son affichage n’a pas été actualisé.'
        ) ?? 'Le type de journée « {id} » a été copié, mais son affichage n’a pas été actualisé.')
          .replace('{id}', dayTypeId);
        // Ne jamais proposer un deuxième enregistrement après succès de la copie.
        this._creatingDayType = false;
        this._duplicatingDayTypeSourceId = null;
        this._creatingDayTypeDraft = null;
        this._selectedDayTypeId = dayTypeId;
      }
      try {
        this._configuration = await this._api.getConfiguration();
      } catch (refreshError) {
        console.error('Day Planner duplicate day type refresh error', refreshError);
      }
      this._error = message;
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveCreateDayType() {
    if (this._loading) {
      return;
    }
    if (this._duplicatingDayTypeSourceId) {
      await this._saveDuplicateDayType();
      return;
    }
    const idInput = this.shadowRoot.querySelector('#new-day-type-id');

    const nameInput = this.shadowRoot.querySelector('#new-day-type-name');

    const dayTypeId = idInput?.value?.trim();
    const name = nameInput?.value?.trim();

    this._creatingDayTypeDraft = {
      id: dayTypeId ?? '',
      name: name ?? '',
    };

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
    this.render();

    try {
      await this._api.addDayType(dayTypeId, name);

      this._configuration = await this._api.getConfiguration();

      this._selectedDayTypeId = dayTypeId;

      this._loadedMonthKey = null;
      this._creatingDayType = false;
      this._creatingDayTypeDraft = null;
    } catch (error) {
      console.error('Day Planner add day type error', error);

      this._error = this._dayTypeError(
        error, 'add_error', "Impossible d'ajouter le type de journée."
      );

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

  _openDuplicateWeekScheduleDialog(sourceId) {
    const source = this._configuration?.week_schedules?.find((item) => item.id === sourceId);
    if (!source) {
      return;
    }

    const usedIds = new Set((this._configuration?.week_schedules || []).map((item) => item.id));
    this._duplicatingWeekScheduleSourceId = source.id;
    this._creatingWeekScheduleDraft = {
      id: this._nextCopyId(source.id, usedIds),
      name: `${source.name} (copie)`,
      monday: source.monday,
      tuesday: source.tuesday,
      wednesday: source.wednesday,
      thursday: source.thursday,
      friday: source.friday,
      saturday: source.saturday,
      sunday: source.sunday,
    };
    this._creatingWeekSchedule = true;
    this._error = null;
    this.render();
  }

  async _saveCreateWeekSchedule() {
    if (this._loading) {
      return;
    }
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

    this._creatingWeekScheduleDraft = {
      id: weekScheduleId ?? '',
      name: name ?? '',
      monday: monday ?? '',
      tuesday: tuesday ?? '',
      wednesday: wednesday ?? '',
      thursday: thursday ?? '',
      friday: friday ?? '',
      saturday: saturday ?? '',
      sunday: sunday ?? '',
    };

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
    this.render();

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
      this._duplicatingWeekScheduleSourceId = null;
      this._creatingWeekScheduleDraft = null;

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
    if (this._loading) {
      return;
    }
    const dayTypeId = this._creatingScheduledMomentDayTypeId;

    const momentId =
      this.shadowRoot.querySelector('#scheduled-moment-id')?.value;

    const time =
      this.shadowRoot.querySelector('#new-scheduled-moment-time')?.value;

    this._creatingScheduledMomentDraft = {
      momentId: momentId ?? '',
      time: time ?? '',
    };

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
      this._creatingScheduledMomentDraft = null;

      await this._loadConfiguration();

      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error(
        'Day Planner add scheduled moment error',
        error
      );

      this._error = this._dayTypeError(
        error, 'add_scheduled_moment_error', "Impossible d'ajouter le moment."
      );
    } finally {
      this._loading = false;
      this.render();
    }
  }

  _openDuplicateCycleDialog(sourceId) {
    const source = this._configuration?.cycles?.find((item) => item.id === sourceId);
    if (!source) {
      return;
    }

    const usedIds = new Set((this._configuration?.cycles || []).map((item) => item.id));
    this._duplicatingCycleSourceId = source.id;
    this._creatingCycleDraft = {
      id: this._nextCopyId(source.id, usedIds),
      name: `${source.name} (copie)`,
      // Une date identique serait rejetée et modifierait potentiellement le planning.
      // L'utilisateur choisit explicitement un autre lundi.
      start_date: '',
      weekSelections: [...(source.week_schedule_ids || [])],
    };
    this._creatingCycle = true;
    this._error = null;
    this.render();
  }

  async _saveCreateCycle() {
    if (this._loading) {
      return;
    }

    const getValue = (id) => this.shadowRoot.querySelector(`#${id}`)?.value?.trim();

    const cycleId = getValue('create-cycle-id');

    const name = getValue('create-cycle-name');

    const startDate = getValue('create-cycle-start-date');

    const weekSelections = [
      getValue('create-cycle-week-1') ?? '',
      getValue('create-cycle-week-2') ?? '',
      getValue('create-cycle-week-3') ?? '',
      getValue('create-cycle-week-4') ?? '',
    ];

    this._creatingCycleDraft = {
      id: cycleId ?? '',
      name: name ?? '',
      start_date: startDate ?? '',
      weekSelections,
    };

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

    const weekScheduleIds = weekSelections.filter(Boolean);

    if (!cycleId) {
      this._error = 
        this._i18n?.t(
          'errors.cycle_id_required',
          "L'identifiant du cycle est obligatoire."
        ) ?? "L'identifiant du cycle est obligatoire.";

      this.render();
      return;
    }

    if (!name) {
      this._error = 
        this._i18n?.t(
          'errors.cycle_name_required',
          'Le libellé du cycle est obligatoire.'
        ) ?? 'Le libellé du cycle est obligatoire.';
      this.render();
      return;
    }

    if (!startDate) {
      this._error = 
        this._i18n?.t(
          'errors.cycle_start_date_required',
          'La date de début du cycle est obligatoire.'
        ) ?? 'La date de début du cycle est obligatoire.';
      this.render();
      return;
    }

    if (weekScheduleIds.length < 1 || weekScheduleIds.length > 4) {
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
    this.render();

    try {
      await this._api.addCycle(cycleId, name, startDate, weekScheduleIds);

      this._creatingCycle = false;
      this._duplicatingCycleSourceId = null;
      this._creatingCycleDraft = null;

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
      } else if (message.startsWith('Maximum number of cycles exceeded:')) {
        const maxCycles = Number(
          message.split(':').pop().trim()
        );

        this._error = Number.isFinite(maxCycles)
          ? `${this._i18n?.t(
              'errors.max_cycles_reached',
              'Nombre maximal de cycles atteint'
            ) ?? 'Nombre maximal de cycles atteint'} : ${maxCycles}.`
          : this._i18n?.t(
              'errors.max_cycles_reached',
              'Nombre maximal de cycles atteint'
            ) ?? 'Nombre maximal de cycles atteint';
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
    if (this._loading) {
      return;
    }

    const cycleId = this._editingCycleId;

    if (!cycleId) {
      return;
    }

    const getValue = (id) => this.shadowRoot.querySelector(`#${id}`)?.value?.trim();

    const name = getValue('edit-cycle-name');

    const startDate = getValue('edit-cycle-start-date');

    const weekSelections = [
      getValue('edit-cycle-week-1') ?? '',
      getValue('edit-cycle-week-2') ?? '',
      getValue('edit-cycle-week-3') ?? '',
      getValue('edit-cycle-week-4') ?? '',
    ];

    this._editingCycleDraft = {
      name: name ?? '',
      start_date: startDate ?? '',
      weekSelections,
    };

    const weekScheduleIds = weekSelections.filter(Boolean);

    if (!name) {
      this._error = 
        this._i18n?.t(
          'errors.cycle_name_required',
          'Le libellé du cycle est obligatoire.'
        ) ?? 'Le libellé du cycle est obligatoire.';
      this.render();
      return;
    }

    if (!startDate) {
      this._error = 
        this._i18n?.t(
          'errors.cycle_start_date_required',
          'La date de début du cycle est obligatoire.'
        ) ?? 'La date de début du cycle est obligatoire.';
      this.render();
      return;
    }

    if (weekScheduleIds.length < 1 || weekScheduleIds.length > 4) {
      this._error = 
        this._i18n?.t(
          'errors.invalid_week_count',
          'Un cycle doit contenir entre 1 et 4 semaines types.'
        ) ?? 'Un cycle doit contenir entre 1 et 4 semaines types.';
      this.render();
      return;
    }

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

    this._loading = true;
    this._error = null;
    this.render();

    try {
      await this._api.updateCycle(cycleId, name, startDate, weekScheduleIds);

      this._editingCycleId = null;

      this._editingCycleDraft = null;

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

  /*
   * L3-07 : gestion commune du focus pour tous les formulaires modaux.
   * Les fenêtres existent déjà dans le shadow DOM de la carte.
   */
  _captureModalOpener() {
    const card = this.shadowRoot.querySelector('ha-card');
    const active = this.shadowRoot.activeElement;

    if (!card || !active || !card.contains(active)) {
      this._modalOpener = null;
      return;
    }

    const controls = Array.from(
      card.querySelectorAll('button, input, select, textarea, [tabindex]')
    );

    this._modalOpener = {
      id: active.id || null,
      classes: Array.from(active.classList),
      data: Array.from(active.attributes)
        .filter((attr) => attr.name.startsWith('data-'))
        .map((attr) => [attr.name, attr.value]),
      index: controls.indexOf(active),
    };
  }

  _restoreModalOpener() {
    const opener = this._modalOpener;
    this._modalOpener = null;

    const card = this.shadowRoot.querySelector('ha-card');
    if (!card) {
      return;
    }

    const controls = Array.from(
      card.querySelectorAll('button, input, select, textarea, [tabindex]')
    );

    let target = null;

    if (opener?.id) {
      target = controls.find((el) => el.id === opener.id);
    }

    if (!target && opener?.data.length) {
      target = controls.find((el) =>
        opener.data.every(([name, value]) => el.getAttribute(name) === value) &&
        opener.classes.every((name) => el.classList.contains(name))
      );
    }

    if (!target && opener?.index >= 0) {
      target = controls[opener.index];
    }

    // L'élément d'origine a pu être supprimé après l'enregistrement.
    (target || card.querySelector('.tab.active'))?.focus({ preventScroll: true });
  }

  _setupModalAccessibility(hadModal) {
    const dialog = this.shadowRoot.querySelector('.modal-backdrop .modal-dialog');

    if (!dialog) {
      if (hadModal) {
        this._restoreModalOpener();
      }
      return;
    }

    // Ne pas appliquer `inert` sur ha-card : les fenêtres sont des éléments
    // distincts de la carte et l'inertie peut bloquer les interactions HA.
    // La couche .modal-backdrop protège déjà le contenu en arrière-plan.
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('tabindex', '-1');

    const title = dialog.querySelector('.modal-title');
    if (title) {
      if (!title.id) {
        title.id = 'day-planner-active-dialog-title';
      }
      dialog.setAttribute('aria-labelledby', title.id);
    }

    const selector = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      'ha-selector',
      'ha-icon-picker',
      '[tabindex]:not([tabindex="-1"])',
    ].join(', ');

    const focusables = () => Array.from(dialog.querySelectorAll(selector))
      .filter((element) =>
        element.getClientRects().length > 0 &&
        element.getAttribute('aria-hidden') !== 'true' &&
        !element.closest('[hidden]')
      );

    // Le gestionnaire appartient uniquement à la modale active.
    // Aucun élément sentinelle ni écouteur global n'est nécessaire.
    dialog.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        if (this._loading) {
          return;
        }
        const cancel = dialog.querySelector(
          'button[id^="cancel-"], button#close-moment-actions'
        );
        if (cancel && !cancel.disabled) {
          event.preventDefault();
          event.stopPropagation();
          cancel.click();
        }
        return;
      }

      if (event.key !== 'Tab') {
        return;
      }

      const elements = focusables();
      if (!elements.length) {
        event.preventDefault();
        dialog.focus({ preventScroll: true });
        return;
      }

      const current = this.shadowRoot.activeElement;
      const currentIndex = elements.findIndex((element) =>
        element === current || element.contains(current)
      );

      if (currentIndex === -1) {
        event.preventDefault();
        (event.shiftKey ? elements.at(-1) : elements[0])
          .focus({ preventScroll: true });
        return;
      }

      if (event.shiftKey && currentIndex === 0) {
        event.preventDefault();
        elements.at(-1).focus({ preventScroll: true });
      } else if (!event.shiftKey && currentIndex === elements.length - 1) {
        event.preventDefault();
        elements[0].focus({ preventScroll: true });
      }
    });

    // Mettre le focus dans le premier champ du formulaire (et non sur les
    // boutons du fond). Les éléments HA peuvent finir leur rendu après
    // l'insertion de la modale dans le shadow DOM.
    const focusFirstField = () => {
      // Un rendu plus récent a pu fermer/remplacer cette fenêtre.
      if (
        !dialog.isConnected ||
        this.shadowRoot.querySelector('.modal-backdrop .modal-dialog') !== dialog
      ) {
        return;
      }

      // Ne jamais déplacer le focus si l'utilisateur est déjà dans la modale.
      const active = this.shadowRoot.activeElement;
      if (active && active !== dialog && dialog.contains(active)) {
        return;
      }

      const fieldSelector = [
        'input:not([type="hidden"]):not([disabled]):not([readonly])',
        'select:not([disabled])',
        'textarea:not([disabled]):not([readonly])',
        'ha-selector:not([disabled])',
        'ha-icon-picker:not([disabled])',
      ].join(', ');

      const firstField = Array.from(dialog.querySelectorAll(fieldSelector))
        .find((field) =>
          field.getClientRects().length > 0 &&
          field.getAttribute('aria-hidden') !== 'true' &&
          !field.closest('[hidden]')
        );

      if (firstField) {
        firstField.focus({ preventScroll: true });
        // Certains contrôles HA délèguent le focus à leur Shadow DOM.
        if (this.shadowRoot.activeElement !== firstField && firstField.shadowRoot) {
          firstField.shadowRoot.querySelector(
            'input:not([disabled]), select:not([disabled]), ' +
            'textarea:not([disabled]), button:not([disabled]), ' +
            '[tabindex]:not([tabindex="-1"])'
          )?.focus({ preventScroll: true });
        }
      } else {
        // Fenêtre de confirmation : aucun champ, premier bouton disponible.
        (focusables()[0] || dialog).focus({ preventScroll: true });
      }
    };

    focusFirstField();
    // Après le clic d'ouverture et le rendu des composants personnalisés.
    requestAnimationFrame(() => requestAnimationFrame(focusFirstField));
  }

  render() {
    if (!this._hass) {
      return;
    }

    const hadModal = Boolean(
      this.shadowRoot.querySelector('.modal-backdrop .modal-dialog')
    );

    if (!hadModal) {
      this._captureModalOpener();
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
    this._setupModalAccessibility(hadModal);
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
    this._editingDayTypeNameDraft = null;
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
    const dependencies = getDayTypeDependencies(this._configuration, dayType.id);
    const blocked = dependencies.weeks.length > 0 || dependencies.exceptions.length > 0;
    const dayNames = (days) => days
      .map((day) => this._i18n?.t(`day_types.weekdays.${day}`, day) ?? day).join(', ');
    const today = formatDate(new Date());
    const weekList = dependencies.weeks.map((week) => `<li><strong>${escapeHtml(week.name)}</strong> : ${escapeHtml(dayNames(week.days))}</li>`).join('');
    const exceptionList = dependencies.exceptions.map((exception) => {
      const status = exception.date < today ? 'past' : exception.date === today ? 'today' : 'future';
      const label = this._i18n?.t(`day_types.exception_${status}`, status) ?? status;
      return `<li>${escapeHtml(formatLongDate(exception.date, this._hass))} — ${escapeHtml(label)}${exception.description ? ` : ${escapeHtml(exception.description)}` : ''}</li>`;
    }).join('');

    return `
    <div class="modal-backdrop">
      <div
        class="modal-dialog day-type-delete-dialog"
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

        ${blocked ? `
          <div class="modal-error" role="alert">
            ${escapeHtml(this._i18n?.t(
              'day_types.delete_blocked',
              'Suppression impossible : ce type de journée est encore utilisé.'
            ) ?? 'Suppression impossible : ce type de journée est encore utilisé.')}
          </div>
          ${weekList ? `<div class="day-type-dependency-list"><strong>${escapeHtml(this._i18n?.t('day_types.weeks_details', 'Semaines types'))}</strong><ul>${weekList}</ul></div>` : ''}
          ${exceptionList ? `<div class="day-type-dependency-list"><strong>${escapeHtml(this._i18n?.t('day_types.exceptions_details', 'Exceptions de calendrier'))}</strong><ul>${exceptionList}</ul></div>` : ''}
          <p>${escapeHtml(this._i18n?.t(
            'day_types.delete_blocked_hint',
            'Modifiez ou supprimez les références ci-dessus avant de supprimer ce type de journée.'
          ) ?? 'Modifiez ou supprimez les références ci-dessus avant de supprimer ce type de journée.')}</p>
        ` : ''}

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
            ${this._loading || blocked ? 'disabled' : ''}
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
    if (this._loading) {
      return;
    }
    const dayTypeId = this._deletingDayTypeId;

    if (!dayTypeId) {
      return;
    }
    const dependencies = getDayTypeDependencies(this._configuration, dayTypeId);
    if (dependencies.weeks.length || dependencies.exceptions.length) {
      this._error = this._i18n?.t(
        'day_types.delete_blocked',
        'Suppression impossible : ce type de journée est encore utilisé.'
      );
      this.render();
      return;
    }

    this._loading = true;
    this._error = null;
    this.render();

    try {
      await this._api.removeDayType(dayTypeId);

      this._configuration = await this._api.getConfiguration();

      this._deletingDayTypeId = null;

      const remaining = this._configuration.day_types || [];

      this._selectedDayTypeId = remaining[0]?.id ?? null;

      this._loadedMonthKey = null;
    } catch (error) {
      console.error('Day Planner remove day type error', error);

      this._error = this._dayTypeError(
        error, 'delete_error', 'Impossible de supprimer le type de journée.'
      );

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
            value="${escapeHtml(this._editingDayTypeNameDraft ?? dayType.name)}"
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
            ${this._loading ? 'disabled' : ''}
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
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-scheduled-moment-dialog-title"
      >
        <div
          id="delete-scheduled-moment-dialog-title"
          class="modal-title"
        >
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
            ${this._loading ? 'disabled' : ''}
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
    const draft = this._creatingWeekScheduleDraft;
    const isDuplication = Boolean(this._duplicatingWeekScheduleSourceId);

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
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-week-schedule-dialog-title"
      >
        <div
          id="create-week-schedule-dialog-title"
          class="modal-title"
        >
          ${isDuplication ? 'Dupliquer une semaine type' : 'Créer une semaine type'}
        </div>
        ${
          this._error
            ? `
              <div class="error" role="alert">
                ${escapeHtml(this._error)}
              </div>
            `
            : ''
        }

        <label class="modal-field">
          <span>Identifiant</span>

          <input
            id="create-week-schedule-id"
            type="text"
            autocomplete="off"
            value="${escapeHtml(draft?.id ?? '')}"
          />
        </label>

        <label class="modal-field">
          <span>Libellé</span>

          <input
            id="create-week-schedule-name"
            type="text"
            autocomplete="off"
            value="${escapeHtml(draft?.name ?? '')}"
          />
        </label>

        ${renderDaySelect('create-week-schedule-monday', 'Lundi', draft?.monday)}

        ${renderDaySelect('create-week-schedule-tuesday', 'Mardi', draft?.tuesday)}

        ${renderDaySelect('create-week-schedule-wednesday', 'Mercredi', draft?.wednesday)}

        ${renderDaySelect('create-week-schedule-thursday', 'Jeudi', draft?.thursday)}

        ${renderDaySelect('create-week-schedule-friday', 'Vendredi', draft?.friday)}

        ${renderDaySelect('create-week-schedule-saturday', 'Samedi', draft?.saturday)}

        ${renderDaySelect('create-week-schedule-sunday', 'Dimanche', draft?.sunday)}

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
            ${this._loading ? 'disabled' : ''}
          >
            ${isDuplication ? 'Dupliquer' : 'Créer'}
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

    const draft = this._editingWeekScheduleDraft ?? weekSchedule;

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
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-week-schedule-dialog-title"
      >
        <div
          id="edit-week-schedule-dialog-title"
          class="modal-title"
        >
          Modifier la semaine type
        </div>
        
        ${
          this._error
            ? `
              <div class="error" role="alert">
                ${escapeHtml(this._error)}
              </div>
            `
            : ''
        }

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
            value="${escapeHtml(draft.name)}"
          />
        </label>

        ${renderDaySelect('edit-week-schedule-monday', 'Lundi', draft.monday)}

        ${renderDaySelect('edit-week-schedule-tuesday', 'Mardi', draft.tuesday)}

        ${renderDaySelect('edit-week-schedule-wednesday', 'Mercredi', draft.wednesday)}

        ${renderDaySelect('edit-week-schedule-thursday', 'Jeudi', draft.thursday)}

        ${renderDaySelect('edit-week-schedule-friday', 'Vendredi', draft.friday)}

        ${renderDaySelect('edit-week-schedule-saturday', 'Samedi', draft.saturday)}

        ${renderDaySelect('edit-week-schedule-sunday', 'Dimanche', draft.sunday)}

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
            ${this._loading ? 'disabled' : ''}
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

    const draft = this._editingCycleDraft ?? cycle;

    const weekIds =
      this._editingCycleDraft?.weekSelections ?? cycle.week_schedule_ids ?? [];
    const weekSchedules = this._configuration?.week_schedules ?? [];

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
            value="${escapeHtml(draft.name)}"
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.start_date', 'Date de début'))}
          </span>

          <input
            id="edit-cycle-start-date"
            type="date"
            value="${escapeHtml(draft.start_date)}"
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
            ${this._loading ? 'disabled' : ''}
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
            ${this._loading ? 'disabled' : ''}
          >
            ${escapeHtml(t('common.delete', 'Supprimer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  async _deleteCycle() {
    if (this._loading) {
      return;
    }

    const cycleId = this._deletingCycleId;

    if (!cycleId) {
      return;
    }

    this._loading = true;
    this._error = null;
    this.render();

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
      <div
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-week-schedule-dialog-title"
      >
        <div
          id="delete-week-schedule-dialog-title"
          class="modal-title"
        >
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
            ${this._loading ? 'disabled' : ''}
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

    const isDuplication = Boolean(this._duplicatingCycleSourceId);
    const draft = this._creatingCycleDraft;
    const weekIds = draft?.weekSelections ?? [];

    const weekSchedules = this._configuration?.week_schedules || [];

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
        <span>${escapeHtml(label)}</span>

        <select
          id="${id}"
          ${required ? 'required' : ''}
        >
          ${
            required
              ? ''
              : `
                <option value="" ${!selectedId ? 'selected' : ''}>
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
          ${escapeHtml(isDuplication
            ? t('cycles.duplicate_title', 'Dupliquer un cycle')
            : t('cycles.create_title', 'Créer un cycle'))}
        </div>
        ${isDuplication ? `
          <p class="modal-message">
            Les semaines types sont conservées. Choisissez une nouvelle date
            de début, un lundi distinct des cycles existants.
          </p>
        ` : ''}
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
            value="${escapeHtml(draft?.id ?? '')}"
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
            value="${escapeHtml(draft?.name ?? '')}"
          />
        </label>

        <label class="modal-field">
          <span>
            ${escapeHtml(t('cycles.start_date', 'Date de début'))}
          </span>

          <input
            id="create-cycle-start-date"
            type="date"
            value="${escapeHtml(draft?.start_date ?? '')}"
          />
        </label>

        ${renderWeekSelect(
          'create-cycle-week-1',
          `${t('cycles.week', 'Semaine')} 1`,
          weekIds[0],
          true
        )}

        ${renderWeekSelect(
          'create-cycle-week-2',
          `${t('cycles.week', 'Semaine')} 2`,
          weekIds[1]
        )}

        ${renderWeekSelect(
          'create-cycle-week-3',
          `${t('cycles.week', 'Semaine')} 3`,
          weekIds[2]
        )}

        ${renderWeekSelect(
          'create-cycle-week-4',
          `${t('cycles.week', 'Semaine')} 4`,
          weekIds[3]
        )}

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
            ${this._loading ? 'disabled' : ''}
          >
            ${escapeHtml(isDuplication
              ? t('common.duplicate', 'Dupliquer')
              : t('common.create', 'Créer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  _openDuplicateCalendarExceptionDialog(sourceId) {
    const source = this._configuration?.calendar_exceptions?.find((item) => item.id === sourceId);
    if (!source) {
      return;
    }

    this._duplicatingCalendarExceptionSourceId = source.id;
    this._creatingCalendarExceptionDate = null;
    this._creatingCalendarExceptionDraft = {
      date: '', // Une exception ne peut pas partager la date de l'originale.
      day_type_id: source.day_type_id,
      description: source.description ?? '',
    };
    this._creatingCalendarException = true;
    this._error = null;
    this.render();
  }

  _renderCreateCalendarExceptionDialog() {
    if (!this._creatingCalendarException) {
      return '';
    }

    const isDuplication = Boolean(this._duplicatingCalendarExceptionSourceId);
    if (!isDuplication && !this._creatingCalendarExceptionDate) {
      return '';
    }

    const source = isDuplication
      ? this._configuration?.calendar_exceptions?.find(
          (item) => item.id === this._duplicatingCalendarExceptionSourceId
        )
      : null;
    const dayTypes = this._configuration?.day_types || [];
    const draft = this._creatingCalendarExceptionDraft;

    const dateLabel = formatLongDate(
      source?.date || this._creatingCalendarExceptionDate,
      this._hass
    );

    const t = (key, fallback) => this._i18n?.t(key, fallback) ?? fallback;

    return /* html */ `
    <div class="modal-backdrop">
      <div class="modal-dialog">

        <div class="modal-title">
          ${escapeHtml(isDuplication
            ? t('calendar_exceptions.duplicate_title', 'Dupliquer une exception')
            : t('calendar_exceptions.create_title', 'Créer une exception'))}
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
  ${isDuplication ? `<span>(${escapeHtml(t('calendar_exceptions.source_date', 'Date d’origine'))})</span>` : ''}
</div>

        ${isDuplication ? `
          <div class="editor-field">
            <label for="duplicate-calendar-exception-date">
              ${escapeHtml(t('calendar_exceptions.new_date', 'Nouvelle date'))}
            </label>
            <input
              id="duplicate-calendar-exception-date"
              type="date"
              required
              value="${escapeHtml(draft?.date ?? '')}"
            />
          </div>
        ` : ''}

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
                    ${dayType.id === draft?.day_type_id ? 'selected' : ''}
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
            value="${escapeHtml(draft?.description ?? '')}"
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
            ${this._loading ? 'disabled' : ''}
          >
            ${escapeHtml(isDuplication
              ? t('common.duplicate', 'Dupliquer')
              : t('common.create', 'Créer'))}
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

    const draft = this._editingCalendarExceptionDraft ?? calendarException;

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
                    ${dayType.id === draft.day_type_id ? 'selected' : ''}
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
            value="${escapeHtml(draft.description ?? '')}"
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
            ${this._loading ? 'disabled' : ''}
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
    if (this._loading) {
      return;
    }

    const isDuplication = Boolean(this._duplicatingCalendarExceptionSourceId);
    const date = isDuplication
      ? this.shadowRoot.querySelector('#duplicate-calendar-exception-date')?.value?.trim() ?? ''
      : this._creatingCalendarExceptionDate;

    const dayTypeId = this.shadowRoot
      .querySelector('#create-calendar-exception-day-type')
      ?.value?.trim();

    const description =
      this.shadowRoot
        .querySelector('#create-calendar-exception-description')
        ?.value?.trim() ?? '';

    this._creatingCalendarExceptionDraft = {
      date: date ?? '',
      day_type_id: dayTypeId ?? '',
      description: description ?? '',
    };

    if (isDuplication) {
      // La nouvelle date est une clé métier unique ; l'ID suit la création habituelle.
      const parsed = /^\d{4}-\d{2}-\d{2}$/.test(date)
        ? new Date(`${date}T12:00:00`)
        : null;
      if (!parsed || Number.isNaN(parsed.getTime()) || formatDate(parsed) !== date) {
        this._error = this._i18n?.t('errors.invalid_date', 'Veuillez choisir une date valide.')
          ?? 'Veuillez choisir une date valide.';
        this.render();
        return;
      }
      if ((this._configuration?.calendar_exceptions || []).some((item) => item.date === date)) {
        this._error = this._i18n?.t(
          'errors.duplicate_calendar_exception_date',
          'Une exception existe déjà pour cette date.'
        ) ?? 'Une exception existe déjà pour cette date.';
        this.render();
        return;
      }
    } else if (!date) {
      return;
    }

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
    this.render();

    try {
      await this._api.addCalendarException(calendarExceptionId, date, dayTypeId, description);

      this._creatingCalendarException = false;
      this._creatingCalendarExceptionDate = null;
      this._duplicatingCalendarExceptionSourceId = null;
      this._creatingCalendarExceptionDraft = null;

      if (isDuplication) {
        // Montrer la nouvelle exception, même si sa date est dans un autre mois.
        const [year, month] = date.split('-').map(Number);
        this._displayYear = year;
        this._displayMonth = month - 1;
        this._selectedDate = date;
      }
      await this._refreshCalendarConfiguration();

      return;
    } catch (error) {
      console.error('Day Planner create calendar exception error', error);

      this._error = error?.message || this._getGenericErrorMessage();
    } finally {
      this._loading = false;
      this.render();
    }
  }

  // Le moment copié n'est pas affecté automatiquement à un type de journée.
  // Ses actions sont indépendantes des actions du moment source.
  _nextCopyId(sourceId, usedIds) {
    const base = `${sourceId}_copy`;
    let candidate = base;
    let suffix = 2;
    while (usedIds.has(candidate)) {
      candidate = `${base}_${suffix++}`;
    }
    usedIds.add(candidate);
    return candidate;
  }

  _openDuplicateMomentDialog(sourceId) {
    const source = this._configuration?.moments?.find((item) => item.id === sourceId);
    if (!source) {
      return;
    }

    const usedIds = new Set((this._configuration?.moments || []).map((item) => item.id));
    this._duplicatingMomentSourceId = source.id;
    this._creatingMomentDraft = {
      id: this._nextCopyId(source.id, usedIds),
      name: `${source.name} (copie)`,
      icon: source.icon || '',
    };
    this._creatingMoment = true;
    this._error = null;
    this.render();
  }

  async _saveDuplicateMoment() {
    if (this._loading) {
      return;
    }

    const source = this._configuration?.moments?.find(
      (item) => item.id === this._duplicatingMomentSourceId
    );
    if (!source) {
      this._error = 'Le moment source est introuvable.';
      this.render();
      return;
    }

    const momentId = this.shadowRoot.querySelector('#new-moment-id')?.value?.trim() || '';
    const name = this.shadowRoot.querySelector('#new-moment-name')?.value?.trim() || '';
    const icon = this.shadowRoot.querySelector('#new-moment-icon')?.value?.trim?.() || null;

    this._creatingMomentDraft = { id: momentId, name, icon: icon || '' };
    if (!momentId || !name) {
      this._error = 'L’identifiant et le libellé sont obligatoires.';
      this.render();
      return;
    }

    // Clonage profond : la séquence copiée ne partage aucune donnée mutable
    // avec celle d'origine. Les identifiants d'actions sont tous renouvelés.
    const actions = structuredClone(source.actions || []);
    const usedActionIds = new Set(actions.map((action) => action.id));
    this._loading = true;
    this._error = null;
    let momentCreated = false;
    let actionsCopied = false;

    try {
      await this._api.addMoment(momentId, name, icon);
      momentCreated = true;

      for (const action of actions) {
        const copiedActionId = this._nextCopyId(action.id, usedActionIds);
        await this._api.addMomentAction(
          momentId,
          copiedActionId,
          action.label || action.id,
          action.sequence
        );
      }
      actionsCopied = true;
      this._configuration = await this._api.getConfiguration();
      this._creatingMoment = false;
      this._duplicatingMomentSourceId = null;
      this._creatingMomentDraft = null;
      this._loadedMonthKey = null;
      this._calendarKey = null;
    } catch (error) {
      console.error('Day Planner duplicate moment error', error);
      let message = error?.message || 'Impossible de dupliquer le moment.';

      if (momentCreated && !actionsCopied) {
        // Une création WebSocket peut avoir réussi avant l'échec d'une action.
        // Revenir à l'état initial au lieu de laisser une copie incomplète.
        try {
          await this._api.removeMoment(momentId);
        } catch (rollbackError) {
          console.error('Day Planner duplicate moment rollback error', rollbackError);
          message += ` Suppression de la copie incomplète « ${momentId} » impossible : ` +
            (rollbackError?.message || 'vérifiez manuellement les moments.');
        }
      } else if (actionsCopied) {
        // La copie existe : une erreur de rafraîchissement ne doit pas la supprimer.
        message = `Le moment « ${momentId} » a été copié, mais son affichage n’a pas été actualisé : ${message}`;
        this._creatingMoment = false;
        this._duplicatingMomentSourceId = null;
        this._creatingMomentDraft = null;
      }

      // Recoller à l'état du serveur après un éventuel rollback.
      try {
        this._configuration = await this._api.getConfiguration();
      } catch (refreshError) {
        console.error('Day Planner duplicate moment refresh error', refreshError);
      }
      this._error = message;
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async _saveCreateMoment() {
    if (this._duplicatingMomentSourceId) {
      await this._saveDuplicateMoment();
      return;
    }

    if (this._loading) {
      return;
    }

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
    if (this._loading) {
      return;
    }

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
      this.shadowRoot
        .querySelector('#edit-calendar-exception-description')
        ?.value?.trim() ?? '';

    this._editingCalendarExceptionDraft = {
      day_type_id: dayTypeId ?? '',
      description: description ?? '',
    };

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
    this.render();

    try {
      await this._api.updateCalendarException(
        calendarExceptionId,
        calendarException.date,
        dayTypeId,
        description
      );

      this._editingCalendarExceptionId = null;
      this._editingCalendarExceptionDraft = null;

      await this._refreshCalendarConfiguration();

      return;
    } catch (error) {
      console.error('Day Planner update calendar exception error', error);

      this._error = error?.message || this._getGenericErrorMessage();
    } finally {
      this._loading = false;
      this.render();
    }
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
            ${this._loading ? 'disabled' : ''}
          >
            ${escapeHtml(t('common.delete', 'Supprimer'))}
          </button>
        </div>

      </div>
    </div>
  `;
  }

  async _deleteCalendarException() {
    if (this._loading) {
      return;
    }

    const calendarExceptionId = this._deletingCalendarExceptionId;

    if (!calendarExceptionId) {
      return;
    }

    this._loading = true;
    this._error = null;
    this.render();

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
      this.render();
    }
  }
 
}

if (!customElements.get('day-planner-card')) {
  customElements.define('day-planner-card', DayPlannerCard);
}

console.info(
  '%c DAY-PLANNER-CARD %c v0.2.9',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);

window.customCards = window.customCards || [];

if (!window.customCards.some((card) => card.type === 'day-planner-card')) {
  window.customCards.push({
  type: 'day-planner-card',
  name: 'Day Planner',
  description: 'Graphical Day Planner configuration card',
});
}
