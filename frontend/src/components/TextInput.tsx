import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';

export function TextInput() {
  const { t } = useTranslation();
  const { textInput, setTextInput } = useAppStore();

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {t('input.textLabel')}
      </label>
      <textarea
        className="input-field min-h-[180px] resize-y"
        placeholder={t('input.textPlaceholder')}
        value={textInput}
        onChange={(e) => setTextInput(e.target.value)}
      />
    </div>
  );
}
