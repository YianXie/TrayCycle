import { createBrowserRouter } from "react-router-dom";

import Layout from "./components/layout/Layout";
import AboutUs from "./pages/AboutUs";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Login from "./pages/Login";
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
                    { path: "dashboard", element: <Dashboard /> },
                    { path: "about-us", element: <AboutUs /> },
                    { path: "login", element: <Login /> },
                    { path: "*", element: <NotFound /> },
                ],
            },
        ],
    },
]);
