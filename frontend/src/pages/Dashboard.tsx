/**
 * Dashboard - Main screen to show the stats of our project
 *
 * Displays food wasted today, trends and other statistical information that the api returns
 */
import { Box, Button, Grid, Typography } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import { useEffect, useState } from "react";

import { getStats } from "../api/stats";
import DistributionChart from "../components/dashboard/DistributionChart";
import KpiCard from "../components/dashboard/KpiCard";
import type { DishRow, Stats } from "../types/stats";

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
const shortDay = (iso: string) => iso.slice(5);
const MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
];

const dayLabel = (iso: string) => {
    const [y, m, d] = iso.split("-");
    return `${Number(d)} ${MONTHS[Number(m) - 1]} ${y}`;
};

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

function BooButton() {
    const [booed, setBooed] = useState(false);

    return (
        <Button
            variant={booed ? "contained" : "outlined"}
            color={booed ? "error" : "inherit"}
            onClick={() => setBooed(!booed)}
            startIcon={booed ? "🍅" : "👎"}
            size="small"
            sx={{ borderRadius: 20, textTransform: "none" }} // Rounded pill shape, clean text
        >
            {booed ? "Booed!" : "Boo"}
        </Button>
    );
}

export default function Dashboard() {
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

    const firstDay = stats.daily.at(0)?.date;
    const lastDay = stats.daily.at(-1)?.date;

    return (
        <div>
            <Box component="section">
                <Typography variant="h5" component="h2" gutterBottom>
                    Waste at a glance
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                    {firstDay && lastDay
                        ? `${dayLabel(firstDay)} - ${dayLabel(lastDay)}`
                        : "All captures"}
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
                <Typography variant="h5" component="h2">
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
            <Box component="section" sx={{ mt: 4 }}>
                <Typography variant="h5" component="h2" gutterBottom>
                    Biggest food offenders
                </Typography>
                <Grid container spacing={3}>
                    {stats.dishes.map((dish) => (
                        <Grid
                            key={dish.dish_id}
                            size={{ xs: 12, sm: 6, md: 6 }}
                        >
                            <KpiCard
                                value={`${dish.total_waste_kg.toFixed(2)} kg`}
                                label={dish.dish_name}
                                hint={`${plural(dish.bowl_count, "bowl")} · avg ${Math.round(dish.average_waste_percent)}% level`}
                                action={<BooButton />}
                            />
                        </Grid>
                    ))}
                </Grid>
            </Box>
            <Box component="section" sx={{ mt: 4 }}>
                <Typography variant="h5" component="h2" gutterBottom>
                    How much of each bowl wasted
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                    Distribution of bowls by waste level
                </Typography>
                <DistributionChart dishes={stats.dishes} />
            </Box>
        </div>
    );
}
