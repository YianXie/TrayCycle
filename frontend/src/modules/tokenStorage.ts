const LOCAL_STORAGE_TOKEN_KEY = "token";

export const tokenStorage = {
    setToken: (token: string) => {
        localStorage.setItem(LOCAL_STORAGE_TOKEN_KEY, token);
    },
    getToken: (): string | null => {
        return localStorage.getItem(LOCAL_STORAGE_TOKEN_KEY);
    },
    removeToken: () => {
        localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY);
    },
};
