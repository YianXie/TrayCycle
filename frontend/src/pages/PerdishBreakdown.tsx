import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { LineChart } from "@mui/x-charts/LineChart";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { getStats } from "../api/stats";
import DistributionChart from "../components/dashboard/DistributionChart";
import KpiCard from "../components/dashboard/KpiCard";
import StatsFilters from "../components/dashboard/StatsFilters";
import { parseParams, toSearch } from "../hooks/statFilters";
import type { DishRow, Stats, StatsParams } from "../types/stats";

export default function PerdishBreakdown() {
    const [searchParams, setSearchParams] = useSearchParams();
    const params = parseParams(searchParams);
    const { start, end, station } = params;
    const key = `${start}|${end}|${station}`;
    const [result, setResult] = useState<{
        key: string;
        stats?: Stats;
        error?: boolean;
    }>({ key: "" });

    useEffect(() => {
        const controller = new AbortController();
        getStats({ start, end, station }, controller.signal)
            .then((stats) => setResult({ key, stats }))
            .catch(() => {
                if (!controller.signal.aborted) setResult({ key, error: true });
            });
        return () => controller.abort();
    }, [key, start, end, station]);

    const current = result.key === key ? result : { key };
    const stats = current.stats;
    const error = current.error;

    const update = (patch: Partial<StatsParams>) =>
        setSearchParams(toSearch({ ...params, ...patch }));

    const dishes = stats?.dishes ?? [];
    const dish = dishes.find((d) => d.dish_id === params.dish) ?? dishes.at(0);

    let body;
    if (error)
        body = <Alert severity="error">Couldn&apos;t load statistics.</Alert>;
    else if (!stats) body = <Typography>Loading...</Typography>;
    else if (!dish)
        body = (
            <Typography color="text.secondary">
                No dishes in this range.
            </Typography>
        );
    else
        body = (
            <>
                <TextField
                    select
                    label="Dish"
                    size="small"
                    value={dish.dish_id}
                    onChange={(e) => update({ dish: Number(e.target.value) })}
                    sx={{ minWidth: 240, mb: 3 }}
                >
                    {dishes.map((d) => (
                        <MenuItem key={d.dish_id} value={d.dish_id}>
                            {d.dish_name}
                        </MenuItem>
                    ))}
                </TextField>
                <DishContent dish={dish} />
            </>
        );

    return (
        <>
            <StatsFilters params={params} onChange={update} />
            <Box sx={{ mt: 3 }}>{body}</Box>
        </>
    );
}

function DishContent({ dish }: { dish: DishRow }) {
    const kpis = [
        { label: "Bowls scanned", value: String(dish.bowl_count) },
        { label: "Food wasted", value: `${dish.total_waste_kg.toFixed(2)} kg` },
        {
            label: "Waste per bowl",
            value: `${dish.average_waste_kg.toFixed(2)} kg`,
        },
        {
            label: "Average waste level",
            value: `${Math.round(dish.average_waste_percent)}%`,
        },
    ];

    return (
        <>
            <Grid container spacing={{ xs: 2, md: 3 }}>
                {kpis.map((k) => (
                    <Grid key={k.label} size={{ xs: 12, sm: 6, md: 3 }}>
                        <KpiCard {...k} />
                    </Grid>
                ))}
            </Grid>
            <Box component="section" sx={{ mt: 4 }}>
                <Typography variant="h5" component="h2">
                    Waste per day
                </Typography>
                <LineChart
                    height={320}
                    dataset={dish.daily}
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
                            valueFormatter: (iso: string) => iso.slice(5),
                        },
                    ]}
                    yAxis={[
                        { min: 0, width: 34, tickLabelStyle: { fontSize: 11 } },
                    ]}
                />
            </Box>
            <Box component="section" sx={{ mt: 4 }}>
                <Typography variant="h5" component="h2" gutterBottom>
                    How much of each bowl wasted
                </Typography>
                <DistributionChart dishes={[dish]} />
            </Box>
        </>
    );
}
