/**
 * Dashboard - Main screen to show the stats of our project
 *
 * Displays food wasted today, trends and other statistical information that the api returns
 */
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { LineChart } from "@mui/x-charts/LineChart";
import { isAxiosError } from "axios";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { getStats } from "../api/stats";
import DistributionChart from "../components/dashboard/DistributionChart";
import KpiCard from "../components/dashboard/KpiCard";
import StatsFilters from "../components/dashboard/StatsFilters";
import { parseParams, toSearch } from "../hooks/statFilters";
import type { StatsParams } from "../types/stats";
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
type RequestState = {
    key: string;
    status: Status;
    stats: Stats | null;
    error?: string;
};
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

const describeError = (error: unknown): string => {
    if (!isAxiosError(error)) return "Something went wrong.";
    if (error.code === "ERR_NETWORK") return "Can't reach the server.";
    if (error.code === "ECONNABORTED")
        return "The server took too long to respond.";
    const status = error.response?.status;
    if (status === 403) return "Your session expired.";
    if (status && status >= 500) return "The server is having trouble.";
    if (status === 401) return "Wrong username or password.";
    if (error.response?.status)
        return `Login failed (${error.response.status}).`;
    return "Something went wrong.";
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
            sx={{ borderRadius: 20, textTransform: "none" }}
        >
            {booed ? "Booed!" : "Boo"}
        </Button>
    );
}

export default function Dashboard() {
    const [searchParams, setSearchParams] = useSearchParams();
    const key = searchParams.toString();
    const [attempt, setAttempt] = useState(0);
    const params = parseParams(new URLSearchParams(key));
    const [request, setRequest] = useState<RequestState>({
        key,
        status: "loading",
        stats: null,
    });
    const retry = () => {
        setRequest({ key, status: "loading", stats: null });
        setAttempt((n) => n + 1);
    };
    useEffect(() => {
        const controller = new AbortController();
        getStats(parseParams(new URLSearchParams(key)), controller.signal)
            .then((data) => {
                setRequest({ key, status: "success", stats: data });
            })
            .catch((error) => {
                if (controller.signal.aborted) return;
                setRequest({
                    key,
                    status: "error",
                    stats: null,
                    error: describeError(error),
                });
            });
        return () => controller.abort();
    }, [key, attempt]);
    const update = (patch: Partial<StatsParams>) =>
        setSearchParams(toSearch({ ...params, ...patch }));
    const currentRequest =
        request.key === key
            ? request
            : { key, status: "loading" as const, stats: null };

    let body;
    if (currentRequest.status === "loading") {
        body = <Typography variant="body1">Loading...</Typography>;
    } else if (currentRequest.status === "error") {
        body = (
            <Alert
                severity="error"
                action={
                    <Button color="inherit" size="small" onClick={retry}>
                        Retry
                    </Button>
                }
            >
                {currentRequest.error ?? "Couldn't load statistics."}
            </Alert>
        );
    } else if (!currentRequest.stats) {
        body = <Typography variant="body1">No stats available.</Typography>;
    } else if (currentRequest.stats.bowl_count === 0) {
        body = (
            <Typography color="text.secondary">
                No captures in this range.
            </Typography>
        );
    } else {
        body = <StatsContent stats={currentRequest.stats} />;
    }

    return (
        <>
            <StatsFilters params={params} onChange={update} />
            <Box sx={{ mt: 3 }}>{body}</Box>
        </>
    );
}
const kg = (n: number) =>
    n > 0 && n < 0.01 ? "<0.01 kg" : `${n.toFixed(2)} kg`;

function StatsContent({ stats }: { stats: Stats }) {
    const firstDay = stats.daily.at(0)?.date;
    const lastDay = stats.daily.at(-1)?.date;
    const visible = stats.dishes.filter((dish) => dish.total_waste_kg > 0);

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
                <Grid container spacing={{ xs: 2, md: 3 }}>
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
                            valueFormatter: (v) =>
                                `${v?.toFixed(2) ?? "0.00"} kg`,
                        },
                    ]}
                    xAxis={[
                        {
                            dataKey: "date",
                            scaleType: "point",
                            valueFormatter: shortDay,
                        },
                    ]}
                    yAxis={[
                        { min: 0, width: 34, tickLabelStyle: { fontSize: 11 } },
                    ]}
                />
            </Box>
            <Box component="section" sx={{ mt: { xs: 3, md: 4 } }}>
                <Typography variant="h5" component="h2" gutterBottom>
                    Biggest food offenders
                </Typography>
                {visible.length === 0 ? (
                    <Typography color="text.secondary">
                        No waste recorded — every bowl was finished.
                    </Typography>
                ) : (
                    <Grid container spacing={3}>
                        {stats.dishes
                            .filter((d) => d.total_waste_kg > 0)
                            .map((dish) => (
                                <Grid
                                    key={dish.dish_id}
                                    size={{ xs: 12, sm: 6, md: 6 }}
                                >
                                    <KpiCard
                                        value={kg(dish.total_waste_kg)}
                                        label={dish.dish_name}
                                        hint={`${plural(dish.bowl_count, "bowl")} · avg ${Math.round(dish.average_waste_percent)}% level`}
                                        action={<BooButton />}
                                    />
                                </Grid>
                            ))}
                    </Grid>
                )}
            </Box>
            <Box component="section" sx={{ mt: { xs: 3, md: 4 } }}>
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
