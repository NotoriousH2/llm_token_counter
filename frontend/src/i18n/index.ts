import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import ko from './ko.json';
import en from './en.json';

// Get saved language or default to Korean
const savedLanguage = typeof window !== 'undefined'
  ? localStorage.getItem('language') || 'ko'
  : 'ko';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      ko: { translation: ko },
      en: { translation: en },
    },
    lng: savedLanguage,
    fallbackLng: 'ko',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
