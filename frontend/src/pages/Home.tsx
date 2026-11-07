/**
 * Home page component - Main landing page with personalized suggestions
 *
 * Displays personalized item suggestions based on user authentication status.
 * For authenticated users: shows "Recommended For You" and "Saved by You" sections.
 * For all users: displays items organized by predefined tags/categories.
 * Includes item comparison functionality with a bottom slider for selected items.
 */
// import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import Box from "@mui/material/Box";
// import Typography from "@mui/material/Typography";
import { createTheme } from "@mui/material/styles";
import { PageContainer } from "@toolpad/core";
import type { Navigation } from "@toolpad/core/AppProvider";
import { DashboardLayout } from "@toolpad/core/DashboardLayout";
import { ReactRouterAppProvider } from "@toolpad/core/react-router";
import { Outlet, useLocation } from "react-router-dom";

import usePageTitle from "../UsePageTitle";
// import Upload from "./Upload";
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
    // {
    //     segment: "upload",
    //     title: "Upload Captures",
    //     icon: <CloudUploadIcon />,
    // },
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
    const { pathname } = useLocation();
    const pages: Record<string, string> = {
        "/dashboard": "Dashboard",
        "/about-us": "About Us",
        "/upload": "Upload",
        "/": "Home",
    };
    const title = pages[pathname] ?? "Page not found";
    usePageTitle(pages[pathname] ?? "Page not found");
    return (
        <ReactRouterAppProvider
            navigation={NAVIGATION}
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
                    <PageContainer title={title}>
                        <Outlet />
                    </PageContainer>
                </Box>
            </DashboardLayout>
        </ReactRouterAppProvider>
    );
}
