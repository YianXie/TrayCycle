import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import { Account, PageContainer } from "@toolpad/core";
import type { Navigation } from "@toolpad/core/AppProvider";
import { DashboardLayout } from "@toolpad/core/DashboardLayout";
import { ReactRouterAppProvider } from "@toolpad/core/react-router";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext";
import usePageTitle from "../../hooks/usePageTitle";
import { theme } from "../../theme";
import ColorModeSwitcher from "./ColorModeSwitcher";
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

// Replaces Toolpad's default light/dark toggle with one that also has "Auto"
function ToolbarActions() {
    return (
        <Stack direction="row" alignItems="center">
            <ColorModeSwitcher />
            <Account />
        </Stack>
    );
}

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
            <DashboardLayout slots={{ toolbarActions: ToolbarActions }}>
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
