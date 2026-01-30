import { useEffect, useCallback } from 'react';
import { useAppStore } from '@/stores/appStore';
import type { ModelListResponse } from '@/types';

const API_BASE = '/tokenizer/api';

export function useModelStore() {
  const {
    officialModels,
    customModels,
    modelVersion,
    modelType,
    selectedModel,
    setModels,
    setSelectedModel,
  } = useAppStore();

  const fetchModels = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/models`);
      if (!response.ok) {
        throw new Error('Failed to fetch models');
      }
      const data: ModelListResponse = await response.json();
      setModels(data.official, data.custom, data.version);

      // Set default model if none selected
      if (!selectedModel) {
        const models = modelType === 'commercial' ? data.official : data.custom;
        if (models.length > 0) {
          setSelectedModel(models[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    }
  }, [modelType, selectedModel, setModels, setSelectedModel]);

  // Fetch models on mount
  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  const getCurrentModels = useCallback(() => {
    return modelType === 'commercial' ? officialModels : customModels;
  }, [modelType, officialModels, customModels]);

  return {
    officialModels,
    customModels,
    modelVersion,
    getCurrentModels,
    refreshModels: fetchModels,
  };
}
