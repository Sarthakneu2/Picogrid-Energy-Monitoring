
import {
  LayoutDashboard,
  Sun,
  BatteryCharging,
  Activity,
  BarChart3,
  Settings,
  Zap,
  Leaf,
} from 'lucide-react'

const navigation = [
  { name: 'Overview', icon: LayoutDashboard },
  { name: 'Solar Generation', icon: Sun },
  { name: 'Battery Monitoring', icon: BatteryCharging },
  { name: 'Energy Consumption', icon: Activity },
  { name: 'Analytics & Reports', icon: BarChart3 },
]

export default function Sidebar() {
  return (
    <aside className="w-64 min-h-screen bg-[#0D1522] border-r border-white/10 p-5 flex flex-col">
      <div className="flex items-center gap-3 mb-10">
        <div className="bg-amber-500 p-2 rounded-xl">
          <Zap size={22} className="text-black" />
        </div>

        <div>
          <h1 className="text-xl font-bold tracking-wide">
            PicoGrid
          </h1>
          <p className="text-xs text-slate-400">
            Energy Intelligence
          </p>
        </div>
      </div>

      <p className="text-xs uppercase tracking-widest text-slate-500 mb-4">
        Main Menu
      </p>

      <nav className="space-y-2">
        {navigation.map((item, index) => {
          const Icon = item.icon

          return (
            <button
              key={item.name}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition ${
                index === 0
                  ? 'bg-amber-500/15 text-amber-400'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <Icon size={19} />
              {item.name}
            </button>
          )
        })}
      </nav>

      <div className="mt-auto border-t border-white/10 pt-5">
        <button className="flex items-center gap-3 text-slate-400 hover:text-white text-sm">
          <Settings size={19} />
          Settings
        </button>

        <div className="mt-6 rounded-xl bg-emerald-500/10 p-4">
          <Leaf size={20} className="text-emerald-400 mb-2" />
          <p className="text-sm font-semibold text-emerald-400">
            Clean Energy
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Monitor your energy ecosystem.
          </p>
        </div>
      </div>
    </aside>
  )
}
