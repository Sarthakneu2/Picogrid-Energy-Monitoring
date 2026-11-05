
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from backend.app.database import get_connection


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)


# =========================================================
# 1. DAILY ANALYTICS
# =========================================================

@router.get("/daily")
def get_daily_analytics(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=365, ge=1, le=365)
):
    """Retrieve daily energy and battery performance analytics."""

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be later than end_date"
        )

    query = """
        SELECT *
        FROM daily_system_kpis
        WHERE (%s::date IS NULL OR reading_date >= %s::date)
          AND (%s::date IS NULL OR reading_date <= %s::date)
        ORDER BY reading_date ASC
        LIMIT %s;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        start_date,
                        start_date,
                        end_date,
                        end_date,
                        limit
                    )
                )
                records = cursor.fetchall()

        return {
            "status": "success",
            "count": len(records),
            "data": records
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve analytics: {type(error).__name__}"
        )


# =========================================================
# 2. ANNUAL SUMMARY
# =========================================================

@router.get("/summary")
def get_annual_summary(
    year: int = Query(default=2025, ge=2000, le=2100)
):
    """Retrieve annual PicoGrid system performance KPIs."""

    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)

    query = """
        SELECT
            COUNT(*) AS total_days,

            ROUND(SUM(pv_generation_kwh)::numeric, 2)
                AS total_pv_generation_kwh,

            ROUND(SUM(load_consumption_kwh)::numeric, 2)
                AS total_load_consumption_kwh,

            ROUND(SUM(grid_import_kwh)::numeric, 2)
                AS total_grid_import_kwh,

            ROUND(SUM(grid_export_kwh)::numeric, 2)
                AS total_grid_export_kwh,

            ROUND(AVG(average_soc_pct)::numeric, 2)
                AS average_battery_soc_pct,

            ROUND(MIN(minimum_soc_pct)::numeric, 2)
                AS minimum_battery_soc_pct,

            ROUND(MAX(maximum_soc_pct)::numeric, 2)
                AS maximum_battery_soc_pct,

            ROUND(MAX(maximum_temperature_c)::numeric, 2)
                AS maximum_battery_temperature_c,

            ROUND(MAX(cumulative_full_cycles)::numeric, 2)
                AS cumulative_full_cycles,

            ROUND(
                (
                    SUM(grid_import_kwh) /
                    NULLIF(SUM(load_consumption_kwh), 0) * 100
                )::numeric,
                2
            ) AS grid_dependency_pct,

            ROUND(
                (
                    SUM(grid_export_kwh) /
                    NULLIF(SUM(pv_generation_kwh), 0) * 100
                )::numeric,
                2
            ) AS solar_export_pct,

            ROUND(SUM(net_grid_energy_kwh)::numeric, 2)
                AS net_grid_energy_kwh

        FROM daily_system_kpis
        WHERE reading_date >= %s
          AND reading_date < %s;
    """

    metadata_query = """
        SELECT
            STRING_AGG(DISTINCT data_origin, ', ') AS data_origin,
            BOOL_AND(hardware_connected) AS hardware_connected
        FROM energy_readings
        WHERE recorded_at >= %s
          AND recorded_at < %s;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(query, (start_date, end_date))
                summary = cursor.fetchone()

                if not summary or summary["total_days"] == 0:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No analytics found for {year}"
                    )

                cursor.execute(
                    metadata_query,
                    (start_date, end_date)
                )
                metadata = cursor.fetchone()

        return {
            "status": "success",
            "year": year,
            "summary": summary,
            "data_provenance": metadata
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve annual summary: {type(error).__name__}"
        )


# =========================================================
# 3. MONTHLY ANALYTICS
# =========================================================

@router.get("/monthly")
def get_monthly_analytics(
    year: int = Query(default=2025, ge=2000, le=2100)
):
    """Retrieve monthly energy and battery analytics."""

    query = """
        SELECT
            e.month,
            e.pv_generation_kwh,
            e.load_consumption_kwh,
            e.grid_import_kwh,
            e.grid_export_kwh,
            e.average_pv_power_kw,
            e.peak_pv_power_kw,
            e.average_load_power_kw,
            e.peak_load_power_kw,
            e.total_readings,

            b.average_soc_pct,
            b.minimum_soc_pct,
            b.maximum_soc_pct,
            b.maximum_temperature_c,
            b.cumulative_full_cycles

        FROM monthly_energy_analytics e

        LEFT JOIN (
            SELECT
                DATE_TRUNC('month', recorded_at) AS month,
                ROUND(AVG(state_of_charge_pct)::numeric, 2)
                    AS average_soc_pct,
                ROUND(MIN(state_of_charge_pct)::numeric, 2)
                    AS minimum_soc_pct,
                ROUND(MAX(state_of_charge_pct)::numeric, 2)
                    AS maximum_soc_pct,
                ROUND(MAX(temperature_c)::numeric, 2)
                    AS maximum_temperature_c,
                ROUND(MAX(equivalent_full_cycles)::numeric, 2)
                    AS cumulative_full_cycles
            FROM battery_readings
            GROUP BY DATE_TRUNC('month', recorded_at)
        ) b ON e.month = b.month

        WHERE EXTRACT(YEAR FROM e.month) = %s
        ORDER BY e.month ASC;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (year,))
                records = cursor.fetchall()

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No monthly analytics found for {year}"
            )

        return {
            "status": "success",
            "year": year,
            "count": len(records),
            "data": records
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve monthly analytics: {type(error).__name__}"
        )
