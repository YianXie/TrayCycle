// import { useState } from "react";

// import "./App.css";
// import heroImg from "./assets/hero.png";
// import reactLogo from "./assets/react.svg";
// import viteLogo from "./assets/vite.svg";
// import Button from "@mui/material/Button";

// function App() {
//     const [count, setCount] = useState(0);

//     return (
//         <>
//             <section id="center">
//                 <div className="hero">
//                     <img
//                         src={heroImg}
//                         className="base"
//                         width="170"
//                         height="179"
//                         alt=""
//                     />
//                     <img
//                         src={reactLogo}
//                         className="framework"
//                         alt="React logo"
//                     />
//                     <img src={viteLogo} className="vite" alt="Vite logo" />
//                 </div>
//                 <div>
//                     <h1>Get started</h1>
//                     <p>
//                         Edit <code>src/App.tsx</code> and save to test{" "}
//                         <code>HMR</code>
//                     </p>
//                 </div>
//                 {/* <button
//                     type="button"
//                     className="counter"
//                     onClick={() => setCount((count) => count + 1)}
//                 >
//                     Count is {count}
//                 </button> */}
//                 <Button
//                     variant="contained"
//                     color="primary"
//                     onClick={() => setCount((count) => count + 1)}
//                 >
//                     Count is {count}
//                 </Button>
//             </section>

//             <section id="test">
//                 <div className="panel-container">
//                     <div className="panelSquare">
//                         <h2>Test Section</h2>
//                         <p>This is a simple test section.</p>
//                     </div>
//                     <div className="panelSquare">
//                         <h2>Test Section 2</h2>
//                         <p>This is a simple test section.</p>
//                     </div>
//                 </div>
//             </section>

//             <div className="ticks"></div>

//             <section id="next-steps">
//                 <div id="docs">
//                     <svg
//                         className="icon"
//                         role="presentation"
//                         aria-hidden="true"
//                     >
//                         <use href="/icons.svg#documentation-icon"></use>
//                     </svg>
//                     <h2>Documentation</h2>
//                     <p>Your questions, answered</p>
//                     <ul>
//                         <li>
//                             <a href="https://vite.dev/" target="_blank">
//                                 <img className="logo" src={viteLogo} alt="" />
//                                 Explore Vite
//                             </a>
//                         </li>
//                         <li>
//                             <a href="https://react.dev/" target="_blank">
//                                 <img
//                                     className="button-icon"
//                                     src={reactLogo}
//                                     alt=""
//                                 />
//                                 Learn more
//                             </a>
//                         </li>
//                     </ul>
//                 </div>
//                 <div id="social">
//                     <svg
//                         className="icon"
//                         role="presentation"
//                         aria-hidden="true"
//                     >
//                         <use href="/icons.svg#social-icon"></use>
//                     </svg>
//                     <h2>Connect with us</h2>
//                     <p>Join the Vite community</p>
//                     <ul>
//                         <li>
//                             <a
//                                 href="https://github.com/vitejs/vite"
//                                 target="_blank"
//                             >
//                                 <svg
//                                     className="button-icon"
//                                     role="presentation"
//                                     aria-hidden="true"
//                                 >
//                                     <use href="/icons.svg#github-icon"></use>
//                                 </svg>
//                                 GitHub
//                             </a>
//                         </li>
//                         <li>
//                             <a href="https://chat.vite.dev/" target="_blank">
//                                 <svg
//                                     className="button-icon"
//                                     role="presentation"
//                                     aria-hidden="true"
//                                 >
//                                     <use href="/icons.svg#discord-icon"></use>
//                                 </svg>
//                                 Discord
//                             </a>
//                         </li>
//                         <li>
//                             <a href="https://x.com/vite_js" target="_blank">
//                                 <svg
//                                     className="button-icon"
//                                     role="presentation"
//                                     aria-hidden="true"
//                                 >
//                                     <use href="/icons.svg#x-icon"></use>
//                                 </svg>
//                                 X.com
//                             </a>
//                         </li>
//                         <li>
//                             <a
//                                 href="https://bsky.app/profile/vite.dev"
//                                 target="_blank"
//                             >
//                                 <svg
//                                     className="button-icon"
//                                     role="presentation"
//                                     aria-hidden="true"
//                                 >
//                                     <use href="/icons.svg#bluesky-icon"></use>
//                                 </svg>
//                                 Bluesky
//                             </a>
//                         </li>
//                     </ul>
//                 </div>
//             </section>

//             <div className="ticks"></div>
//             <section id="spacer"></section>
//         </>
//     );
// }

// export default App;


import React from 'react';
import ReactDOM from 'react-dom/client';
import { createTheme } from '@mui/material/styles';
import DashboardIcon from '@mui/icons-material/Dashboard';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PersonIcon from '@mui/icons-material/Person';


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
