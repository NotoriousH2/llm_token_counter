import { useCallback } from 'react';
import { useAppStore } from '@/stores/appStore';
import type { TokenCountRequest, TokenCountResponse, ErrorResponse } from '@/types';

const API_BASE = '/tokenizer/api';

export function useTokenCount() {
  const {
    selectedModel,
    modelType,
    textInput,
    selectedFile,
    inputMethod,
    setResult,
    setLoading,
    setError,
    addHistoryEntry,
  } = useAppStore();

  const countTokensFromText = useCallback(async () => {
    if (!selectedModel.trim()) {
      setError('Model name is required');
      return;
    }

    if (!textInput.trim()) {
      setError('Text input is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const request: TokenCountRequest = {
        text: textInput,
        model: selectedModel,
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

      const result: TokenCountResponse = await response.json();
      setResult(result);

      // Add to history
      addHistoryEntry({
        input: textInput.length > 20 ? textInput.substring(0, 20) + '...' : textInput,
        model: result.model,
        tokenCount: result.token_count,
      });

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, [selectedModel, textInput, modelType, setResult, setLoading, setError, addHistoryEntry]);

  const countTokensFromFile = useCallback(async () => {
    if (!selectedModel.trim()) {
      setError('Model name is required');
      return;
    }

    if (!selectedFile) {
      setError('File is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('model', selectedModel);
      formData.append('model_type', modelType);

      const response = await fetch(`${API_BASE}/count-tokens/file`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        throw new Error(errorData.error || `HTTP error ${response.status}`);
      }

      const result: TokenCountResponse = await response.json();
      setResult(result);

      // Add to history
      addHistoryEntry({
        input: selectedFile.name,
        model: result.model,
        tokenCount: result.token_count,
      });

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, [selectedModel, selectedFile, modelType, setResult, setLoading, setError, addHistoryEntry]);

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
