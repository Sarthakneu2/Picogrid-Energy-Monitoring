
interface DailyData {
  reading_date: string
  pv_generation_kwh: number
  load_consumption_kwh: number
  grid_import_kwh: number
  grid_export_kwh: number
  average_soc_pct: number
  maximum_temperature_c: number
}

interface Props {
  data: DailyData[]
}

function DailyKPICards({ data }: Props) {
  const totalPV = data.reduce(
    (sum, day) => sum + day.pv_generation_kwh, 0
  )

  const totalLoad = data.reduce(
    (sum, day) => sum + day.load_consumption_kwh, 0
  )

  const totalGridImport = data.reduce(
    (sum, day) => sum + day.grid_import_kwh, 0
  )

  const totalGridExport = data.reduce(
    (sum, day) => sum + day.grid_export_kwh, 0
  )

  const averageSOC = data.length
    ? data.reduce((sum, day) => sum + day.average_soc_pct, 0) / data.length
    : 0

  const maximumTemperature = data.length
    ? Math.max(...data.map(day => day.maximum_temperature_c))
    : 0

  const cards = [
    {
      title: 'Solar Generation',
      value: totalPV.toFixed(2),
      unit: 'kWh',
      color: 'text-amber-400',
      description: 'Total PV energy generated',
    },
    {
      title: 'Energy Consumption',
      value: totalLoad.toFixed(2),
      unit: 'kWh',
      color: 'text-sky-400',
      description: 'Total energy consumed',
    },
    {
      title: 'Grid Import',
      value: totalGridImport.toFixed(2),
      unit: 'kWh',
      color: 'text-orange-400',
      description: 'Energy imported from grid',
    },
    {
      title: 'Grid Export',
      value: totalGridExport.toFixed(2),
      unit: 'kWh',
      color: 'text-emerald-400',
      description: 'Energy exported to grid',
    },
    {
      title: 'Average Battery SOC',
      value: averageSOC.toFixed(2),
      unit: '%',
      color: 'text-purple-400',
      description: 'Average state of charge',
    },
    {
      title: 'Maximum Battery Temperature',
      value: maximumTemperature.toFixed(2),
      unit: '°C',
      color: 'text-rose-400',
      description: 'Highest recorded modelled temperature',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5 mb-6">

      {cards.map((card) => (
        <div
          key={card.title}
          className="bg-[#151E2D] border border-white/5 rounded-2xl p-5"
        >
          <p className="text-sm text-slate-400">
            {card.title}
          </p>

          <div className="flex items-baseline gap-2 mt-3">
            <h3 className={`text-2xl font-bold ${card.color}`}>
              {card.value}
            </h3>

            <span className="text-sm text-slate-400">
              {card.unit}
            </span>
          </div>

          <p className="text-xs text-slate-500 mt-2">
            {card.description}
          </p>
        </div>
      ))}

    </div>
  )
}

export default DailyKPICards
