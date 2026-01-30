import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';

export function LanguageToggle() {
  const { t, i18n } = useTranslation();
  const { language, setLanguage } = useAppStore();

  const handleToggle = () => {
    const newLang = language === 'ko' ? 'en' : 'ko';
    setLanguage(newLang);
    i18n.changeLanguage(newLang);
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-500">{t('language.setting')}</span>
      <button
        type="button"
        className="btn-secondary text-sm"
        onClick={handleToggle}
      >
        {t('language.toggle')}
      </button>
    </div>
  );
}
