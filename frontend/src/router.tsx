/**
 * Router configuration for the TriCycle web application.
 *
 * Defines the routes and their corresponding components for the application.
 * Includes protected routes that require authentication, as well as public routes for login and logout.
 */
import { createBrowserRouter } from "react-router-dom";

import Home from "./components/layout/AppShell";
import AboutUs from "./pages/AboutUs";
import Login from "./pages/Login";
import Logout from "./pages/Logout";
import NotFound from "./pages/NotFound";
import Dashboard from "./pages/Overview";
import PerdishBreakdown from "./pages/PerdishBreakdown";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Home />,
        children: [
            { path: "overview", element: <Dashboard /> },
            { path: "per-dish", element: <PerdishBreakdown /> },
            { path: "about-us", element: <AboutUs /> },
            { path: "*", element: <NotFound /> },
        ],
    },
    { path: "login", element: <Login /> },
    { path: "logout", element: <Logout /> },
]);
