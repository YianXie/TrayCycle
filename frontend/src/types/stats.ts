/**
 * Shapes returned by GET /api/stats (waste/views.py StatsView).
 * Taken from the Django REST Framework serializers in waste/views.py.
 */

export type MetricRow = {
    bowl_count: number;
    average_waste_percent: number;
    total_waste_kg: number;
    average_waste_kg: number;
};

export type DailyRow = MetricRow & { date: string };

export type BucketValue = 0 | 25 | 50 | 75 | 100;

export type DishRow = MetricRow & {
    dish_id: number;
    dish_name: string;
    daily: DailyRow[];
    waste_bucket_distribution: Partial<Record<`${BucketValue}`, number>>;
};

export type Stats = MetricRow & {
    daily: DailyRow[];
    dishes: DishRow[];
};

export type StatsParams = {
    start?: string;
    end?: string;
    station?: number;
    dish?: number;
};
