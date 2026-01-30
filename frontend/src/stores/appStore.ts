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
  selectedModels: string[];
  officialModels: string[];
  customModels: string[];
  modelVersion: number;

  // Input state
  inputMethod: 'text' | 'file';
  textInput: string;
  selectedFile: File | null;

  // Result state
  results: TokenCountResponse[];
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
  setSelectedModels: (models: string[]) => void;
  toggleModel: (model: string) => void;
  setModels: (official: string[], custom: string[], version: number) => void;
  setInputMethod: (method: 'text' | 'file') => void;
  setTextInput: (text: string) => void;
  setSelectedFile: (file: File | null) => void;
  setResults: (results: TokenCountResponse[]) => void;
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
  selectedModels: [] as string[],
  officialModels: [] as string[],
  customModels: [] as string[],
  modelVersion: 0,
  inputMethod: 'text' as const,
  textInput: '',
  selectedFile: null as File | null,
  results: [] as TokenCountResponse[],
  isLoading: false,
  error: null as string | null,
  history: [] as HistoryEntry[],
  language: 'ko' as const,
  wsConnected: false,
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setModelType: (type) => {
        set({
          modelType: type,
          selectedModels: [],
        });
      },

      setSelectedModels: (models) => set({ selectedModels: models }),

      toggleModel: (model) => {
        const state = get();
        const isSelected = state.selectedModels.includes(model);
        if (isSelected) {
          set({ selectedModels: state.selectedModels.filter((m) => m !== model) });
        } else {
          set({ selectedModels: [...state.selectedModels, model] });
        }
      },

      setModels: (official, custom, version) => {
        set({
          officialModels: official,
          customModels: custom,
          modelVersion: version,
        });
      },

      setInputMethod: (method) => set({ inputMethod: method }),

      setTextInput: (text) => set({ textInput: text }),

      setSelectedFile: (file) => set({ selectedFile: file }),

      setResults: (results) => set({ results }),

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
