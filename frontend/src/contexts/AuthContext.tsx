import axios from "axios";
import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { toast } from "react-toastify";

import { login as authLogin, getMe } from "../api/auth";
import { tokenStorage } from "../modules/tokenStorage";
import type { AuthContextValue, User } from "../types/auth";

const AuthContext = createContext<AuthContextValue>(
    null as unknown as AuthContextValue
);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [token, setToken] = useState<string | null>(tokenStorage.getToken());
    const [user, setUser] = useState<User>(null);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!token);
    const [loading, setLoading] = useState(true);

    const logout = () => {
        tokenStorage.removeToken();
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
    };

    // Authenticate user if a token already exists on load
    useEffect(() => {
        const fetchUser = async () => {
            if (token) {
                try {
                    const data = await getMe();
                    setUser(data);
                    setIsAuthenticated(true);
                } catch (error) {
                    if (
                        axios.isAxiosError(error) &&
                        error.response?.status === 401
                    ) {
                        toast.error("Session expired. Please log in again.");
                    } else {
                        toast.error(`Error fetching user data: ${error}`);
                    }
                    logout();
                }
            }
            setLoading(false);
        };
        fetchUser();
    }, [token]);

    const login = async (username: string, password: string) => {
        try {
            const { token, user } = await authLogin(username, password);
            tokenStorage.setToken(token);
            setToken(token);
            setUser(user);
            setIsAuthenticated(true);
        } catch (error) {
            if (axios.isAxiosError(error)) {
                if (error.response?.status === 401) {
                    toast.error("Invalid username or password.");
                } else {
                    toast.error(
                        `Login failed: ${
                            error.response?.data?.detail || error.message
                        }`
                    );
                }
            } else {
                toast.error(`Login failed: ${error}`);
            }
        }
    };

    return (
        <AuthContext.Provider
            value={{ token, user, loading, isAuthenticated, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
