import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';

export function ResultDisplay() {
  const { t } = useTranslation();
  const { result, isLoading, error } = useAppStore();

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

  return (
    <div className="result-card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('result.title')}</h3>

      <div className="grid grid-cols-3 gap-4">
        {/* Token Count */}
        <div className="text-center">
          <div className="result-value text-primary-600">
            {result ? result.token_count.toLocaleString() : '-'}
          </div>
          <div className="result-label">{t('result.tokens')}</div>
        </div>

        {/* Estimated Cost */}
        <div className="text-center">
          <div className="result-value text-green-600">
            {result ? formatCost(result.cost_usd) : '-'}
          </div>
          <div className="result-label">{t('result.estimatedCost')}</div>
        </div>

        {/* Context Usage */}
        <div className="text-center">
          <div className="result-value text-orange-600 text-xl">
            {result
              ? formatContextUsage(result.context_usage_percent, result.context_window)
              : '-'}
          </div>
          <div className="result-label">{t('result.contextUsage')}</div>
        </div>
      </div>
    </div>
  );
}
