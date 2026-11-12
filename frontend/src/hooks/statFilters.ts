import type { StatsParams } from "../types/stats";

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

const asDate = (value: string | null): string | undefined =>
    value && ISO_DATE.test(value) ? value : undefined;

const asId = (value: string | null): number | undefined => {
    const id = Number(value);
    return Number.isInteger(id) && id > 0 ? id : undefined;
};

export function parseParams(search: URLSearchParams): StatsParams {
    const start = asDate(search.get("start"));
    const end = asDate(search.get("end"));
    const reversed = Boolean(start && end && start > end);
    return {
        start: reversed ? undefined : start,
        end: reversed ? undefined : end,
        station: asId(search.get("station")),
        dish: asId(search.get("dish")),
    };
}

export function toSearch(params: StatsParams): URLSearchParams {
    const search = new URLSearchParams();
    if (params.start) search.set("start", params.start);
    if (params.end) search.set("end", params.end);
    if (params.station) search.set("station", String(params.station));
    if (params.dish) search.set("dish", String(params.dish));
    return search;
}
