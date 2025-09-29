import { defineStore } from 'pinia';
import { api } from '../boot/axios';

export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('auth_token'),
    isAuthenticated: !!localStorage.getItem('auth_token'),
  }),

  getters: {
    currentUser: (state): User | null => state.user,
    isLoggedIn: (state): boolean => state.isAuthenticated,
  },

  actions: {
    async login(email: string, password: string): Promise<void> {
      try {
        const response = await api.post<{ access_token: string; user: User }>(
          '/auth/login',
          {
            email,
            password,
          }
        );

        this.token = response.data.access_token;
        this.user = response.data.user;
        this.isAuthenticated = true;

        localStorage.setItem('auth_token', this.token);
      } catch (error) {
        throw error;
      }
    },

    async register(
      email: string,
      username: string,
      password: string,
      fullName?: string
    ): Promise<void> {
      try {
        const response = await api.post<{ access_token: string; user: User }>(
          '/auth/register',
          {
            email,
            username,
            password,
            full_name: fullName,
          }
        );

        this.token = response.data.access_token;
        this.user = response.data.user;
        this.isAuthenticated = true;

        localStorage.setItem('auth_token', this.token);
      } catch (error) {
        throw error;
      }
    },

    logout(): void {
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;
      localStorage.removeItem('auth_token');
    },

    async fetchUser(): Promise<void> {
      if (!this.isAuthenticated) return;

      try {
        const response = await api.get<User>('/auth/me');
        this.user = response.data;
      } catch (error) {
        this.logout();
        throw error;
      }
    },
  },
});
