
import { useEffect, useState } from 'react'
import {
  CalendarDays,
  Download,
  RefreshCw,
  AlertCircle,
  Activity,
} from 'lucide-react'

import Sidebar from './components/layout/Sidebar'
import KPICards from './components/dashboard/KPICards'
import MonthlyAnalytics from './components/dashboard/MonthlyAnalytics'
import DailyAnalytics from './components/dashboard/DailyAnalytics'
import DailyKPICards from './components/dashboard/DailyKPICards'
import api from './services/api'

// ---------------------------------------------
// TYPES
// ---------------------------------------------

interface Summary {
  total_days: number
  total_pv_generation_kwh: number
  total_load_consumption_kwh: number
  total_grid_import_kwh: number
  total_grid_export_kwh: number
  average_battery_soc_pct: number
  minimum_battery_soc_pct: number
  maximum_battery_soc_pct: number
  maximum_battery_temperature_c: number
  cumulative_full_cycles: number
  grid_dependency_pct: number
  solar_export_pct: number
  net_grid_energy_kwh: number
}

interface SummaryResponse {
  status: string
  year: number
  summary: Summary
  data_provenance: {
    data_origin: string
    hardware_connected: boolean
  }
}

interface MonthlyData {
  month: string
  pv_generation_kwh: number
  load_consumption_kwh: number
  grid_import_kwh: number
  grid_export_kwh: number
  average_pv_power_kw: number
  peak_pv_power_kw: number
  average_load_power_kw: number
  peak_load_power_kw: number
  average_soc_pct: number
  minimum_soc_pct: number
  maximum_soc_pct: number
  maximum_temperature_c: number
  cumulative_full_cycles: number
}

interface MonthlyResponse {
  status: string
  year: number
  count: number
  data: MonthlyData[]
}

interface DailyData {
  reading_date: string
  pv_generation_kwh: number
  load_consumption_kwh: number
  grid_import_kwh: number
  grid_export_kwh: number
  peak_pv_power_kw: number
  peak_load_power_kw: number
  average_soc_pct: number
  minimum_soc_pct: number
  maximum_soc_pct: number
  maximum_temperature_c: number
  cumulative_full_cycles: number
  grid_dependency_pct: number
  solar_export_pct: number
  net_grid_energy_kwh: number
  total_readings: number
}

interface DailyResponse {
  status: string
  count: number
  data: DailyData[]
}

// ---------------------------------------------
// MAIN APPLICATION
// ---------------------------------------------

