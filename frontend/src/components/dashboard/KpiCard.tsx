import { Box, Card, CardContent, Typography } from "@mui/material";

export type KpiCardProps = {
    value: string;
    label: string;
    hint?: string;
};

function KpiCard({ value, label, hint }: KpiCardProps) {
    return (
        <Card
            variant="outlined"
            sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                borderColor: "divider",
                "&:hover": {
                    boardColor: "primary.main",
                    boxShadow: 3,
                },
            }}
        >
            <Box
                sx={{
                    flexGrow: 1,
                    display: "flex",
                    flexDirection: "column",
                    height: 3,
                    bgcolor: "primary.main",
                }}
            />
            <CardContent
                sx={{
                    flexGrow: 1,
                    display: "flex",
                    flexDirection: "column",
                    gap: 0.5,
                    alignItems: "center",
                    justifyContent: "center",
                }}
            >
                <Typography
                    variant="h3"
                    component="p"
                    sx={{
                        fontWeight: 700,
                        lineHeight: 1.05,
                        letterSpacing: "-0.03em",
                        fontVariantNumeric: "tabular-nums",
                    }}
                >
                    {value}
                </Typography>
                <Typography variant="body2">{label}</Typography>
                {hint && (
                    <Typography variant="caption" color="text.secondary">
                        {hint}
                    </Typography>
                )}
            </CardContent>
        </Card>
    );
}

export default KpiCard;
