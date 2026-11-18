/**
 * KPI Card component for the TriCycle web application.
 *
 * Displays a card with a key performance indicator (KPI) value, label, optional hint, and optional action.
 * The card has a colored top border and changes appearance on hover.
 */
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import React from "react";

export type KpiCardProps = {
    value: string;
    label: string;
    hint?: string;
    action?: React.ReactNode;
};

function KpiCard({ value, label, hint, action }: KpiCardProps) {
    return (
        <Card
            variant="outlined"
            sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                borderColor: "divider",
                // "&:hover": {
                //     borderColor: "primary.main",
                //     boxShadow: 1,
                // },
            }}
        >
            <Box sx={{ height: 3, flexShrink: 0, bgcolor: "primary.main" }} />
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
                        fontSize: { xs: "1.75rem", md: "2.5rem" },
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
                {action}
            </CardContent>
        </Card>
    );
}

export default KpiCard;
