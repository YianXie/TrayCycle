/**
 * Distribution Chart component for the TriCycle web application.
 *
 * Displays a horizontal stacked bar chart showing the distribution of waste buckets for each dish.
 * Each bar represents a dish, and the segments of the bar represent the percentage of bowls in each waste bucket (0%, 25%, 50%, 75%, 100%).
 * If no bowls are recorded for any dishes, a message is displayed instead of the chart.
 */
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { alpha, useTheme } from "@mui/material/styles";

import type { BucketValue, DishRow } from "../../types/stats";

const BUCKETS = [0, 25, 50, 75, 100] as const;

const BUCKET_LABELS: Record<BucketValue, string> = {
    0: "All eaten",
    25: "A quarter left",
    50: "Half left",
    75: "Most left",
    100: "Untouched",
};

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
        <Box>
            <Stack
                direction="row"
                spacing={1}
                sx={{ mb: 2, flexWrap: "wrap", gap: 1.5 }}
            >
                {BUCKETS.map((bucket, i) => (
                    <Stack
                        key={bucket}
                        direction="row"
                        spacing={1}
                        alignItems="center"
                    >
                        <Box
                            sx={{
                                width: 10,
                                height: 10,
                                borderRadius: "2px",
                                backgroundColor: colors[i],
                            }}
                        />
                        <Typography variant="caption" color="text.secondary">
                            {BUCKET_LABELS[bucket]}
                        </Typography>
                    </Stack>
                ))}
            </Stack>

            <Stack spacing={2}>
                {rows.map((row) => (
                    <Box key={row.dish}>
                        <Stack
                            direction="row"
                            sx={{ justifyContent: "space-between", mb: 0.5 }}
                        >
                            <Typography variant="body2">{row.dish}</Typography>
                            <Typography
                                variant="caption"
                                color="text.secondary"
                            >
                                {row.bowls} bowls
                            </Typography>
                        </Stack>
                        <Box
                            sx={{
                                display: "flex",
                                height: 24,
                                borderRadius: 1,
                                overflow: "hidden",
                            }}
                        >
                            {BUCKETS.map((bucket, i) => (
                                <Tooltip
                                    key={bucket}
                                    title={`${BUCKET_LABELS[bucket]} — ${row[`b${bucket}`].toFixed(0)}% of bowls`}
                                >
                                    <Box
                                        sx={{
                                            flexBasis: 0,
                                            flexGrow: row[`b${bucket}`],
                                            backgroundColor: colors[i],
                                            minWidth:
                                                row[`b${bucket}`] > 0 ? 6 : 0,
                                        }}
                                    />
                                </Tooltip>
                            ))}
                        </Box>
                    </Box>
                ))}
            </Stack>
        </Box>
    );
}
