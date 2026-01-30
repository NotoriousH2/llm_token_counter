import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';

export function ResultDisplay() {
  const { t } = useTranslation();
  const { results, isLoading, error } = useAppStore();

  const formatCost = (cost: number | null): string => {
    if (cost === null) return t('result.costUnknown');
    if (cost < 0.01) return `~$${cost.toFixed(6)}`;
    return `~$${cost.toFixed(4)}`;
  };

  const formatContextUsage = (
    usagePercent: number | null,
    contextWindow: number | null
  ): string => {
    if (usagePercent === null || contextWindow === null) {
      return t('result.contextUnknown');
    }

    let windowStr: string;
    if (contextWindow >= 1_000_000) {
      windowStr = `${Math.floor(contextWindow / 1_000_000)}M`;
    } else if (contextWindow >= 1000) {
      windowStr = `${Math.floor(contextWindow / 1000)}K`;
    } else {
      windowStr = String(contextWindow);
    }

    return `${usagePercent.toFixed(2)}% of ${windowStr}`;
  };

  if (isLoading) {
    return (
      <div className="result-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('result.title')}</h3>
        <div className="flex items-center justify-center py-8">
          <div className="spinner" />
          <span className="ml-3 text-gray-500">{t('button.calculating')}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="result-card border-red-200 bg-red-50">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('result.title')}</h3>
        <div className="text-red-600 text-sm">{error}</div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="result-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('result.title')}</h3>
        <div className="text-gray-500 text-center py-4">{t('result.noResults')}</div>
      </div>
    );
  }

  // Single result - show grid layout
  if (results.length === 1) {
    const result = results[0];
    return (
      <div className="result-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('result.title')}</h3>
        <div className="text-sm text-gray-500 mb-4">{result.model}</div>

        <div className="grid grid-cols-3 gap-4">
          {/* Token Count */}
          <div className="text-center">
            <div className="result-value text-primary-600">
              {result.token_count.toLocaleString()}
            </div>
            <div className="result-label">{t('result.tokens')}</div>
          </div>

          {/* Estimated Cost */}
          <div className="text-center">
            <div className="result-value text-green-600">
              {formatCost(result.cost_usd)}
            </div>
            <div className="result-label">{t('result.estimatedCost')}</div>
          </div>

          {/* Context Usage */}
          <div className="text-center">
            <div className="result-value text-orange-600 text-xl">
              {formatContextUsage(result.context_usage_percent, result.context_window)}
            </div>
            <div className="result-label">{t('result.contextUsage')}</div>
          </div>
        </div>
      </div>
    );
  }

  // Multiple results - show table layout
  return (
    <div className="result-card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('result.title')}</h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 px-3 font-medium text-gray-700">{t('result.model')}</th>
              <th className="text-right py-2 px-3 font-medium text-gray-700">{t('result.tokens')}</th>
              <th className="text-right py-2 px-3 font-medium text-gray-700">{t('result.estimatedCost')}</th>
              <th className="text-right py-2 px-3 font-medium text-gray-700">{t('result.contextUsage')}</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => (
              <tr
                key={result.model}
                className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}
              >
                <td className="py-2 px-3 text-gray-900 font-medium">{result.model}</td>
                <td className="py-2 px-3 text-right text-primary-600 font-semibold">
                  {result.token_count.toLocaleString()}
                </td>
                <td className="py-2 px-3 text-right text-green-600">
                  {formatCost(result.cost_usd)}
                </td>
                <td className="py-2 px-3 text-right text-orange-600">
                  {formatContextUsage(result.context_usage_percent, result.context_window)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
