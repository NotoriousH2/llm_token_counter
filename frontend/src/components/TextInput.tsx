import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';

export function TextInput() {
  const { t } = useTranslation();
  const { textInput, setTextInput } = useAppStore();

  const handleExampleClick = (lang: 'korean' | 'english') => {
    setTextInput(t(`input.exampleText.${lang}`));
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="block text-sm font-medium text-gray-700">
          {t('input.textLabel')}
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => handleExampleClick('korean')}
            className="text-xs px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
          >
            {t('input.exampleButton.korean')}
          </button>
          <button
            type="button"
            onClick={() => handleExampleClick('english')}
            className="text-xs px-2 py-1 rounded bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
          >
            {t('input.exampleButton.english')}
          </button>
        </div>
      </div>
      <textarea
        className="input-field min-h-[180px] resize-y"
        placeholder={t('input.textPlaceholder')}
        value={textInput}
        onChange={(e) => setTextInput(e.target.value)}
      />
    </div>
  );
}
