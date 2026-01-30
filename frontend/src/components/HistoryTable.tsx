import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';

export function HistoryTable() {
  const { t } = useTranslation();
  const { history } = useAppStore();

  if (history.length === 0) {
    return (
      <div className="result-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('history.title')}</h3>
        <p className="text-gray-500 text-sm text-center py-4">{t('history.empty')}</p>
      </div>
    );
  }

  return (
    <div className="result-card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('history.title')}</h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 px-3 font-medium text-gray-500">
                {t('history.input')}
              </th>
              <th className="text-left py-2 px-3 font-medium text-gray-500">
                {t('history.model')}
              </th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">
                {t('history.count')}
              </th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry) => (
              <tr key={entry.id} className="border-b border-gray-100 last:border-0">
                <td className="py-2 px-3 text-gray-700 truncate max-w-[150px]" title={entry.input}>
                  {entry.input}
                </td>
                <td className="py-2 px-3 text-gray-700 truncate max-w-[150px]" title={entry.model}>
                  {entry.model}
                </td>
                <td className="py-2 px-3 text-right text-gray-900 font-medium">
                  {entry.tokenCount.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
