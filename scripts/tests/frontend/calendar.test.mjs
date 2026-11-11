import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const frontend = new URL('../../../custom_components/day_planner/frontend/', import.meta.url);
const translations = {};
for (const lang of ['fr', 'en']) {
  translations[lang] = JSON.parse(await readFile(new URL(`translations/${lang}.json`, frontend), 'utf8'));
}
const registry = new Map();
globalThis.HTMLElement = class { attachShadow() { this.shadowRoot = {}; } };
globalThis.customElements = { get: (name) => registry.get(name), define: (name, value) => registry.set(name, value) };
globalThis.window = { matchMedia: () => ({ matches: false }) };
await import(new URL('day-planner-card.js', frontend));
const { DayPlannerApi } = await import(new URL('api.js', frontend));
const { renderCalendarView } = await import(new URL('views/calendar-view.js', frontend));
const { getPlannerLocation } = await import(new URL('utils.js', frontend));

function cardFixture(language = 'fr') {
  const card = new (registry.get('day-planner-card'))();
  card.render = () => {};
  card._hass = { language, config: { country: 'FR', latitude: 48, longitude: 7 }, states: {
    'binary_sensor.renamed_location': { state: 'on', attributes: {
      integration: 'Day Planner', from_cache: true, country_code: 'FR', country_name: 'France',
      subdivision_name: 'Bas-Rhin', subdivision_code: 'FR-67',
    } },
  } };
  card._displayYear = 2027;
  card._displayMonth = 2;
  card._selectedDate = '2027-03-26';
  card._calendar = { days: [{ date: card._selectedDate, day_type: { id: 'special', name: 'Congé' },
    base_day_type: { name: 'Travail' }, calendar_exception_id: 'exception', scheduled_moments: [] }] };
  card._configuration = { day_types: [{ id: 'rest', name: 'Repos' }], calendar_exceptions: [{ id: 'exception', description: 'Exception existante' }] };
  card._i18n = { load: async () => {}, t: (key, fallback = key) =>
    key.split('.').reduce((value, part) => value?.[part], translations[language]) ?? fallback };
  card._api = { getPublicHolidays: async (year) => holidayYear(year) };
  return card;
}
function holidayYear(year = 2027) {
  return { year, country_code: 'FR', subdivision: '6AE', scope: 'subdivision', status: 'ready', days: [
    { date: `${year}-03-26`, names: ['Vendredi saint'], scope: 'regional', warnings: ['local_applicability_unverified'] },
  ] };
}
function deferred() {
  let resolve;
  const promise = new Promise((done) => { resolve = done; });
  return { promise, resolve };
}

test('uses the existing response-only HA service', async () => {
  let request;
  const api = new DayPlannerApi({ callWS: async (msg) => { request = msg; return { response: holidayYear() }; } });
  assert.deepEqual(await api.getPublicHolidays(2027), holidayYear());
  assert.deepEqual(request, { type: 'call_service', domain: 'day_planner', service: 'get_public_holidays',
    service_data: { year: 2027 }, return_response: true });
});

test('keeps programmed days, exceptions, holiday details and local warnings together', async () => {
  const card = cardFixture();
  const plannerBefore = JSON.stringify([card._calendar, card._configuration]);
  await card._loadPublicHolidays();
  const html = renderCalendarView(card);
  for (const value of ['Vendredi saint', 'Congé', 'Exception existante', 'Bas-Rhin', 'France',
    'Portée locale', 'L’application locale de ce jour férié est à vérifier.', 'public-holiday-marker',
    'public-holiday-details', 'mdi:calendar-alert', 'aria-label=', 'aria-pressed="true"']) assert.ok(html.includes(value), value);
  assert.equal(JSON.stringify([card._calendar, card._configuration]), plannerBefore);
});

test('uses the frontend language for scope and warning labels', async () => {
  const card = cardFixture('en');
  await card._loadPublicHolidays();
  const html = renderCalendarView(card);
  assert.ok(html.includes('Public holidays'));
  assert.ok(html.includes('Local scope'));
  assert.ok(html.includes(translations.en.public_holidays.reasons.local_applicability_unverified));
  assert.ok(!html.includes('Portée locale'));
});

test('escapes holiday names and location labels in markup and attributes', async () => {
  const card = cardFixture();
  card._api.getPublicHolidays = async () => {
    const data = holidayYear(); data.days[0].names = ['<img src=x onerror="alert(1)">']; return data;
  };
  card._hass.states['binary_sensor.renamed_location'].attributes.country_name = '<script>bad</script>';
  await card._loadPublicHolidays();
  const html = renderCalendarView(card);
  assert.ok(!html.includes('<img'));
  assert.ok(!html.includes('<script>bad'));
  assert.ok(html.includes('&lt;img'));
});

