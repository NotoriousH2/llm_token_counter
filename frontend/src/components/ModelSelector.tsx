import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';
import { useModelStore } from '@/hooks/useModelStore';

export function ModelSelector() {
  const { t } = useTranslation();
  const { modelType, selectedModels, toggleModel, setSelectedModels } = useAppStore();
  const { getCurrentModels } = useModelStore();

  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const models = getCurrentModels();

  const filteredModels = models.filter((model) =>
    model.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const placeholder = modelType === 'commercial'
    ? t('model.commercialPlaceholder')
    : t('model.huggingfacePlaceholder');

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setIsOpen(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchTerm.trim()) {
      e.preventDefault();
      const modelName = searchTerm.trim();
      if (!selectedModels.includes(modelName)) {
        setSelectedModels([...selectedModels, modelName]);
      }
      setSearchTerm('');
    }
  };

  const handleToggleModel = (model: string) => {
    toggleModel(model);
  };

  const handleRemoveModel = (model: string) => {
    setSelectedModels(selectedModels.filter((m) => m !== model));
  };

  const handleFocus = () => {
    setIsOpen(true);
  };

  const handleSelectAll = () => {
    setSelectedModels(filteredModels);
  };

  const handleClearAll = () => {
    setSelectedModels([]);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {t('model.selectLabel')}
      </label>

      {/* Selected Models Tags */}
      {selectedModels.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {selectedModels.map((model) => (
            <span
              key={model}
              className="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-700 text-sm rounded-full"
            >
              {model}
              <button
                type="button"
                onClick={() => handleRemoveModel(model)}
                className="hover:text-primary-900"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          className="input-field pr-10"
          placeholder={selectedModels.length > 0 ? t('model.addMore') : placeholder}
          value={searchTerm}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
        />
        <button
          type="button"
          className="absolute inset-y-0 right-0 flex items-center px-2 text-gray-400 hover:text-gray-600"
          onClick={() => setIsOpen(!isOpen)}
        >
          <svg
            className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
          {/* Select All / Clear All */}
          <div className="flex justify-between px-4 py-2 border-b border-gray-100 text-sm">
            <button
              type="button"
              className="text-primary-600 hover:text-primary-800"
              onClick={handleSelectAll}
            >
              {t('model.selectAll')}
            </button>
            <button
              type="button"
              className="text-gray-500 hover:text-gray-700"
              onClick={handleClearAll}
            >
              {t('model.clearAll')}
            </button>
          </div>

          {/* Model List */}
          <ul className="max-h-60 overflow-auto">
            {filteredModels.length > 0 ? (
              filteredModels.map((model) => {
                const isSelected = selectedModels.includes(model);
                return (
                  <li
                    key={model}
                    className={`px-4 py-2 cursor-pointer hover:bg-primary-50 flex items-center gap-2 ${
                      isSelected ? 'bg-primary-100' : ''
                    }`}
                    onClick={() => handleToggleModel(model)}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <span className={isSelected ? 'text-primary-700 font-medium' : 'text-gray-700'}>
                      {model}
                    </span>
                  </li>
                );
              })
            ) : searchTerm.trim() ? (
              <li className="px-4 py-2 text-gray-500 text-sm">
                {t('model.pressEnterToAdd', { model: searchTerm.trim() })}
              </li>
            ) : (
              <li className="px-4 py-2 text-gray-500 text-sm">{t('model.noResults')}</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
