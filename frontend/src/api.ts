import axios from "axios";

import { router } from "./router";

// Pull the backend URL from Vite environment variables
const API_URL = import.meta.env.VITE_API_URL;

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Request interceptor to inject the token dynamically
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
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
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (
            error.response &&
            error.response.status === 401 &&
            !router.state.location.pathname.includes("/login")
        ) {
            // Token expired or invalid: Clear local storage and redirect to login
            localStorage.removeItem("token");
            router.navigate("/login", { replace: true });
        }
        return Promise.reject(error);
    }
);

export default apiClient;
