import {
    Navigate,
    Route,
    BrowserRouter as Router,
    Routes,
} from "react-router-dom";

import Layout from "./components/layout/Layout";
import AboutUs from "./pages/AboutUs";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";

/**
 * Main App component that sets up routing and layout
 *
 * Defines all application routes with components for better performance.
 */
export default function App() {
    return (
        <Router>
            <Routes>
                <Route path="login" element={<Login />} />
                <Route element={<Layout />}>
                    <Route element={<Home />}>
                        <Route
                            index
                            element={<Navigate to="/dashboard" replace />}
                        />
                        <Route path="dashboard" element={<Dashboard />} />
                        <Route path="about-us" element={<AboutUs />} />
                        {/* <Route path="upload" element={<Upload />} /> */}
                        <Route path="*" element={<NotFound />} />
                    </Route>
                </Route>
            </Routes>
        </Router>
    );
}
