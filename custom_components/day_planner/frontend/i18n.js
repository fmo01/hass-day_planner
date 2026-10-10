const DEFAULT_LANGUAGE = 'en';

const SUPPORTED_LANGUAGES = ['fr', 'en'];

const cache = new Map();

function normalizeLanguage(language) {
  if (!language) {
    return DEFAULT_LANGUAGE;
  }

  const shortLanguage = language.toLowerCase().split('-')[0];

  return SUPPORTED_LANGUAGES.includes(shortLanguage) ? shortLanguage : DEFAULT_LANGUAGE;
}

async function loadTranslations(language) {
  const normalizedLanguage = normalizeLanguage(language);

  if (cache.has(normalizedLanguage)) {
    return cache.get(normalizedLanguage);
  }

  const response = await fetch(`/day_planner/frontend/translations/${normalizedLanguage}.json`);

  if (!response.ok) {
    throw new Error(`Unable to load translations: ${normalizedLanguage}`);
  }

  const translations = await response.json();

  cache.set(normalizedLanguage, translations);

  return translations;
}

function getNestedValue(object, key) {
  return key.split('.').reduce((value, part) => value?.[part], object);
}

export class DayPlannerI18n {
  constructor(hass) {
    this._hass = hass;
    this._translations = {};
    this._language = null;
  }

  setHass(hass) {
    this._hass = hass;
  }

  async load() {
    const language = normalizeLanguage(this._hass?.language || this._hass?.locale?.language);

    if (this._language === language && Object.keys(this._translations).length) {
      return;
    }

    this._translations = await loadTranslations(language);

    this._language = language;
  }

  t(key, fallback = key) {
    return getNestedValue(this._translations, key) ?? fallback;
  }
}
