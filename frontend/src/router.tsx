import { Outlet, createBrowserRouter } from "react-router-dom";

import Layout from "./components/layout/Layout";
import ProtectedRoute from "./components/shared/ProtectedRoute";
import AboutUs from "./pages/AboutUs";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Logout from "./pages/Logout";
import NotFound from "./pages/NotFound";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Layout />,
        children: [
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
        ],
    },
]);
