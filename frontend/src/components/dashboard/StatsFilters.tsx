import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";

import type { StatsParams } from "../../types/stats";

const isoDate = (date: Date) => date.toLocaleDateString("sv-SE");

const isoToday = () => isoDate(new Date());

const isoDaysAgo = (days: number) => {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return isoDate(date);
};

const PRESETS = [
    { label: "7 days", days: 6 },
    { label: "30 days", days: 29 },
];

type StatsFiltersProps = {
    params: StatsParams;
    onChange: (patch: Partial<StatsParams>) => void;
};

/**
 * Filter bar for the dashboard - date range presets plus manual from/to dates.
 *
 * Owns no state: every change is reported upwards so the caller stays the
 * single source of truth for what is being fetched.
 */
export default function StatsFilters({ params, onChange }: StatsFiltersProps) {
    const hasRange = Boolean(params.start || params.end);

    const isPresetActive = (days: number) =>
        params.start === isoDaysAgo(days) && params.end === isoToday();

    return (
        <Paper
            variant="outlined"
            sx={{
                p: 1.5,
                display: "flex",
                flexWrap: "wrap",
                alignItems: "center",
                gap: 1,
            }}
        >
            <Button
                size="small"
                variant={hasRange ? "outlined" : "contained"}
                onClick={() => onChange({ start: undefined, end: undefined })}
            >
                All time
            </Button>

            {PRESETS.map((preset) => (
                <Button
                    key={preset.label}
                    size="small"
                    variant={
                        isPresetActive(preset.days) ? "contained" : "outlined"
                    }
                    onClick={() =>
                        onChange({
                            start: isoDaysAgo(preset.days),
                            end: isoToday(),
                        })
                    }
                >
                    Last {preset.label}
                </Button>
            ))}

            <Stack direction="row" spacing={1}>
                <TextField
                    label="From"
                    type="date"
                    size="small"
                    value={params.start ?? ""}
                    onChange={(event) =>
                        onChange({ start: event.target.value || undefined })
                    }
                    slotProps={{ inputLabel: { shrink: true } }}
                    fullWidth
                />
                <TextField
                    label="To"
                    type="date"
                    size="small"
                    value={params.end ?? ""}
                    onChange={(event) =>
                        onChange({ end: event.target.value || undefined })
                    }
                    slotProps={{ inputLabel: { shrink: true } }}
                    fullWidth
                />
            </Stack>
        </Paper>
    );
}
