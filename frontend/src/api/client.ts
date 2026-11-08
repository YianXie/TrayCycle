import axios from "axios";

import { tokenStorage } from "../modules/tokenStorage";
import { router } from "../router";

// Pull the backend URL from Vite environment variables
const API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
    baseURL: API_URL,
    timeout: 10000, // 10 seconds timeout
});

// Request interceptor to inject the token dynamically
api.interceptors.request.use(
    (config) => {
        const token = tokenStorage.getToken();
        if (token) {
            config.headers.Authorization = `Token ${token}`; //
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to catch global errors (like 401 Unauthorized)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (
            error.response &&
            error.response.status === 401 &&
            !router.state.location.pathname.includes("/login")
        ) {
            // Token expired or invalid: Clear local storage and redirect to login
            tokenStorage.removeToken();
            router.navigate("/login", { replace: true });
        }
        return Promise.reject(error);
    }
);

export default api;