test('displays partial and unsupported results without hiding the planner', async () => {
  for (const [status, reason] of [['partial', 'subdivision_missing'], ['unsupported', 'country_not_supported'],
    ['unavailable', 'location_unresolved']]) {
    const card = cardFixture();
    card._api.getPublicHolidays = async () => ({ ...holidayYear(), status, reason, subdivision: null, scope: 'national', days: [] });
    await card._loadPublicHolidays();
    const html = renderCalendarView(card);
    assert.ok(html.includes(translations.fr.public_holidays.reasons[reason]));
    assert.ok(html.includes('Congé'));
    assert.ok(!html.includes('class="public-holiday-marker"'));
  }
});

test('loads again for a new year and ignores the older response', async () => {
  const card = cardFixture(); const calls = [];
  card._api.getPublicHolidays = (year) => { const request = deferred(); calls.push({ year, ...request }); return request.promise; };
  const first = card._loadPublicHolidays(); await Promise.resolve();
  card._displayYear = 2028;
  const second = card._loadPublicHolidays(); await Promise.resolve();
  calls[1].resolve(holidayYear(2028)); await second;
  calls[0].resolve(holidayYear(2027)); await first;
  assert.equal(card._currentPublicHolidays().year, 2028);
  assert.equal(card._publicHolidaysLoading, false);
});

test('invalidates days immediately after moving home and refreshes the new location', async () => {
  const card = cardFixture(); await card._loadPublicHolidays();
  card._hass.config.country = 'DE';
  assert.equal(card._currentPublicHolidays(), null);
  card._api.getPublicHolidays = async (year) => ({ year, country_code: 'DE', subdivision: 'BY',
    status: 'ready', scope: 'subdivision', days: [] });
  await card._loadPublicHolidays();
  assert.equal(card._currentPublicHolidays().country_code, 'DE');
  assert.ok(!renderCalendarView(card).includes('Bas-Rhin'));
});

test('reuses annual data on ordinary HA updates and reloads when resolution changes', async () => {
  const card = cardFixture(); let calls = 0;
  card._api.getPublicHolidays = async (year) => { calls += 1; return holidayYear(year); };
  await card._loadPublicHolidays(); await card._loadPublicHolidays();
  assert.equal(calls, 1);
  card._hass.states['binary_sensor.renamed_location'].attributes.resolved_at = '2026-11-11T12:00:00+00:00';
  await card._loadPublicHolidays(); assert.equal(calls, 2);
  assert.equal(getPlannerLocation(card._hass).attributes.subdivision_code, 'FR-67');
});

test('recovers a failed call with an explicit retry', async () => {
  const card = cardFixture();
  card._api.getPublicHolidays = async () => { throw new Error('offline'); };
  await card._loadPublicHolidays();
  assert.equal(card._publicHolidaysError, true);
  const html = renderCalendarView(card);
  assert.ok(html.includes('retry-public-holidays'));
  assert.ok(html.includes('Congé'));
  card._api.getPublicHolidays = async () => holidayYear();
  await card._loadPublicHolidays(true);
  assert.equal(card._publicHolidaysError, false);
  assert.equal(card._currentPublicHolidays().status, 'ready');
});

test('rejects invalid responses without applying dates from another year', async () => {
  const card = cardFixture();
  card._api.getPublicHolidays = async () => holidayYear(2028);
  await card._loadPublicHolidays();
  assert.equal(card._currentPublicHolidays(), null);
  assert.equal(card._publicHolidaysError, true);
});

test('provides matching FR and EN keys and every backend reason', async () => {
  function keys(value, prefix = '') {
    return Object.entries(value).flatMap(([key, item]) => typeof item === 'object' ? keys(item, prefix + key + '.') : [prefix + key]).sort();
  }
  assert.deepEqual(keys(translations.fr.public_holidays), keys(translations.en.public_holidays));
  const backend = JSON.parse(await readFile(new URL('../translations/en.json', frontend), 'utf8'));
  for (const key of Object.keys(backend.exceptions).filter((key) => key.startsWith('public_holidays_'))) {
    assert.ok(translations.en.public_holidays.reasons[key.slice('public_holidays_'.length)]);
  }
});