function App() {

  // Dashboard data
  const [summary, setSummary] = useState<Summary | null>(null)
  const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([])
  const [dailyData, setDailyData] = useState<DailyData[]>([])

  // Date filters
  const [startDate, setStartDate] = useState('2025-01-01')
  const [endDate, setEndDate] = useState('2025-01-31')

  // Loading states
  const [loading, setLoading] = useState(true)
  const [dailyLoading, setDailyLoading] = useState(false)

  // Error states
  const [error, setError] = useState('')
  const [dailyError, setDailyError] = useState('')

  // Refresh trigger
  const [refreshKey, setRefreshKey] = useState(0)

  // ---------------------------------------------
  // FETCH ANNUAL SUMMARY AND MONTHLY ANALYTICS
  // ---------------------------------------------

  useEffect(() => {
    let cancelled = false

    async function fetchDashboardData() {
      try {
        setLoading(true)
        setError('')

        const [summaryResponse, monthlyResponse] = await Promise.all([
          api.get<SummaryResponse>(
            '/api/v1/analytics/summary',
            { params: { year: 2025 } }
          ),

          api.get<MonthlyResponse>(
            '/api/v1/analytics/monthly',
            { params: { year: 2025 } }
          ),
        ])

        if (cancelled) return

        setSummary(summaryResponse.data.summary)
        setMonthlyData(monthlyResponse.data.data)

      } catch (err) {
        if (cancelled) return

        console.error('Dashboard data error:', err)
        setError(
          'Unable to load dashboard data. Please check that the backend and database are running.'
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDashboardData()

    return () => {
      cancelled = true
    }
  }, [refreshKey])

  // ---------------------------------------------
  // FETCH DAILY ANALYTICS
  // ---------------------------------------------

  useEffect(() => {
    let cancelled = false

    async function fetchDailyData() {
      if (!startDate || !endDate) return

      if (startDate > endDate) {
        setDailyError('Start date cannot be later than end date.')
        setDailyData([])
        return
      }

      setDailyLoading(true)
      setDailyError('')

      try {
        const response = await api.get<DailyResponse>(
          '/api/v1/analytics/daily',
          {
            params: {
              start_date: startDate,
              end_date: endDate,
              limit: 365,
            },
          }
        )

        if (cancelled) return

        setDailyData(response.data.data ?? [])

      } catch (err) {
        if (cancelled) return

        console.error('Daily analytics error:', err)
        setDailyError(
          'Unable to load daily analytics. Please check the selected dates and API connection.'
        )
        setDailyData([])
      } finally {
        if (!cancelled) {
          setDailyLoading(false)
        }
      }
    }

    fetchDailyData()

    return () => {
      cancelled = true
    }
  }, [startDate, endDate, refreshKey])

  // ---------------------------------------------
  // DATE FILTER HANDLERS
  // ---------------------------------------------

  const resetDateFilter = () => {
    setStartDate('2025-01-01')
    setEndDate('2025-01-31')
  }

  // ---------------------------------------------
  // CSV EXPORT
  // ---------------------------------------------

  const exportDailyCSV = () => {
    if (dailyData.length === 0) {
      return
    }

    const columns: (keyof DailyData)[] = [
      'reading_date',
      'pv_generation_kwh',
      'load_consumption_kwh',
      'grid_import_kwh',
      'grid_export_kwh',
      'peak_pv_power_kw',
      'peak_load_power_kw',
      'average_soc_pct',
      'minimum_soc_pct',
      'maximum_soc_pct',
      'maximum_temperature_c',
      'cumulative_full_cycles',
      'grid_dependency_pct',
      'solar_export_pct',
      'net_grid_energy_kwh',
      'total_readings',
    ]

    const csvRows = [
      columns.join(','),

      ...dailyData.map((day) =>
        columns.map((column) => {
          const value = day[column]
          return value === null || value === undefined
            ? ''
            : String(value)
        }).join(',')
      ),
    ]

    const csvContent = '\uFEFF' + csvRows.join('\n')
    const blob = new Blob([csvContent], {
      type: 'text/csv;charset=utf-8;',
    })

    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.download = `picogrid_daily_analytics_${startDate}_to_${endDate}.csv`

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(url)
  }

  // ---------------------------------------------
  // REFRESH DASHBOARD
  // ---------------------------------------------

  const refreshDashboard = () => {
    setRefreshKey((previous) => previous + 1)
  }

  // ---------------------------------------------
  // LOADING SCREEN
  // ---------------------------------------------

  if (loading) {
    return (
      <div className="min-h-screen bg-[#090e17] flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-10 h-10 text-emerald-400 animate-pulse mx-auto mb-4" />

          <h2 className="text-xl font-semibold text-white">
            Loading PicoGrid
          </h2>

          <p className="text-slate-400 text-sm mt-2">
            Preparing your energy analytics dashboard...
          </p>
        </div>
      </div>
    )
  }

  // ---------------------------------------------
  // MAIN DASHBOARD UI
  // ---------------------------------------------

  return (
    <div className="min-h-screen bg-[#090e17] text-white">

      <div className="flex min-h-screen">

        {/* SIDEBAR */}

        <Sidebar />

        {/* MAIN CONTENT */}

        <main className="flex-1 min-w-0 p-5 md:p-8">

          <div className="max-w-[1600px] mx-auto">

            {/* HEADER */}

            <header className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5 mb-8">

              <div>
                <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium mb-2">
                  <Activity size={16} />
                  ENERGY MANAGEMENT PLATFORM
                </div>

                <h1 className="text-3xl font-bold text-white">
                  Energy Dashboard
                </h1>

                <p className="text-slate-400 mt-2">
                  Monitor, analyse and understand your energy system.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">

                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#151e2d] border border-white/10">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />

                  <span className="text-xs text-slate-300">
                    Simulation Mode — Hardware Not Connected
                  </span>
                </div>

                <button
                  onClick={refreshDashboard}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition"
                >
                  <RefreshCw size={16} />
                  Refresh
                </button>

              </div>
            </header>

            {/* GENERAL ERROR */}

            {error && (
              <div className="mb-6 p-4 rounded-xl border border-red-500/30 bg-red-500/10 flex items-start gap-3">
                <AlertCircle className="text-red-400 shrink-0" size={20} />

                <p className="text-sm text-red-300">
                  {error}
                </p>
              </div>
            )}

            {/* ANNUAL OVERVIEW */}

            {summary && (
              <section className="mb-10">

                <div className="flex items-center justify-between mb-5">
                  <div>
                    <h2 className="text-xl font-semibold">
                      Annual Energy Overview
                    </h2>

                    <p className="text-sm text-slate-400 mt-1">
                      System performance for January–December 2025
                    </p>
                  </div>

                  <span className="text-sm text-slate-400 bg-[#151e2d] px-3 py-1.5 rounded-lg">
                    2025
                  </span>
                </div>

                <KPICards summary={summary} />

                {/* ADDITIONAL SYSTEM METRICS */}

                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mt-5">

                  <div className="bg-[#151e2d] border border-white/5 rounded-xl p-5">
                    <p className="text-sm text-slate-400">
                      Average Battery SOC
                    </p>

                    <h3 className="text-2xl font-bold text-purple-400 mt-2">
                      {summary.average_battery_soc_pct.toFixed(2)}%
                    </h3>
                  </div>

                  <div className="bg-[#151e2d] border border-white/5 rounded-xl p-5">
                    <p className="text-sm text-slate-400">
                      Grid Dependency
                    </p>

                    <h3 className="text-2xl font-bold text-orange-400 mt-2">
                      {summary.grid_dependency_pct.toFixed(2)}%
                    </h3>
                  </div>

                  <div className="bg-[#151e2d] border border-white/5 rounded-xl p-5">
                    <p className="text-sm text-slate-400">
                      Solar Export Ratio
                    </p>

                    <h3 className="text-2xl font-bold text-emerald-400 mt-2">
                      {summary.solar_export_pct.toFixed(2)}%
                    </h3>
                  </div>

                  <div className="bg-[#151e2d] border border-white/5 rounded-xl p-5">
                    <p className="text-sm text-slate-400">
                      Equivalent Full Cycles
                    </p>

                    <h3 className="text-2xl font-bold text-sky-400 mt-2">
                      {summary.cumulative_full_cycles.toFixed(2)}
                    </h3>
                  </div>

                </div>

              </section>
            )}

            {/* MONTHLY ANALYTICS */}

            <section className="mb-12">

              <div className="mb-5">
                <h2 className="text-xl font-semibold">
                  Monthly Analytics
                </h2>

                <p className="text-sm text-slate-400 mt-1">
                  Monthly solar generation, energy consumption, grid exchange and battery performance.
                </p>
              </div>

              {monthlyData.length > 0 ? (
                <MonthlyAnalytics data={monthlyData} />
              ) : (
                <div className="bg-[#151e2d] rounded-xl p-8 text-center text-slate-400">
                  No monthly analytics available.
                </div>
              )}

            </section>

            {/* DAILY ANALYTICS */}

            <section className="mb-10">

              <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-5 mb-6">

                <div>
                  <h2 className="text-xl font-semibold">
                    Daily Analytics
                  </h2>

                  <p className="text-sm text-slate-400 mt-1">
                    Explore daily energy performance over a selected period.
                  </p>
                </div>

                {/* DATE FILTERS */}

                <div className="flex flex-wrap items-end gap-3">

                  <div>
                    <label className="block text-xs text-slate-400 mb-2">
                      Start Date
                    </label>

                    <div className="flex items-center gap-2 bg-[#151e2d] border border-white/10 rounded-xl px-3 py-2">
                      <CalendarDays size={16} className="text-slate-400" />

                      <input
                        type="date"
                        value={startDate}
                        min="2025-01-01"
                        max="2025-12-31"
                        onChange={(event) => setStartDate(event.target.value)}
                        className="bg-transparent text-white text-sm outline-none [color-scheme:dark]"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs text-slate-400 mb-2">
                      End Date
                    </label>

                    <div className="flex items-center gap-2 bg-[#151e2d] border border-white/10 rounded-xl px-3 py-2">
                      <CalendarDays size={16} className="text-slate-400" />

                      <input
                        type="date"
                        value={endDate}
                        min="2025-01-01"
                        max="2025-12-31"
                        onChange={(event) => setEndDate(event.target.value)}
                        className="bg-transparent text-white text-sm outline-none [color-scheme:dark]"
                      />
                    </div>
                  </div>

                  <button
                    onClick={resetDateFilter}
                    className="px-4 py-2.5 rounded-xl bg-[#253247] hover:bg-[#33445e] text-sm text-white transition"
                  >
                    Reset
                  </button>

                  <button
                    onClick={exportDailyCSV}
                    disabled={dailyData.length === 0 || dailyLoading}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium text-white transition"
                  >
                    <Download size={16} />
                    Export CSV
                  </button>

                </div>

              </div>

              {/* DAILY ERROR */}

              {dailyError && (
                <div className="mb-5 p-4 rounded-xl border border-red-500/30 bg-red-500/10 flex items-center gap-3">
                  <AlertCircle className="text-red-400 shrink-0" size={20} />

                  <p className="text-sm text-red-300">
                    {dailyError}
                  </p>
                </div>
              )}

              {/* DAILY LOADING */}

              {dailyLoading ? (

                <div className="bg-[#151e2d] rounded-xl p-12 text-center">
                  <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin mx-auto mb-3" />

                  <p className="text-slate-300">
                    Loading daily analytics...
                  </p>
                </div>

              ) : dailyData.length > 0 ? (

                <>

                  {/* DAILY KPI CARDS */}

                  <div className="mb-6">
                    <DailyKPICards data={dailyData} />
                  </div>

                  {/* DAILY CHARTS */}

                  <DailyAnalytics data={dailyData} />

                  {/* DATA INFORMATION */}

                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mt-5 text-xs text-slate-500">

                    <p>
                      Showing {dailyData.length} daily records
                    </p>

                    <p>
                      Data source: Modelled test telemetry · 5-minute intervals
                    </p>

                  </div>

                </>

              ) : !dailyError ? (

                <div className="bg-[#151e2d] border border-white/5 rounded-xl p-10 text-center">

                  <CalendarDays className="w-9 h-9 text-slate-500 mx-auto mb-3" />

                  <h3 className="text-white font-medium">
                    No daily records found
                  </h3>

                  <p className="text-sm text-slate-400 mt-2">
                    Select a different date range to view energy analytics.
                  </p>

                </div>

              ) : null}

            </section>

            {/* FOOTER */}

            <footer className="border-t border-white/10 pt-5 pb-3 flex flex-col sm:flex-row justify-between gap-2 text-xs text-slate-500">

              <p>
                PicoGrid · IoT Energy Monitoring and Analytics Platform
              </p>

              <p>
                Dhulikhel, Kavrepalanchok, Nepal · Pilot Year 2025
              </p>

            </footer>

          </div>

        </main>

      </div>

    </div>
  )
}

export default App
