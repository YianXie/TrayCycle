import type { LoginResponse, User } from "../types/auth";
import api from "./client";

export const login = async (
    username: string,
    password: string
): Promise<LoginResponse> => {
    const response = await api.post("/api/accounts/login", {
        username,
        password,
    });
    return response.data;
};

export const getMe = async (): Promise<User> => {
    const response = await api.get("/api/accounts/me");
    return response.data;
};
