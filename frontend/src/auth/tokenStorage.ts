/**
 * Token storage abstraction.
 *
 * Currently uses localStorage. To migrate to HttpOnly secure cookies,
 * replace this implementation — no other code needs to change.
 */
export interface TokenStore {
  getToken(): string | null;
  setToken(token: string): void;
  clearToken(): void;
}

class LocalStorageTokenStore implements TokenStore {
  private readonly key = "access_token";

  getToken(): string | null {
    return localStorage.getItem(this.key);
  }

  setToken(token: string): void {
    localStorage.setItem(this.key, token);
  }

  clearToken(): void {
    localStorage.removeItem(this.key);
  }
}

/** Singleton token store — swap the implementation to migrate storage. */
export const tokenStorage: TokenStore = new LocalStorageTokenStore();
