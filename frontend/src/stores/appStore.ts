import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  ModelType,
  TokenCountResponse,
  HistoryEntry,
} from '@/types';

interface AppState {
  // Model selection
  modelType: ModelType;
  selectedModel: string;
  officialModels: string[];
  customModels: string[];
  modelVersion: number;

  // Input state
  inputMethod: 'text' | 'file';
  textInput: string;
  selectedFile: File | null;

  // Result state
  result: TokenCountResponse | null;
  isLoading: boolean;
  error: string | null;

  // History (last 5 entries)
  history: HistoryEntry[];

  // Language
  language: 'ko' | 'en';

  // WebSocket
  wsConnected: boolean;

  // Actions
  setModelType: (type: ModelType) => void;
  setSelectedModel: (model: string) => void;
  setModels: (official: string[], custom: string[], version: number) => void;
  setInputMethod: (method: 'text' | 'file') => void;
  setTextInput: (text: string) => void;
  setSelectedFile: (file: File | null) => void;
  setResult: (result: TokenCountResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addHistoryEntry: (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => void;
  clearHistory: () => void;
  setLanguage: (lang: 'ko' | 'en') => void;
  setWsConnected: (connected: boolean) => void;
  reset: () => void;
}

const initialState = {
  modelType: 'commercial' as ModelType,
  selectedModel: '',
  officialModels: [],
  customModels: [],
  modelVersion: 0,
  inputMethod: 'text' as const,
  textInput: '',
  selectedFile: null,
  result: null,
  isLoading: false,
  error: null,
  history: [],
  language: 'ko' as const,
  wsConnected: false,
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setModelType: (type) => {
        const state = get();
        const models = type === 'commercial' ? state.officialModels : state.customModels;
        set({
          modelType: type,
          selectedModel: models[0] || '',
        });
      },

      setSelectedModel: (model) => set({ selectedModel: model }),

      setModels: (official, custom, version) => {
        const state = get();
        const newState: Partial<AppState> = {
          officialModels: official,
          customModels: custom,
          modelVersion: version,
        };

        // Set default model if none selected
        if (!state.selectedModel) {
          const models = state.modelType === 'commercial' ? official : custom;
          newState.selectedModel = models[0] || '';
        }

        set(newState);
      },

      setInputMethod: (method) => set({ inputMethod: method }),

      setTextInput: (text) => set({ textInput: text }),

      setSelectedFile: (file) => set({ selectedFile: file }),

      setResult: (result) => set({ result }),

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),

      addHistoryEntry: (entry) => {
        const state = get();
        const newEntry: HistoryEntry = {
          ...entry,
          id: crypto.randomUUID(),
          timestamp: Date.now(),
        };
        // Keep only last 5 entries
        const newHistory = [newEntry, ...state.history].slice(0, 5);
        set({ history: newHistory });
      },

      clearHistory: () => set({ history: [] }),

      setLanguage: (lang) => {
        localStorage.setItem('language', lang);
        set({ language: lang });
      },

      setWsConnected: (connected) => set({ wsConnected: connected }),

      reset: () => set(initialState),
    }),
    {
      name: 'llm-token-counter-storage',
      partialize: (state) => ({
        history: state.history,
        language: state.language,
        modelType: state.modelType,
      }),
    }
  )
);
