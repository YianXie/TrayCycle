import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import Box from "@mui/material/Box";
import { createTheme } from "@mui/material/styles";
import { PageContainer } from "@toolpad/core";
import type { Navigation } from "@toolpad/core/AppProvider";
import { DashboardLayout } from "@toolpad/core/DashboardLayout";
import { ReactRouterAppProvider } from "@toolpad/core/react-router";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import usePageTitle from "../../hooks/usePageTitle";
import TrayCycleLogo from "/logo.png";

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
    const { pathname } = useLocation();
    const navigate = useNavigate();
    const { user } = useAuth();
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
            authentication={{
                signIn: () => navigate("/login"),
                signOut: () => navigate("/logout"),
            }}
            session={{
                user: {
                    id: user?.id ?? null,
                    name: user?.username ?? null,
                    image: null,
                    email: user?.email ?? null,
                },
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