test('preserves coincident holiday names and mixed scope', async () => {
  const card = cardFixture();
  card._api.getPublicHolidays = async () => {
    const data = holidayYear(); data.days[0].names = ['Fête A', 'Fête B']; data.days[0].scope = 'mixed'; return data;
  };
  await card._loadPublicHolidays();
  const html = renderCalendarView(card);
  assert.ok(html.includes('Fête A / Fête B'));
  assert.ok(html.includes('Portée nationale et locale'));
});

test('loads the planner through the normal entry point when holidays fail', async () => {
  const card = cardFixture();
  const calendar = card._calendar;
  card._calendar = null;
  card._api.getCalendar = async () => calendar;
  card._api.getPublicHolidays = async () => { throw Error('offline'); };
  await card._loadCalendar();
  await Promise.resolve();
  assert.equal(card._calendar, calendar);
  assert.equal(card._error, null);
  assert.equal(card._loading, false);
  assert.equal(card._publicHolidaysError, true);
});

test('ignores a translation fetch completed after the user changes language', async () => {
  const { DayPlannerI18n } = await import(new URL('i18n.js', frontend));
  const requests = new Map();
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (url) => {
    const request = deferred(); requests.set(url, request); return request.promise;
  };
  try {
    const i18n = new DayPlannerI18n({ language: 'fr' });
    const first = i18n.load();
    i18n.setHass({ language: 'en' });
    const second = i18n.load();
    requests.get('/day_planner/frontend/translations/en.json').resolve({ ok: true, json: async () => translations.en });
    await second;
    requests.get('/day_planner/frontend/translations/fr.json').resolve({ ok: true, json: async () => translations.fr });
    await first;
    assert.equal(i18n.t('public_holidays.title'), 'Public holidays');
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('keeps the displayed month consistent when calendar responses arrive out of order', async () => {
  const card = cardFixture(); const requests = [];
  card._api.getCalendar = (start) => { const request = deferred(); requests.push({start,...request}); return request.promise; };
  const first = card._loadCalendar();
  card._displayYear = 2028;
  const second = card._loadCalendar();
  requests[1].resolve({ days: [{ date: '2028-03-01' }] }); await second;
  requests[0].resolve({ days: [{ date: '2027-03-01' }] }); await first;
  assert.equal(card._loadedMonthKey, '2028-03');
  assert.equal(card._selectedDate, '2028-03-01');
  assert.equal(card._calendar.days[0].date, '2028-03-01');
  assert.equal(card._loading, false);
});

test('suggests all holiday names only when opening an ordinary exception creation', async () => {
  const card = cardFixture();
  await card._loadPublicHolidays();
  card._publicHolidays.days[0].names = ['Fête A', 'Fête B'];
  const before = JSON.stringify(card._configuration);
  card._openCreateCalendarExceptionDialog('2027-03-26');
  assert.equal(card._creatingCalendarExceptionDate, '2027-03-26');
  assert.deepEqual(card._creatingCalendarExceptionDraft, { day_type_id: '', description: 'Fête A / Fête B' });
  assert.equal(JSON.stringify(card._configuration), before);
  card._openCreateCalendarExceptionDialog('2027-03-27');
  assert.equal(card._creatingCalendarExceptionDraft.description, '');
});

test('never suggests holidays from an obsolete location or unavailable annual data', async () => {
  const card = cardFixture();
  card._openCreateCalendarExceptionDialog('2027-03-26');
  assert.equal(card._creatingCalendarExceptionDraft.description, '');
  await card._loadPublicHolidays();
  card._hass.config.latitude = 50;
  card._openCreateCalendarExceptionDialog('2027-03-26');
  assert.equal(card._creatingCalendarExceptionDraft.description, '');
});

test('escapes suggested names and preserves the draft after a late holiday response', async () => {
  const card = cardFixture();
  await card._loadPublicHolidays();
  card._publicHolidays.days[0].names = ['Fête "<test>"'];
  card._openCreateCalendarExceptionDialog('2027-03-26');
  const html = card._renderCreateCalendarExceptionDialog();
  assert.ok(html.includes('Fête &quot;&lt;test&gt;&quot;'));
  assert.ok(!html.includes('<test>'));
  card._creatingCalendarExceptionDraft.description = '';
  await card._loadPublicHolidays(true);
  assert.equal(card._creatingCalendarExceptionDraft.description, '');
});

test('saves the user description including an explicitly cleared suggestion', async () => {
  for (const description of ['Mon congé', '']) {
    const card = cardFixture();
    await card._loadPublicHolidays();
    card._openCreateCalendarExceptionDialog('2027-03-26');
    card.shadowRoot.querySelector = (selector) => ({ value:
      selector.endsWith('day-type') ? 'rest' : description });
    let saved;
    card._api.addCalendarException = async (...args) => { saved = args; };
    card._refreshCalendarConfiguration = async () => {};
    await card._saveCreateCalendarException();
    assert.deepEqual(saved, ['exception-2027-03-26', '2027-03-26', 'rest', description]);
  }
});

test('keeps existing descriptions and the fixed date when editing or duplicating', async () => {
  const card = cardFixture();
  await card._loadPublicHolidays();
  card._configuration.day_types = [{ id: 'rest', name: 'Repos' }];
  card._configuration.calendar_exceptions = [{ id: 'existing', date: '2027-03-26',
    day_type_id: 'rest', description: 'Description personnelle' }];
  card._editingCalendarExceptionId = 'existing';
  const html = card._renderEditCalendarExceptionDialog();
  assert.ok(html.includes('Description personnelle'));
  assert.ok(!html.includes('Vendredi saint'));
  assert.ok(!html.includes('type="date"'));
  card.shadowRoot.querySelector = (selector) => ({ value:
    selector.endsWith('day-type') ? 'rest' : 'Texte modifié' });
  let saved;
  card._api.updateCalendarException = async (...args) => { saved = args; };
  card._refreshCalendarConfiguration = async () => {};
  await card._saveEditCalendarException();
  assert.deepEqual(saved, ['existing', '2027-03-26', 'rest', 'Texte modifié']);
  card._openDuplicateCalendarExceptionDialog('existing');
  assert.equal(card._creatingCalendarExceptionDraft.description, 'Description personnelle');
  assert.equal(card._creatingCalendarExceptionDraft.date, '');
});

function exceptionForm(mode, language = 'fr') {
  const card = cardFixture(language);
  card._configuration.calendar_exceptions = [];
  card._openCreateCalendarExceptionDialog('2027-03-26');
  if (mode === 'edit') {
    card._creatingCalendarException = false;
    card._configuration.calendar_exceptions = [{ id: 'existing', date: '2027-03-26',
      day_type_id: 'rest', description: 'Original' }];
    card._editingCalendarExceptionId = 'existing';
  }
  const fields = { dayType: { value: 'rest' }, description: { value: '' }, date: { value: '2027-03-27' } };
  const handlers = {};
  const cancel = { addEventListener: (name, fn) => { handlers[name] = fn; },
    click: () => handlers.click(), disabled: false };
  card.shadowRoot.querySelector = (selector) => {
    if (selector === `#cancel-${mode}-calendar-exception`) return cancel;
    if (selector === `#${mode}-calendar-exception-day-type`) return fields.dayType;
    if (selector === `#${mode}-calendar-exception-description`) return fields.description;
    if (selector === '#duplicate-calendar-exception-date') return fields.date;
    return null;
  };
  card.shadowRoot.querySelectorAll = () => [];
  const calls = [];
  card._api.addCalendarException = async (...args) => { calls.push(args); };
  card._api.updateCalendarException = async (...args) => { calls.push(args); };
  let refreshed = 0;
  card._refreshCalendarConfiguration = async () => { refreshed++; };
  return { card, fields, cancel, calls, refreshed: () => refreshed,
    save: () => mode === 'create' ? card._saveCreateCalendarException() : card._saveEditCalendarException(),
    draft: () => mode === 'create' ? card._creatingCalendarExceptionDraft : card._editingCalendarExceptionDraft,
    html: () => mode === 'create' ? card._renderCreateCalendarExceptionDialog() : card._renderEditCalendarExceptionDialog() };
}

test('requires a configured day type in both forms with FR and EN messages', async () => {
  for (const mode of ['create', 'edit']) for (const language of ['fr', 'en']) {
    const form = exceptionForm(mode, language);
    for (const [value, key] of [['', 'calendar_exception_day_type_required'], ['removed', 'calendar_exception_day_type_unknown']]) {
      form.fields.dayType.value = value;
      form.fields.description.value = 'Texte conservé';
      await form.save();
      assert.equal(form.card._error, translations[language].errors[key]);
      assert.equal(form.calls.length, 0);
      assert.equal(form.draft().description, 'Texte conservé');
      assert.ok(form.html().includes('value="Texte conservé"'));
    }
  }
});

test('rejects duplicate dates for ordinary creation and duplication without changing the existing exception', async () => {
  for (const duplicate of [false, true]) {
    const form = exceptionForm('create');
    const existing = { id: 'existing', date: '2027-03-26', day_type_id: 'rest', description: 'Original' };
    form.card._configuration.calendar_exceptions = [existing];
    if (duplicate) {
      form.card._openDuplicateCalendarExceptionDialog('existing');
      form.fields.date.value = existing.date;
    }
    await form.save();
    assert.equal(form.card._error, translations.fr.errors.duplicate_calendar_exception_date);
    assert.equal(form.calls.length, 0);
    assert.equal(form.card._configuration.calendar_exceptions[0], existing);
    assert.equal(existing.description, 'Original');
  }
});

test('rejects invalid dates before making a creation request', async () => {
  const form = exceptionForm('create', 'en');
  for (const date of ['', '2027-02-30', 'not-a-date']) {
    form.card._creatingCalendarExceptionDate = date;
    await form.save();
    assert.equal(form.card._error, translations.en.errors.invalid_date);
  }
  assert.equal(form.calls.length, 0);
});

test('preserves even an empty description on backend failure and permits retry', async () => {
  for (const mode of ['create', 'edit']) for (const description of ['', 'Mon texte <libre>']) {
    const form = exceptionForm(mode);
    form.fields.description.value = description;
    const method = mode === 'create' ? 'addCalendarException' : 'updateCalendarException';
    form.card._api[method] = async () => { throw new Error('Refus du serveur'); };
    const original = console.error;
    try {
      console.error = () => {};
      await form.save();
    } finally { console.error = original; }
    assert.equal(form.card._error, 'Refus du serveur');
    assert.equal(form.draft().description, description);
    assert.equal(form.draft().day_type_id, 'rest');
    assert.equal(form.refreshed(), 0);
    assert.equal(form.card._loading, false);
    assert.ok(form.html().includes('Refus du serveur'));
    form.card._api[method] = async (...args) => { form.calls.push(args); };
    await form.save();
    assert.equal(form.calls.length, 1);
    assert.equal(form.calls[0][3], description);
    assert.equal(form.refreshed(), 1);
  }
});

test('prevents duplicate submissions and cancellation while saving either form', async () => {
  for (const mode of ['create', 'edit']) {
    const form = exceptionForm(mode);
    const pending = deferred();
    let requests = 0;
    form.card._api[mode === 'create' ? 'addCalendarException' : 'updateCalendarException'] = async () => {
      requests++; await pending.promise;
    };
    form.card._bindEvents();
    const saving = form.save();
    await form.save();
    assert.equal(requests, 1);
    assert.match(form.html(), new RegExp(`id="cancel-${mode}-calendar-exception"[^>]*disabled`));
    assert.match(form.html(), new RegExp(`id="save-${mode}-calendar-exception"[^>]*disabled`));
    form.cancel.click();
    assert.ok(mode === 'create' ? form.card._creatingCalendarException : form.card._editingCalendarExceptionId);
    pending.resolve(); await saving;
    assert.equal(form.refreshed(), 1);
    assert.equal(form.card._loading, false);
    assert.ok(!(mode === 'create' ? form.card._creatingCalendarException : form.card._editingCalendarExceptionId));
  }
});

test('cancel and Escape close the forms without writing', () => {
  for (const mode of ['create', 'edit']) for (const escape of [false, true]) {
    const form = exceptionForm(mode);
    form.card._bindEvents();
    if (escape) {
      let keydown;
      const dialog = { setAttribute() {}, isConnected: false,
        querySelector: (selector) => selector.startsWith('button') ? form.cancel : null,
        querySelectorAll: () => [], addEventListener: (_, fn) => { keydown = fn; } };
      const query = form.card.shadowRoot.querySelector;
      form.card.shadowRoot.querySelector = (selector) => selector === '.modal-backdrop .modal-dialog' ? dialog : query(selector);
      const original = globalThis.requestAnimationFrame;
      try {
        globalThis.requestAnimationFrame = () => {};
        form.card._setupModalAccessibility(false);
        keydown({ key: 'Escape', preventDefault() {}, stopPropagation() {} });
      } finally { globalThis.requestAnimationFrame = original; }
    } else form.cancel.click();
    assert.equal(form.calls.length, 0);
    assert.equal(form.refreshed(), 0);
    assert.equal(form.draft(), null);
    assert.ok(!(mode === 'create' ? form.card._creatingCalendarException : form.card._editingCalendarExceptionId));
  }
});
