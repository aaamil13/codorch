import { defineStore } from 'pinia';

export interface MainState {
  loading: boolean;
  error: string | null;
}

export const useMainStore = defineStore('main', {
  state: (): MainState => ({
    loading: false,
    error: null,
  }),

  getters: {
    isLoading: (state): boolean => state.loading,
    hasError: (state): boolean => state.error !== null,
  },

  actions: {
    setLoading(loading: boolean): void {
      this.loading = loading;
    },

    setError(error: string | null): void {
      this.error = error;
    },

    clearError(): void {
      this.error = null;
    },
  },
});
