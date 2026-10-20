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

import React from 'react';
import ReactDOM from 'react-dom/client';
import { createTheme } from '@mui/material/styles';
import DashboardIcon from '@mui/icons-material/Dashboard';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PersonIcon from '@mui/icons-material/Person';
import TrayCycleLogo from './assets/traycycle-scan.svg';



import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

import { AppProvider, type Navigation } from '@toolpad/core/AppProvider';
import { DashboardLayout } from '@toolpad/core/DashboardLayout';

const NAVIGATION: Navigation = [
  {
    kind: 'header',
    title: 'Main Items',
  },
  {
    segment: 'dashboard',
    title: 'Dashboard',
    icon: <DashboardIcon />,
  },
  {
    segment: 'about-us',
    title: 'About Us',
    icon: <PersonIcon />,
  },
  {
    segment: 'upload',
    title: 'Upload Captures',
    icon: <CloudUploadIcon />,
  },
];

const theme = createTheme({
  cssVariables: {
    colorSchemeSelector: 'data-material-color-scheme',
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

export default function App() {
  // State track active navigation menu item
  const [pathname, setPathname] = React.useState('/dashboard');

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
        logo: <img src={TrayCycleLogo} alt="TrayCycle logo" style={{ height: 75, width: 'auto' }} />,
        title: 'TrayCycle',
      }}
    >
      <DashboardLayout>
        <Box sx={{ py: 4, px: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="h4">
            Viewing: {pathname.replace('/', '').charAt(0).toUpperCase() + pathname.replace('/', '').slice(1)} Page
          </Typography>
          {/* use these checks when done with pages
          {pathname === '/dashboard' && <DashboardView />}
          {pathname === '/upload' && <UploadView />}
          {pathname === '/about-us' && <AboutUsView />}
          */}
          {pathname === '/dashboard' && (
            <Typography variant="body1">Welcome to TrayCycle.</Typography>
          )}
          {pathname === '/about-us' && (
            <Typography variant="body1">Learn more about us here.</Typography>
          )}
          {pathname === '/upload' && (
            <Typography variant="body1">Upload and manage your capture images here.</Typography>
          )}
        </Box>
      </DashboardLayout>
    </AppProvider>
  );
}
