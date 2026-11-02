/**
 * Dashboard - Main screen to show the stats of our project
 *
 * Displays food wasted today, trends and other statistical information that the api returns
 */
import { Typography } from "@mui/material";

import { getStats } from "../api/stats";

export default function Dashboard() {
    return <Typography variant="body1">Welcome to TrayCycle.</Typography>;
}
