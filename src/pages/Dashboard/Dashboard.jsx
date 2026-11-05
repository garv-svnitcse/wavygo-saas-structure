import { useEffect, useState } from 'react'
import {
  ArrowUpRight,
  Bike,
  CalendarDays,
  Check,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  MapPin,
  MoreHorizontal,
  Plus,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useDemoData } from '../../data/DemoDataContext.jsx'
import { dashboardService } from '../../services/dashboardService.js'
import {
  BarChart,
  Button,
  Card,
  FilterSelect,
  MetricCard,
  PageHeader,
  StatusBadge,
} from '../../components/ui/Workspace.jsx'

function Dashboard() {
  const { bookings = [], vehicles = [], payments = [] } = useDemoData()
  const [dateRange, setDateRange] = useState('Last 30 days')
  const [backendStats, setBackendStats] = useState(null)

  useEffect(() => {
    let active = true
    async function loadStats() {
      try {
        const stats = await dashboardService.getStats(dateRange)
        if (active && stats) {
          setBackendStats(stats)
        }
      } catch (err) {
        console.warn('Dashboard backend sync notice:', err)
      }
    }
    loadStats()
    return () => {
      active = false
    }
  }, [dateRange, bookings.length, vehicles.length, payments.length])

  const rentedVehicles = vehicles.filter((v) => v.availability === 'Rented')
  const availableVehicles = vehicles.filter((v) => v.availability === 'Available')
  const activeBookings = bookings.filter((b) => b.status === 'Active')

  // Calculations with live backend prioritization
  const totalPaidRevenue =
    backendStats?.total_revenue ??
    (bookings.reduce((sum, b) => sum + (Number(b.paid) || 0), 0) ||
      payments.reduce((sum, p) => sum + (Number(p.amount) || 0), 0))

  const pendingPayments =
    backendStats?.pending_payments ??
    bookings.reduce((sum, b) => sum + (Number(b.pending) || 0), 0)

  const fleetUtilization =
    backendStats?.fleet_utilization ??
    (vehicles.length > 0 ? Math.round((rentedVehicles.length / vehicles.length) * 100) : 0)

  const totalVehiclesCount = backendStats?.total_vehicles ?? vehicles.length
  const availableVehiclesCount = backendStats?.available_vehicles ?? availableVehicles.length
  const activeBookingsCount = backendStats?.active_bookings ?? activeBookings.length

  const todayDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).toUpperCase()

  // Trend data computed from backend or fallback monthly bins
  const revenueTrend =
    backendStats?.revenue_trend || [
      { label: 'May', value: Math.round(totalPaidRevenue * 0.1) },
      { label: 'Jun', value: Math.round(totalPaidRevenue * 0.15) },
      { label: 'Jul', value: Math.round(totalPaidRevenue * 0.18) },
      { label: 'Aug', value: Math.round(totalPaidRevenue * 0.22) },
      { label: 'Sep', value: Math.round(totalPaidRevenue * 0.25) },
      { label: 'Oct', value: totalPaidRevenue || 0 },
    ]

  const recentBookingsList = backendStats?.recent_bookings || bookings.slice(0, 4)
  const rentedDisplayList =
    backendStats?.rented_vehicles_list?.length > 0
      ? backendStats.rented_vehicles_list
      : (rentedVehicles.length > 0 ? rentedVehicles : vehicles.slice(0, 2))

  return (
    <div>
      <PageHeader
        eyebrow={todayDate}
        title="Good day, Partner"
        description="Here is what is happening across your rental fleet and bookings today."
        action={
          <div className="flex flex-wrap gap-2">
            <FilterSelect
              value={dateRange}
              onChange={setDateRange}
              options={['Last 7 days', 'Last 30 days', 'This month', 'Last 90 days']}
            />
            <Link to="/app/bookings/new">
              <Button>
                <Plus size={16} aria-hidden="true" />
                New booking
              </Button>
            </Link>
          </div>
        }
      />

      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4 sm:gap-4">
        <MetricCard
          label="Total vehicles"
          value={totalVehiclesCount}
          caption="Total fleet size"
          icon={Bike}
          tone="navy"
        />
        <MetricCard
          label="Available vehicles"
          value={availableVehiclesCount}
          caption="Ready for customer booking"
          icon={Check}
          tone="green"
        />
        <MetricCard
          label="Active bookings"
          value={activeBookingsCount}
          caption="Vehicles on the road"
          icon={CalendarDays}
          tone="blue"
        />
        <MetricCard
          label="Total revenue"
          value={`₹${totalPaidRevenue.toLocaleString('en-IN')}`}
          caption="Total collections"
          icon={CircleDollarSign}
          tone="violet"
        />
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1.65fr)_minmax(300px,0.9fr)]">
        <Card className="min-w-0 p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Revenue overview</h2>
              <p className="mt-1 text-xs text-slate-500">Booking revenue · {dateRange}</p>
            </div>
            <button
              type="button"
              aria-label="More revenue options"
              className="grid size-8 place-items-center rounded-lg text-slate-400 hover:bg-slate-100"
            >
              <MoreHorizontal size={18} aria-hidden="true" />
            </button>
          </div>
          <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-[30px] font-semibold tracking-tight text-slate-900">
                ₹{totalPaidRevenue.toLocaleString('en-IN')}
              </p>
              <p className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-emerald-700">
                <ArrowUpRight size={14} aria-hidden="true" />
                Live synced <span className="font-normal text-slate-400">with payments</span>
              </p>
            </div>
            <div className="rounded-xl bg-amber-50 px-3.5 py-2.5">
              <p className="text-[10px] font-medium uppercase tracking-wide text-amber-700">
                Pending payments
              </p>
              <p className="mt-1 text-lg font-semibold text-slate-900">
                ₹{pendingPayments.toLocaleString('en-IN')}
              </p>
            </div>
          </div>
          <div className="mt-3">
            <BarChart data={revenueTrend} label="Monthly booking revenue trend" />
          </div>
        </Card>

        <Card className="p-5 sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Recent bookings</h2>
              <p className="mt-1 text-xs text-slate-500">Latest customer handovers</p>
            </div>
            <Link
              to="/app/bookings"
              className="inline-flex items-center gap-1 text-xs font-medium text-emerald-800 hover:text-emerald-950"
            >
              See all <ChevronRight size={14} aria-hidden="true" />
            </Link>
          </div>
          <div className="mt-4 divide-y divide-slate-100">
            {recentBookingsList.map((booking, index) => (
              <div key={booking.id} className="flex items-center gap-3 py-3.5 first:pt-0 last:pb-0">
                <div
                  className={`grid size-10 shrink-0 place-items-center rounded-xl text-lg ${
                    index % 2 ? 'bg-emerald-50' : 'bg-slate-100'
                  }`}
                >
                  {index % 2 ? '🏍️' : '🛵'}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-semibold text-slate-800">{booking.customer}</p>
                  <p className="mt-1 truncate text-[11px] text-slate-400">{booking.vehicle}</p>
                </div>
                <div className="text-right">
                  <StatusBadge status={booking.status} />
                  <p className="mt-1 text-[10px] text-slate-400">{booking.dates}</p>
                </div>
              </div>
            ))}
            {recentBookingsList.length === 0 && (
              <div className="py-10 text-center">
                <p className="text-xs font-medium text-slate-600">No bookings recorded yet</p>
                <p className="mt-1 text-[11px] text-slate-400">
                  Create your first rental booking with the button above.
                </p>
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <Card className="p-5 sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Currently rented</h2>
              <p className="mt-1 text-xs text-slate-500">Vehicles out on a booking</p>
            </div>
            <Link
              to="/app/vehicles"
              className="inline-flex items-center gap-1 text-xs font-medium text-emerald-800"
            >
              Fleet <ChevronRight size={14} aria-hidden="true" />
            </Link>
          </div>
          <div className="mt-4 grid gap-2.5 sm:grid-cols-2">
            {rentedDisplayList.map((vehicle) => (
              <div
                key={vehicle.id}
                className="flex items-center gap-3 rounded-xl border border-slate-100 p-3"
              >
                <span className="grid size-10 place-items-center rounded-xl bg-emerald-50 text-xl">
                  {vehicle.image || '🛵'}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-semibold text-slate-800">{vehicle.name}</p>
                  <p className="mt-1 text-[11px] text-slate-400">{vehicle.registration}</p>
                </div>
                <StatusBadge status={vehicle.availability} />
              </div>
            ))}
            {rentedDisplayList.length === 0 && (
              <p className="col-span-2 py-6 text-center text-xs text-slate-400">
                No vehicles registered in fleet yet.
              </p>
            )}
          </div>
        </Card>

        <Card className="p-5 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Quick overview</h2>
              <p className="mt-1 text-xs text-slate-500">Fleet activity at a glance</p>
            </div>
            <span className="grid size-9 place-items-center rounded-xl bg-emerald-50 text-emerald-700">
              <CircleDollarSign size={17} aria-hidden="true" />
            </span>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-50 p-3.5">
              <p className="text-[11px] text-slate-500">Total Bookings</p>
              <p className="mt-1.5 text-xl font-semibold text-slate-900">{bookings.length}</p>
              <p className="mt-1 text-[10px] text-emerald-700">Live records</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3.5">
              <p className="text-[11px] text-slate-500">Fleet utilization</p>
              <p className="mt-1.5 text-xl font-semibold text-slate-900">{fleetUtilization}%</p>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200">
                <div
                  className="h-full rounded-full bg-emerald-600 transition-all"
                  style={{ width: `${Math.min(fleetUtilization, 100)}%` }}
                />
              </div>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-2 rounded-xl border border-slate-100 px-3 py-2.5 text-xs text-slate-500">
            <MapPin size={14} aria-hidden="true" className="text-emerald-700" />
            Fleet Operations Hub <span className="ml-auto text-[10px] text-emerald-600 font-medium">Online</span>
            <Clock3 size={13} aria-hidden="true" />
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
