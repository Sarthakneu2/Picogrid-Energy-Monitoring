
import {
  ResponsiveContainer,
  ComposedChart,
  BarChart,
  LineChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'

interface DailyData {
  reading_date: string
  pv_generation_kwh: number
  load_consumption_kwh: number
  grid_import_kwh: number
  grid_export_kwh: number
  average_soc_pct: number
  minimum_soc_pct: number
  maximum_soc_pct: number
  maximum_temperature_c: number
  cumulative_full_cycles: number
}

interface Props {
  data: DailyData[]
}

const tooltipStyle = {
  backgroundColor: '#151E2D',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '12px',
  color: '#fff',
}

export default function DailyAnalytics({ data }: Props) {
  const chartData = data.map((item) => ({
    ...item,
    day: item.reading_date.slice(8, 10),
  }))

  return (
    <div className="space-y-6">

      {/* Daily Solar Generation and Consumption */}
      <section className="bg-[#151E2D] border border-white/5 rounded-2xl p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold">
            Daily Solar Generation vs Consumption
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Daily energy performance · kWh
          </p>
        </div>

        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#ffffff12"
                vertical={false}
              />

              <XAxis
                dataKey="day"
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
              />

              <YAxis
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
              />

              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(label) => `January ${label}, 2025`}
              />

              <Legend />

              <Bar
                dataKey="pv_generation_kwh"
                name="Solar Generation"
                fill="#FBBF24"
                radius={[4, 4, 0, 0]}
              />

              <Line
                type="monotone"
                dataKey="load_consumption_kwh"
                name="Energy Consumption"
                stroke="#60A5FA"
                strokeWidth={2}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Daily Grid Exchange */}
      <section className="bg-[#151E2D] border border-white/5 rounded-2xl p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold">
            Daily Grid Import vs Export
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Daily electricity exchange · kWh
          </p>
        </div>

        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#ffffff12"
                vertical={false}
              />

              <XAxis
                dataKey="day"
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
              />

              <YAxis
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
              />

              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(label) => `January ${label}, 2025`}
              />

              <Legend />

              <Bar
                dataKey="grid_import_kwh"
                name="Grid Import"
                fill="#F97316"
                radius={[4, 4, 0, 0]}
              />

              <Bar
                dataKey="grid_export_kwh"
                name="Grid Export"
                fill="#34D399"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Daily Battery SOC */}
      <section className="bg-[#151E2D] border border-white/5 rounded-2xl p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold">
            Daily Battery Monitoring
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Average and minimum battery charge level · %
          </p>
        </div>

        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#ffffff12"
                vertical={false}
              />

              <XAxis
                dataKey="day"
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
              />

              <YAxis
                domain={[0, 100]}
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
                unit="%"
              />

              <Tooltip
                contentStyle={tooltipStyle}
                labelFormatter={(label) => `January ${label}, 2025`}
              />

              <Legend />

              <Line
                type="monotone"
                dataKey="average_soc_pct"
                name="Average SOC"
                stroke="#34D399"
                strokeWidth={3}
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="minimum_soc_pct"
                name="Minimum SOC"
                stroke="#F97316"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

    </div>
  )
}
