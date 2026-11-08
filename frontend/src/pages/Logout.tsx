import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function Logout() {
    const { logout } = useAuth();
    const navigate = useNavigate();

    // Perform logout and redirect to login page
    useEffect(() => {
        logout();
        navigate("/login");
    }, [logout, navigate]);

    return null; // No UI needed for logout page
}
