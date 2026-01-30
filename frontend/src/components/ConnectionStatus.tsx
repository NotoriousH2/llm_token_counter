import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';

export function ConnectionStatus() {
  const { t } = useTranslation();
  const { wsConnected } = useAppStore();

  return (
    <div className="flex items-center gap-2 text-sm">
      <span
        className={`w-2 h-2 rounded-full ${
          wsConnected ? 'bg-green-500' : 'bg-gray-400'
        }`}
      />
      <span className="text-gray-500">
        {wsConnected ? t('status.wsConnected') : t('status.wsDisconnected')}
      </span>
    </div>
  );
}
