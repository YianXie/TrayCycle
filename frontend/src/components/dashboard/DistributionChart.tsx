import Typography from "@mui/material/Typography";
import { alpha, useTheme } from "@mui/material/styles";
import { BarChart } from "@mui/x-charts/BarChart";

import type { BucketValue, DishRow } from "../../types/stats";

const BUCKETS = [0, 25, 50, 75, 100] as const;

type DistributionRow = {
    dish: string;
    bowls: number;
} & { [K in `b${BucketValue}`]: number };

function toRows(dishes: DishRow[]): DistributionRow[] {
    return dishes.map((dish) => {
        const row = {
            dish: dish.dish_name,
            bowls: dish.bowl_count,
        } as DistributionRow;
        for (const bucket of BUCKETS) {
            const count = dish.waste_bucket_distribution[`${bucket}`] ?? 0;
            row[`b${bucket}`] = (count / dish.bowl_count) * 100;
        }
        return row;
    });
}

const SERIES = BUCKETS.map((bucket) => ({
    dataKey: `b${bucket}`,
    label: `${bucket}%`,
    stack: "waste",
}));

export default function DistributionChart({ dishes }: { dishes: DishRow[] }) {
    const theme = useTheme();
    const colors = BUCKETS.map((_, i) =>
        alpha(theme.palette.primary.main, 0.15 + i * 0.21)
    );

    const rows = toRows(dishes.filter((d) => d.bowl_count > 0));
    if (rows.length === 0) {
        return (
            <Typography color="text.secondary">No bowls recorded.</Typography>
        );
    }
    return (
        <BarChart
            layout="horizontal"
            height={72 + rows.length * 56}
            dataset={rows}
            series={SERIES.map((s, i) => ({ ...s, color: colors[i] }))}
            xAxis={[{ max: 100, label: "% of bowls" }]}
            yAxis={[{ scaleType: "band", dataKey: "dish" }]}
            slotProps={{
                legend: {
                    direction: "horizontal",
                    position: { vertical: "top", horizontal: "center" },
                },
            }}
            margin={{ left: 120 }}
        />
    );
}
