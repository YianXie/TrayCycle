/**
 * Router configuration for the TriCycle web application.
 *
 * Defines the routes and their corresponding components for the application.
 * Includes protected routes that require authentication, as well as public routes for login and logout.
 */
import { Outlet, createBrowserRouter } from "react-router-dom";

import Home from "./components/layout/AppShell";
import ProtectedRoute from "./components/shared/ProtectedRoute";
import AboutUs from "./pages/AboutUs";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Logout from "./pages/Logout";
import NotFound from "./pages/NotFound";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Home />,
        children: [
            {
                element: (
                    <ProtectedRoute>
                        <Outlet />
                    </ProtectedRoute>
                ),
                children: [
                    { path: "dashboard", element: <Dashboard /> },
                    { path: "about-us", element: <AboutUs /> },
                    { path: "*", element: <NotFound /> },
                ],
            },
        ],
    },
    { path: "login", element: <Login /> },
    { path: "logout", element: <Logout /> },
]);
