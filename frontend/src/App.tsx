import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import Layout from "./components/layout/Layout";
import Home from "./pages/Home";

/**
 * Main App component that sets up routing and layout
 *
 * Defines all application routes with components for better performance.
 */
function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route
                        index
                        element={
                            <>
                                <Home />
                            </>
                        }
                    />
                </Route>
            </Routes>
        </Router>
    );
}

export default App;
