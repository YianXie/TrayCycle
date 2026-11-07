import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
    const { token, loading } = useAuth();

    if (loading) {
        return <div>Loading authentication status...</div>; // Prevents flashing white screens
    }

    // If no token exists, redirect the user to the login screen
    return token ? children : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
