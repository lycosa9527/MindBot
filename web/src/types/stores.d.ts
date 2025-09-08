declare module '@/stores/common' {
  import { defineStore } from 'pinia';
  
  interface LogEntry {
    type: string;
    data: string;
  }

  interface PluginMarketItem {
    name: string;
    desc: string;
    author: string;
    repo: string;
    installed: boolean;
    version: string;
    social_link?: string;
    tags: string[];
    logo: string;
    pinned: boolean;
    stars: number;
    updated_at: string;
  }

  interface CommonState {
    eventSource: AbortController | null;
    log_cache: LogEntry[];
    sse_connected: boolean;
    log_cache_max_len: number;
    startTime: number;
    pluginMarketData: PluginMarketItem[];
  }

  interface CommonActions {
    createEventSource(): Promise<void>;
    closeEventSourcet(): void;
    getLogCache(): LogEntry[];
    getStartTime(): number | undefined;
    getPluginCollections(force?: boolean): Promise<PluginMarketItem[]>;
  }

  export const useCommonStore: () => {
    $state: CommonState;
  } & CommonActions;
}
