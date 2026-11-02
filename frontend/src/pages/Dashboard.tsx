/**
 * Dashboard - Main screen to show the stats of our project
 *
 * Displays food wasted today, trends and other statistical information that the api returns
 */
import { Grid, Typography } from "@mui/material";
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

export default function Dashboard() {
    type Status = "loading" | "success" | "error";
    const [status, setStatus] = useState<Status>("loading");
    const [stats, setStats] = useState<Stats | null>(null);

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

    return (
        <div>
            <Grid container spacing={3}>
                {kpis(stats).map((k) => (
                    <Grid key={k.label} size={{ xs: 12, sm: 6, md: 3 }}>
                        <KpiCard {...k} />
                    </Grid>
                ))}
            </Grid>
        </div>
    );
}
