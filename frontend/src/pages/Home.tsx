/**
 * Home page component - Main landing page with personalized suggestions
 *
 * Displays personalized item suggestions based on user authentication status.
 * For authenticated users: shows "Recommended For You" and "Saved by You" sections.
 * For all users: displays items organized by predefined tags/categories.
 * Includes item comparison functionality with a bottom slider for selected items.
 */
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { createTheme } from "@mui/material/styles";
import { AppProvider, type Navigation } from "@toolpad/core/AppProvider";
import { DashboardLayout } from "@toolpad/core/DashboardLayout";
import React from "react";

import TrayCycleLogo from "/traycycle-scan.svg";

// Sidebar navigation stuff
const NAVIGATION: Navigation = [
    {
        kind: "header",
        title: "Main Items",
    },
    {
        segment: "dashboard",
        title: "Dashboard",
        icon: <DashboardIcon />,
    },
    {
        segment: "upload",
        title: "Upload Captures",
        icon: <CloudUploadIcon />,
    },
    {
        segment: "about-us",
        title: "About Us",
        icon: <PersonIcon />,
    },
];

// Theme for the webpage
const theme = createTheme({
    cssVariables: {
        colorSchemeSelector: "data-material-color-scheme",
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

// The thing that loads the webpage, uses Toolpad
export default function Home() {
    // State track active navigation menu item
    const [pathname, setPathname] = React.useState("/dashboard");

    const router = React.useMemo(() => {
        return {
            pathname,
            searchParams: new URLSearchParams(),
            navigate: (path: string | URL) => setPathname(String(path)),
        };
    }, [pathname]);

    return (
        <AppProvider
            navigation={NAVIGATION}
            router={router}
            theme={theme}
            branding={{
                logo: (
                    <img
                        src={TrayCycleLogo}
                        alt="TrayCycle logo"
                        style={{ height: 75, width: "auto" }}
                    />
                ),
                title: "TrayCycle",
            }}
        >
            <DashboardLayout>
                <Box
                    sx={{
                        py: 4,
                        px: 3,
                        display: "flex",
                        flexDirection: "column",
                        gap: 2,
                    }}
                >
                    <Typography variant="h4">
                        Viewing:{" "}
                        {pathname.replace("/", "").charAt(0).toUpperCase() +
                            pathname.replace("/", "").slice(1)}{" "}
                        Page
                    </Typography>
                    {/* use these checks when done with pages
          {pathname === '/dashboard' && <DashboardView />}
          {pathname === '/upload' && <UploadView />}
          {pathname === '/about-us' && <AboutUsView />}
          */}
                    {pathname === "/dashboard" && (
                        <Typography variant="body1">
                            Welcome to TrayCycle.
                        </Typography>
                    )}
                    {pathname === "/about-us" && (
                        <Typography variant="body1">
                            Learn more about us here.
                        </Typography>
                    )}
                    {pathname === "/upload" && (
                        <Typography variant="body1">
                            Upload and manage your capture images here.
                        </Typography>
                    )}
                </Box>
            </DashboardLayout>
        </AppProvider>
    );
}
