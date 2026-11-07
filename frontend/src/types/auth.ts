export type User = {
    username: string;
    email: string;
} | null;

export type AuthContextValue = {
    token: string | null;
    user: User | null;
    loading: boolean;
    login: (username: string, password: string) => Promise<unknown>;
    logout: () => void;
};
