import { useCallback } from 'react';
import { useAppStore } from '@/stores/appStore';
import type { TokenCountRequest, TokenCountResponse, ErrorResponse } from '@/types';

const API_BASE = '/tokenizer/api';

export function useTokenCount() {
  const {
    selectedModels,
    modelType,
    textInput,
    selectedFile,
    inputMethod,
    setResults,
    setLoading,
    setError,
    addHistoryEntry,
  } = useAppStore();

  const countTokensForModel = async (
    model: string,
    text: string
  ): Promise<TokenCountResponse> => {
    const request: TokenCountRequest = {
      text,
      model,
      model_type: modelType,
    };

    const response = await fetch(`${API_BASE}/count-tokens`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData: ErrorResponse = await response.json();
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }

    return response.json();
  };

  const countTokensForModelFromFile = async (
    model: string,
    file: File
  ): Promise<TokenCountResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', model);
    formData.append('model_type', modelType);

    const response = await fetch(`${API_BASE}/count-tokens/file`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData: ErrorResponse = await response.json();
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }

    return response.json();
  };

  const countTokensFromText = useCallback(async () => {
    if (selectedModels.length === 0) {
      setError('At least one model must be selected');
      return;
    }

    if (!textInput.trim()) {
      setError('Text input is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const promises = selectedModels.map((model) =>
        countTokensForModel(model, textInput)
      );

      const results = await Promise.all(promises);
      setResults(results);

      // Add to history (summarized entry)
      const inputPreview = textInput.length > 20 ? textInput.substring(0, 20) + '...' : textInput;
      results.forEach((result) => {
        addHistoryEntry({
          input: inputPreview,
          model: result.model,
          tokenCount: result.token_count,
        });
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setError(message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [selectedModels, textInput, modelType, setResults, setLoading, setError, addHistoryEntry]);

  const countTokensFromFile = useCallback(async () => {
    if (selectedModels.length === 0) {
      setError('At least one model must be selected');
      return;
    }

    if (!selectedFile) {
      setError('File is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const promises = selectedModels.map((model) =>
        countTokensForModelFromFile(model, selectedFile)
      );

      const results = await Promise.all(promises);
      setResults(results);

      // Add to history
      results.forEach((result) => {
        addHistoryEntry({
          input: selectedFile.name,
          model: result.model,
          tokenCount: result.token_count,
        });
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setError(message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [selectedModels, selectedFile, modelType, setResults, setLoading, setError, addHistoryEntry]);

  const countTokens = useCallback(async () => {
    if (inputMethod === 'file') {
      await countTokensFromFile();
    } else {
      await countTokensFromText();
    }
  }, [inputMethod, countTokensFromFile, countTokensFromText]);

  return {
    countTokens,
    countTokensFromText,
    countTokensFromFile,
  };
}
