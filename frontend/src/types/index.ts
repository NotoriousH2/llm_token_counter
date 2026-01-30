// Model types
export type ModelType = 'commercial' | 'huggingface';

// API request/response types
export interface TokenCountRequest {
  text: string;
  model: string;
  model_type: ModelType;
}

export interface TokenCountResponse {
  token_count: number;
  cost_usd: number | null;
  context_window: number | null;
  context_usage_percent: number | null;
  model: string;
}

export interface ModelListResponse {
  official: string[];
  custom: string[];
  version: number;
}

export interface AddModelRequest {
  name: string;
  type: 'official' | 'custom';
}

export interface PricingInfoResponse {
  model: string;
  input_price: number | null;
  context_window: number | null;
  context_window_formatted: string | null;
}

export interface ErrorResponse {
  error: string;
  error_code?: string;
}

// WebSocket message types
export type WebSocketMessageType = 'init' | 'model_added' | 'add_model' | 'error';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data?: {
    official: string[];
    custom: string[];
    version: number;
  };
  error?: string;
  name?: string;
  category?: 'official' | 'custom';
}

// History entry type
export interface HistoryEntry {
  id: string;
  input: string;
  model: string;
  tokenCount: number;
  timestamp: number;
}

// App state
export interface AppState {
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

  // History
  history: HistoryEntry[];

  // Language
  language: 'ko' | 'en';

  // WebSocket
  wsConnected: boolean;
}
