/**
 * Entry point for the TriCycle web application.
 *
 * Sets up the theme, authentication context, and router for the application.
 * Renders the application into the root DOM element.
 */
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { ToastContainer } from "react-toastify";

import { AuthProvider } from "./contexts/AuthContext.tsx";
import { router } from "./router.tsx";
import { COLOR_SCHEME_STORAGE_KEY, MODE_STORAGE_KEY, theme } from "./theme";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <ThemeProvider
            theme={theme}
            defaultMode="system"
            modeStorageKey={MODE_STORAGE_KEY}
            colorSchemeStorageKey={COLOR_SCHEME_STORAGE_KEY}
        >
            <CssBaseline />
            <AuthProvider>
                <RouterProvider router={router} />
            </AuthProvider>
            <ToastContainer />
        </ThemeProvider>
    </StrictMode>
);
