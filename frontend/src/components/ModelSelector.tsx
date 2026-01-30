import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores/appStore';
import { useModelStore } from '@/hooks/useModelStore';

export function ModelSelector() {
  const { t } = useTranslation();
  const { modelType, selectedModel, setSelectedModel } = useAppStore();
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
    const value = e.target.value;
    setSearchTerm(value);
    setSelectedModel(value);
    setIsOpen(true);
  };

  const handleSelect = (model: string) => {
    setSelectedModel(model);
    setSearchTerm(model);
    setIsOpen(false);
  };

  const handleFocus = () => {
    setIsOpen(true);
    setSearchTerm(selectedModel);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {t('model.selectLabel')}
      </label>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          className="input-field pr-10"
          placeholder={placeholder}
          value={selectedModel}
          onChange={handleInputChange}
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

      {isOpen && filteredModels.length > 0 && (
        <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {filteredModels.map((model) => (
            <li
              key={model}
              className={`px-4 py-2 cursor-pointer hover:bg-primary-50 ${
                model === selectedModel ? 'bg-primary-100 text-primary-700' : 'text-gray-700'
              }`}
              onClick={() => handleSelect(model)}
            >
              {model}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
