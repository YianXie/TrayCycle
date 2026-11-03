/**
 * Dashboard - Main screen to show the stats of our project
 *
 * Displays food wasted today, trends and other statistical information that the api returns
 */
import { Box, Grid, Typography } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import { useEffect, useState } from "react";

import { getStats } from "../api/stats";
import KpiCard from "../components/dashboard/KpiCard";
import type { Stats } from "../types/stats";

const kpis = (stats: Stats) => [
    { label: "Bowls scanned", value: String(stats.bowl_count) },
    { label: "Food wasted", value: `${stats.total_waste_kg.toFixed(2)} kg` },
    {
        label: "Waste per bowl",
        value: `${stats.average_waste_kg.toFixed(2)} kg`,
    },
    {
        label: "Average waste level",
        value: `${Math.round(stats.average_waste_percent)}%`,
    },
];
type Status = "loading" | "success" | "error";

export default function Dashboard() {
    const [status, setStatus] = useState<Status>("loading");
    const [stats, setStats] = useState<Stats | null>(null);
    const shortDay = (iso: string) => iso.slice(5);
    useEffect(() => {
        let ignore = false;
        getStats({})
            .then((data) => {
                if (!ignore) {
                    setStats(data);
                    setStatus("success");
                }
            })
            .catch(() => {
                if (!ignore) setStatus("error");
            });
        return () => {
            ignore = true;
        };
    }, []);

    if (status === "loading") {
        return <Typography variant="body1">Loading...</Typography>;
    }

    if (status === "error") {
        return <Typography variant="body1">Error fetching stats.</Typography>;
    }

    if (!stats) {
        return <Typography variant="body1">No stats available.</Typography>;
    }

    if (stats.bowl_count === 0) {
        return <Typography color="text.secondary">No captures yet.</Typography>;
    }

    const firstDay = stats.daily.at(0)?.date;
    const lastDay = stats.daily.at(-1)?.date;

    return (
        <div>
            <Box component="section">
                <Typography variant="h5" component="h2" gutterBottom>
                    {firstDay && lastDay
                        ? `${shortDay(firstDay)} - ${shortDay(lastDay)}`
                        : "Waste by day"}
                </Typography>
                <Grid container spacing={3}>
                    {kpis(stats).map((k) => (
                        <Grid key={k.label} size={{ xs: 12, sm: 6, md: 3 }}>
                            <KpiCard {...k} />
                        </Grid>
                    ))}
                </Grid>
            </Box>
            <Box component="section" sx={{ mt: 4 }}>
                <Typography variant="h5" component="h2" gutterBottom>
                    Waste per day
                </Typography>
                <LineChart
                    height={320}
                    dataset={stats.daily}
                    series={[
                        {
                            dataKey: "total_waste_kg",
                            label: "Waste (kg)",
                            valueFormatter: (v) => `${v?.toFixed(2)} kg`,
                        },
                    ]}
                    xAxis={[
                        {
                            dataKey: "date",
                            scaleType: "point",
                            valueFormatter: shortDay,
                        },
                    ]}
                    yAxis={[{ label: "kg" }]}
                />
            </Box>
        </div>
    );
}
