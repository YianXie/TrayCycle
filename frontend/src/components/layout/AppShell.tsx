/**
 * AppShell component for the TriCycle web application.
 *
 * Provides the main layout for the application, including navigation, branding, and authentication.
 * Uses Toolpad's ReactRouterAppProvider and DashboardLayout to structure the application.
 * Displays the current page title based on the route and renders the corresponding page content.
 */
import DashboardIcon from "@mui/icons-material/Dashboard";
import InfoIcon from "@mui/icons-material/Info";
import PersonIcon from "@mui/icons-material/Person";
import Stack from "@mui/material/Stack";
import { Account, PageContainer } from "@toolpad/core";
import type { Navigation } from "@toolpad/core/AppProvider";
import { DashboardLayout } from "@toolpad/core/DashboardLayout";
import { ReactRouterAppProvider } from "@toolpad/core/react-router";
import { Outlet, useLocation } from "react-router-dom";

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
        segment: "overview",
        title: "Overview",
        icon: <DashboardIcon />,
    },
    {
        segment: "per-dish",
        title: "Per-dish Breakdown",
        icon: <InfoIcon />,
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
    const pages: Record<string, string> = {
        "/overview": "Overview",
        "/per-dish": "Per-dish Breakdown",
        "/about-us": "About Us",
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
                        style={{ height: 40, width: "auto" }}
                    />
                ),
                title: "TrayCycle",
            }}
        >
            <DashboardLayout slots={{ toolbarActions: ToolbarActions }}>
                <PageContainer
                    title={title}
                    breadcrumbs={[]}
                    sx={{ px: { xs: 2, sm: 3 }, py: { xs: 2, sm: 3 } }}
                >
                    <Outlet />
                </PageContainer>
            </DashboardLayout>
        </ReactRouterAppProvider>
    );
}
