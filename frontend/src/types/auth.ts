export type LoginResponse = {
    token: string;
    user: User;
};

export type User = {
    id: string;
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
