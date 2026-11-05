import { createContext, useContext, useEffect, useState } from 'react'
import { authService } from '../services/authService.js'
import { bookingService } from '../services/bookingService.js'
import { customerService } from '../services/customerService.js'
import { documentService } from '../services/documentService.js'
import { maintenanceService } from '../services/maintenanceService.js'
import { paymentService } from '../services/paymentService.js'
import { financeService } from '../services/financeService.js'
import { vehicleService } from '../services/vehicleService.js'
import { notificationService } from '../services/notificationService.js'

const DemoDataContext = createContext(null)

const seed = {
  vehicles: [],
  customers: [],
  bookings: [],
  payments: [],
  documents: [],
  maintenance: [],
  staff: [],
  expenses: [],
  notifications: [],
  financeOverview: null,
}

export function DemoDataProvider({ children }) {
  const [data, setData] = useState(seed)

  async function syncVehicles() {
    try {
      const res = await vehicleService.listVehicles({ limit: 100 })
      const backendVehicles = Array.isArray(res) ? res : res?.items || []
      const mapped = backendVehicles.map((v) => {
        const firstPhotoUrl = Array.isArray(v.photos) && v.photos.length > 0
          ? (typeof v.photos[0] === 'string' ? v.photos[0] : v.photos[0]?.url)
          : null

        return {
          id: v.id || v._id,
          name: v.makeModel || v.name,
          makeModel: v.makeModel || v.name,
          trim: v.trim || '',
          registration: v.registration || v.registrationNumber || '',
          type: v.type || 'Motorcycle',
          fuel: v.fuel || 'Petrol',
          year: Number(v.year) || 2024,
          color: v.color || '',
          engineCapacity: v.engineCapacity ? Number(v.engineCapacity) : null,
          rcStatus: v.rcStatus || 'Verified',
          seats: Number(v.seats) || 2,
          showOnWavygo: Boolean(v.showOnWavygo ?? (v.status === 'Online')),
          show_on_wavygo: Boolean(v.showOnWavygo ?? (v.status === 'Online')),
          status: Boolean(v.showOnWavygo ?? (v.status === 'Online')) ? 'Online' : 'Offline',
          availability: v.fleetAvailability || v.availability || 'Available',
          fleetAvailability: v.fleetAvailability || v.availability || 'Available',
          price: Number(v.dailyRate || v.price || 0),
          dailyRate: Number(v.dailyRate || v.price || 0),
          image: firstPhotoUrl || (v.type === 'Electric' ? '⚡' : v.type === 'Scooter' ? '🛵' : '🏍️'),
          photos: v.photos || [],
          documents: v.documents || [],
          backendSynced: true,
        }
      })
      setData((current) => ({
        ...current,
        vehicles: mapped,
      }))
    } catch (err) {
      console.warn('syncVehicles error:', err)
    }
  }

  async function syncCustomers() {
    try {
      const res = await customerService.listCustomers({ limit: 100 })
      const backendCustomers = Array.isArray(res) ? res : res?.customers || res?.items || []
      const mapped = backendCustomers.map((c) => ({
        id: c.id || c._id,
        name: c.name,
        phone: c.phone,
        email: c.email || '',
        status: c.status || 'Verified',
        bookings: c.bookings ?? 0,
        active: c.active ?? 0,
        paid: c.paid ?? 0,
        pending: c.pending ?? 0,
        backendSynced: true,
      }))
      setData((current) => ({
        ...current,
        customers: mapped,
      }))
    } catch (err) {
      console.warn('syncCustomers error:', err)
    }
  }

  async function syncOfflineBookings() {
    try {
      const backendBookings = await bookingService.listOfflineBookings()
      const list = Array.isArray(backendBookings) ? backendBookings : []
      const mapped = list.map((b) => ({
        id: b.id,
        customer: b.customer,
        vehicle: b.vehicle,
        dates: b.dates,
        type: b.type || 'Offline',
        status: b.status || 'Active',
        paid: Number(b.paid) || 0,
        pending: Number(b.pending) || 0,
        base_amount: b.base_amount,
        add_on_amount: b.add_on_amount,
        service_fee: b.service_fee,
        discount_amount: b.discount_amount,
        deposit_amount: b.deposit_amount,
        total_amount: Number(b.total_amount) || 0,
        rental_days: b.rental_days,
        vehicle_details: b.vehicle_details,
        customer_details: b.customer_details,
        rental_details: b.rental_details,
        payment_details: b.payment_details,
        notes: b.notes,
        backendSynced: true,
      }))
      setData((current) => ({
        ...current,
        bookings: mapped,
      }))
    } catch (err) {
      console.warn('syncOfflineBookings error:', err)
    }
  }

  async function syncDocuments() {
    try {
      const backendDocs = await documentService.listDocuments()
      const list = Array.isArray(backendDocs) ? backendDocs : []
      const mapped = list.map((d) => ({
        id: d.id,
        name: d.name,
        category: d.category,
        date: d.date,
        status: d.status || 'Verified',
        scope: d.scope || 'Business',
        file_url: d.file_url,
        backendSynced: true,
      }))
      setData((current) => ({
        ...current,
        documents: mapped,
      }))
    } catch (err) {
      console.warn('syncDocuments error:', err)
    }
  }

  async function syncPayments() {
    try {
      const backendPayments = await paymentService.listPayments()
      const list = Array.isArray(backendPayments) ? backendPayments : []
      const mapped = list.map((p) => ({
        id: p.id,
        booking: p.booking || p.booking_id,
        customer: p.customer || p.customer_name,
        method: p.method || 'UPI',
        date: p.date || p.payment_date,
        amount: Number(p.amount) || 0,
        status: p.status || 'Paid',
        notes: p.notes,
        backendSynced: true,
      }))
      setData((current) => ({
        ...current,
        payments: mapped,
      }))
    } catch (err) {
      console.warn('syncPayments error:', err)
    }
  }

  async function syncMaintenance() {
    try {
      const backendMaint = await maintenanceService.listMaintenance()
      const list = Array.isArray(backendMaint) ? backendMaint : []
      const mapped = list.map((m) => ({
        id: m.id,
        vehicle: m.vehicle || m.vehicle_name,
        type: m.type || m.maintenance_type,
        start: m.start || m.start_date,
        expected: m.expected || m.expected_date,
        cost: Number(m.cost || m.estimated_cost) || 0,
        payment: m.payment || m.payment_status || 'Paid',
        status: m.status || 'Ongoing',
        backendSynced: true,
      }))
      setData((current) => ({
        ...current,
        maintenance: mapped,
      }))
    } catch (err) {
      console.warn('syncMaintenance error:', err)
    }
  }

  async function syncFinance() {
    try {
      const [overview, expensesList] = await Promise.all([
        financeService.getOverview().catch(() => null),
        financeService.listExpenses().catch(() => []),
      ])
      setData((current) => ({
        ...current,
        financeOverview: overview,
        expenses: Array.isArray(expensesList)
          ? expensesList.map((e) => ({ ...e, backendSynced: true }))
          : [],
      }))
    } catch (err) {
      console.warn('syncFinance error:', err)
    }
  }

  async function syncNotifications() {
    try {
      const res = await notificationService.listNotifications({ limit: 100 })
      const list = Array.isArray(res) ? res : []
      setData((current) => ({
        ...current,
        notifications: list,
      }))
    } catch (err) {
      console.warn('syncNotifications error:', err)
    }
  }

  async function markNotificationRead(id) {
    try {
      await notificationService.markRead(id)
      setData((current) => ({
        ...current,
        notifications: (current.notifications || []).map((n) =>
          n.id === id ? { ...n, is_read: true } : n,
        ),
      }))
    } catch (err) {
      console.warn('markNotificationRead error:', err)
    }
  }

  async function markAllNotificationsRead() {
    try {
      await notificationService.markAllRead()
      setData((current) => ({
        ...current,
        notifications: (current.notifications || []).map((n) => ({ ...n, is_read: true })),
      }))
    } catch (err) {
      console.warn('markAllNotificationsRead error:', err)
    }
  }

  async function deleteNotification(id) {
    try {
      await notificationService.deleteNotification(id)
      setData((current) => ({
        ...current,
        notifications: (current.notifications || []).filter((n) => n.id !== id),
      }))
    } catch (err) {
      console.warn('deleteNotification error:', err)
    }
  }

  useEffect(() => {
    async function init() {
      // If vendor is not already logged in, sign into default vendor to ensure tenant endpoints respond
      if (!authService.isAuthenticated()) {
        try {
          await authService.login({
            email: 'vendor@wavygo.com',
            password: 'VendorPassword123!',
          })
        } catch (err) {
          console.warn('Initial vendor login fallback:', err)
        }
      }

      await Promise.allSettled([
        syncVehicles(),
        syncCustomers(),
        syncOfflineBookings(),
        syncDocuments(),
        syncPayments(),
        syncMaintenance(),
        syncFinance(),
        syncNotifications(),
      ])
    }

    init()
  }, [])

  function addRecord(collection, record) {
    setData((current) => ({
      ...current,
      [collection]: [record, ...(current[collection] || [])],
    }))
  }

  function updateRecord(collection, id, changes) {
    setData((current) => ({
      ...current,
      [collection]: (current[collection] || []).map((record) =>
        record.id === id ? { ...record, ...changes } : record,
      ),
    }))
  }

  function deleteRecord(collection, id) {
    setData((current) => ({
      ...current,
      [collection]: (current[collection] || []).filter((record) => record.id !== id),
    }))
  }

  return (
    <DemoDataContext.Provider
      value={{
        ...data,
        addRecord,
        updateRecord,
        deleteRecord,
        syncVehicles,
        syncCustomers,
        syncOfflineBookings,
        syncDocuments,
        syncPayments,
        syncMaintenance,
        syncFinance,
        syncNotifications,
        markNotificationRead,
        markAllNotificationsRead,
        deleteNotification,
        unreadNotificationsCount: (data.notifications || []).filter((n) => !n.is_read).length,
      }}
    >
      {children}
    </DemoDataContext.Provider>
  )
}

export function useDemoData() {
  const context = useContext(DemoDataContext)
  if (!context) {
    throw new Error('useDemoData must be used within DemoDataProvider.')
  }
  return context
}
