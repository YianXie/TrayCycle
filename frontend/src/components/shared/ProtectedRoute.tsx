import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
    const { token, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return <div>Loading authentication status...</div>;
    }

    // If no token exists, redirect the user to the login screen
    return token ? (
        children
    ) : (
        <Navigate to="/login" state={{ location: location.pathname }} replace />
    );
};

export default ProtectedRoute;
