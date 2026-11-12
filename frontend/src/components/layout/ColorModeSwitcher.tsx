/**
 * Color Mode Switcher component for the TriCycle web application.
 *
 * Allows the user to switch between light, dark, and system (auto) color modes.
 * The selected mode is persisted in localStorage.
 */
import BrightnessAutoIcon from "@mui/icons-material/BrightnessAuto";
import CheckIcon from "@mui/icons-material/Check";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import IconButton from "@mui/material/IconButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Tooltip from "@mui/material/Tooltip";
import { useColorScheme } from "@mui/material/styles";
import { useState } from "react";

type Mode = "light" | "dark" | "system";

const OPTIONS: { mode: Mode; label: string; icon: React.ReactNode }[] = [
    { mode: "light", label: "Light", icon: <LightModeIcon fontSize="small" /> },
    { mode: "dark", label: "Dark", icon: <DarkModeIcon fontSize="small" /> },
    {
        mode: "system",
        label: "Auto",
        icon: <BrightnessAutoIcon fontSize="small" />,
    },
];

// Lets the user pick light, dark, or auto (follow the OS). MUI persists the
// choice to localStorage, so it is remembered across visits.
export default function ColorModeSwitcher() {
    const { mode, setMode } = useColorScheme();
    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

    // `mode` is undefined until MUI has read the stored preference
    if (!mode) return null;

    const current = OPTIONS.find((o) => o.mode === mode) ?? OPTIONS[2];

    return (
        <>
            <Tooltip title={`Theme: ${current.label}`}>
                <IconButton
                    aria-label="Change color mode"
                    onClick={(e) => setAnchorEl(e.currentTarget)}
                >
                    {current.icon}
                </IconButton>
            </Tooltip>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
            >
                {OPTIONS.map((option) => (
                    <MenuItem
                        key={option.mode}
                        selected={option.mode === mode}
                        onClick={() => {
                            setMode(option.mode);
                            setAnchorEl(null);
                        }}
                    >
                        <ListItemIcon>{option.icon}</ListItemIcon>
                        <ListItemText>{option.label}</ListItemText>
                        {option.mode === mode && (
                            <CheckIcon fontSize="small" sx={{ ml: 2 }} />
                        )}
                    </MenuItem>
                ))}
            </Menu>
        </>
    );
}
