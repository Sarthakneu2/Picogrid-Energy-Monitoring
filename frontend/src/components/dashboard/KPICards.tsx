
import {
  Sun,
  Activity,
  Download,
  Upload,
  TrendingUp,
} from 'lucide-react'

interface Summary {
  total_pv_generation_kwh: number
  total_load_consumption_kwh: number
  total_grid_import_kwh: number
  total_grid_export_kwh: number
}

interface KPICardsProps {
  summary: Summary
}

export default function KPICards({ summary }: KPICardsProps) {
  const cards = [
    {
      title: 'Solar Generation',
      value: summary.total_pv_generation_kwh,
      unit: 'kWh',
      icon: Sun,
      color: 'text-amber-400',
      background: 'bg-amber-500/10',
    },
    {
      title: 'Energy Consumption',
      value: summary.total_load_consumption_kwh,
      unit: 'kWh',
      icon: Activity,
      color: 'text-blue-400',
      background: 'bg-blue-500/10',
    },
    {
      title: 'Grid Import',
      value: summary.total_grid_import_kwh,
      unit: 'kWh',
      icon: Download,
      color: 'text-orange-400',
      background: 'bg-orange-500/10',
    },
    {
      title: 'Grid Export',
      value: summary.total_grid_export_kwh,
      unit: 'kWh',
      icon: Upload,
      color: 'text-emerald-400',
      background: 'bg-emerald-500/10',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
      {cards.map((card) => {
        const Icon = card.icon

        return (
          <div
            key={card.title}
            className="bg-[#151E2D] border border-white/5 rounded-2xl p-5 hover:border-white/15 transition"
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-slate-400">
                  {card.title}
                </p>

                <h2 className="text-2xl font-bold mt-3 text-white">
                  {card.value.toLocaleString('en-US', {
                    maximumFractionDigits: 2,
                  })}
                  <span className="text-sm text-slate-400 ml-2">
                    {card.unit}
                  </span>
                </h2>
              </div>

              <div className={`p-3 rounded-xl ${card.background}`}>
                <Icon className={card.color} size={22} />
              </div>
            </div>

            <div className="flex items-center gap-2 mt-5 text-xs text-slate-500">
              <TrendingUp size={14} />
              Annual overview · 2025
            </div>
          </div>
        )
      })}
    </div>
  )
}
