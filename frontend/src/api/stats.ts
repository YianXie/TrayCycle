import api from "../api/client";
import { MOCK_DATA } from "../mocks/data";
import type { DailyRow, DishRow, Stats, StatsParams } from "../types/stats";

const round3 = (n: number) => Math.round(n * 1000) / 1000;

const totals = (rows: DailyRow[]) => {
    const bowls = rows.reduce((sum, row) => sum + row.bowl_count, 0);
    const kg = rows.reduce((sum, row) => sum + row.total_waste_kg, 0);
    const pct = rows.reduce(
        (sum, row) => sum + row.average_waste_percent * row.bowl_count,
        0
    );
    return {
        bowl_count: bowls,
        total_waste_kg: round3(kg),
        average_waste_kg: bowls ? round3(kg / bowls) : 0,
        average_waste_percent: bowls ? round3(pct / bowls) : 0,
    };
};

const inRange = (params: StatsParams) => (row: DailyRow) =>
    (!params.start || row.date >= params.start) &&
    (!params.end || row.date <= params.end);

function filterMock(base: Stats, params: StatsParams): Stats {
    const keep = inRange(params);
    const scoped = params.dish
        ? base.dishes.filter((dish) => dish.dish_id === params.dish)
        : base.dishes;

    const dishes = scoped
        .map((dish) => {
            const daily = dish.daily.filter(keep);
            return { ...dish, daily, ...totals(daily) };
        })
        .filter((dish) => dish.bowl_count > 0);

    const daily = params.dish
        ? scoped.flatMap((dish) => dish.daily).filter(keep)
        : base.daily.filter(keep);

    return { ...base, daily, ...totals(daily), dishes };
}

export async function getStats(
    params: StatsParams,
    signal?: AbortSignal
): Promise<Stats> {
    const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

    if (USE_MOCK) return filterMock(MOCK_DATA, params);

    const { data } = await api.get<Stats>("/api/wastes/stats", {
        params,
        signal,
    });
    return data;
}
