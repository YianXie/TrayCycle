import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { toast } from "react-toastify";

import apiClient from "../api";
import type { AuthContextValue, User } from "../types/auth";

const AuthContext = createContext<AuthContextValue>(
    null as unknown as AuthContextValue
);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [token, setToken] = useState<string | null>(
        localStorage.getItem("token")
    );
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const logout = () => {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
    };

    // Authenticate user if a token already exists on load
    useEffect(() => {
        const fetchUser = async () => {
            if (token) {
                try {
                    const response = await apiClient.get("/api/accounts/me");
                    setUser(response.data);
                } catch (error) {
                    toast.error(`Error fetching user data: ${error}`);
                    logout();
                }
            }
            setLoading(false);
        };
        fetchUser();
    }, [token]);

    const login = async (username: string, password: string) => {
        const response = await apiClient.post("/api/accounts/login", {
            username,
            password,
        });
        const { token: userToken, user: userData } = response.data;

        localStorage.setItem("token", userToken);
        setToken(userToken);
        setUser(userData);
        return response.data;
    };

    return (
        <AuthContext.Provider value={{ token, user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
