import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useModelStore } from '@/hooks/useModelStore';
import { useTokenCount } from '@/hooks/useTokenCount';
import {
  ModelSelector,
  TextInput,
  FileUpload,
  ResultDisplay,
  HistoryTable,
  LanguageToggle,
  Tab,
  TabPanel,
  TabGroup,
  ConnectionStatus,
} from '@/components';

function App() {
  const { t } = useTranslation();
  const {
    modelType,
    setModelType,
    inputMethod,
    setInputMethod,
    isLoading,
  } = useAppStore();

  // Initialize WebSocket connection
  useWebSocket();

  // Initialize model store
  useModelStore();

  // Token counting
  const { countTokens } = useTokenCount();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {t('title')}
              </h1>
              <p className="text-sm text-gray-500">{t('subtitle')}</p>
            </div>
            <div className="flex flex-col items-end gap-2">
              <LanguageToggle />
              <ConnectionStatus />
            </div>
          </div>

          <div className="mt-4 p-3 bg-primary-50 rounded-lg">
            <p className="text-sm text-primary-700">{t('quickStart')}</p>
          </div>
        </header>

        {/* Main Content */}
        <main className="space-y-6">
          {/* Model Type Tabs */}
          <section className="bg-white rounded-lg shadow-sm p-4">
            <TabGroup>
              <Tab
                id="commercial"
                label={t('tabs.commercial')}
                isActive={modelType === 'commercial'}
                onClick={() => setModelType('commercial')}
              />
              <Tab
                id="huggingface"
                label={t('tabs.huggingface')}
                isActive={modelType === 'huggingface'}
                onClick={() => setModelType('huggingface')}
              />
            </TabGroup>

            <div className="mt-4">
              {/* Model Selector */}
              <ModelSelector />

              {/* Input Method Tabs */}
              <div className="mt-6">
                <TabGroup>
                  <Tab
                    id="text"
                    label={t('tabs.textInput')}
                    isActive={inputMethod === 'text'}
                    onClick={() => setInputMethod('text')}
                  />
                  <Tab
                    id="file"
                    label={t('tabs.fileUpload')}
                    isActive={inputMethod === 'file'}
                    onClick={() => setInputMethod('file')}
                  />
                </TabGroup>

                <TabPanel isActive={inputMethod === 'text'}>
                  <TextInput />
                </TabPanel>

                <TabPanel isActive={inputMethod === 'file'}>
                  <FileUpload />
                </TabPanel>
              </div>

              {/* Calculate Button */}
              <div className="mt-6">
                <button
                  type="button"
                  className="btn-primary w-full"
                  onClick={countTokens}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="spinner" />
                      {t('button.calculating')}
                    </span>
                  ) : (
                    t('button.calculate')
                  )}
                </button>
              </div>
            </div>
          </section>

          {/* Results */}
          <section>
            <ResultDisplay />
          </section>

          {/* History */}
          <section>
            <HistoryTable />
          </section>
        </main>

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-400">
          <a
            href="https://github.com/NotoriousH2/llm_token_counter"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-primary-500"
          >
            GitHub Repository
          </a>
        </footer>
      </div>
    </div>
  );
}

export default App;
