
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

interface MonthlyData {
  month: string
  pv_generation_kwh: number
  load_consumption_kwh: number
  grid_import_kwh: number
  grid_export_kwh: number
  average_soc_pct: number
  minimum_soc_pct: number
  maximum_soc_pct: number
  cumulative_full_cycles: number
}

interface Props {
  data: MonthlyData[]
}

const formatMonth = (date: string) =>
  new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    timeZone: 'UTC',
  })

const tooltipStyle = {
  backgroundColor: '#151E2D',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '12px',
  color: '#fff',
}

export default function MonthlyAnalytics({ data }: Props) {
  const chartData = data.map((item) => ({
    ...item,
    monthLabel: formatMonth(item.month),
  }))

  return (
    <div className="space-y-6">

      {/* Solar Generation vs Consumption */}
      <section className="bg-[#151E2D] border border-white/5 rounded-2xl p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold">
            Solar Generation vs Consumption
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Monthly energy performance · kWh
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
                dataKey="monthLabel"
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
              />

              <Tooltip contentStyle={tooltipStyle} />
              <Legend />

              <Bar
                dataKey="pv_generation_kwh"
                name="Solar Generation"
                fill="#FBBF24"
                radius={[5, 5, 0, 0]}
              />

              <Line
                type="monotone"
                dataKey="load_consumption_kwh"
                name="Energy Consumption"
                stroke="#60A5FA"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Grid Import vs Export */}
      <section className="bg-[#151E2D] border border-white/5 rounded-2xl p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold">
            Grid Import vs Export
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Monthly electricity exchange with the grid · kWh
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
                dataKey="monthLabel"
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
              />

              <Tooltip contentStyle={tooltipStyle} />
              <Legend />

              <Bar
                dataKey="grid_import_kwh"
                name="Grid Import"
                fill="#F97316"
                radius={[5, 5, 0, 0]}
              />

              <Bar
                dataKey="grid_export_kwh"
                name="Grid Export"
                fill="#34D399"
                radius={[5, 5, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Battery SOC */}
      <section className="bg-[#151E2D] border border-white/5 rounded-2xl p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold">
            Battery State of Charge
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Monthly average battery charge level · %
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
                dataKey="monthLabel"
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                domain={[0, 100]}
                stroke="#94A3B8"
                tickLine={false}
                axisLine={false}
                unit="%"
              />

              <Tooltip contentStyle={tooltipStyle} />
              <Legend />

              <Line
                type="monotone"
                dataKey="average_soc_pct"
                name="Average Battery SOC"
                stroke="#34D399"
                strokeWidth={3}
                dot={{ r: 4 }}
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
