import { createTheme } from "@mui/material/styles";

// Toolpad's AppProvider stores the color mode under these localStorage keys.
// The root ThemeProvider uses the same keys so pages outside the dashboard
// (login, logout) remember the same choice.
export const MODE_STORAGE_KEY = "toolpad-mode";
export const COLOR_SCHEME_STORAGE_KEY = "toolpad-color-scheme";

export const theme = createTheme({
    cssVariables: {
        colorSchemeSelector: "class",
    },
    colorSchemes: { light: true, dark: true },
    breakpoints: {
        values: {
            xs: 0,
            sm: 600,
            md: 960,
            lg: 1280,
            xl: 1920,
        },
    },
});
