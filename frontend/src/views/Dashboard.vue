<template>
  <header class="topbar">
    <h1 class="topbar__title">Hotel PMS · Gestión Interna</h1>
    <div class="topbar__right">
      <span class="role-badge">{{ rolDisplay }}</span>
      <button class="btn-ghost-danger" @click="logout">Cerrar sesión</button>
    </div>
  </header>

  <main class="page">
    <!-- Administrador -->
    <section v-if="rolActivo === 'administrador'" class="panel">
      <h2 class="panel__title">Panel Administrativo</h2>

      <div class="metrics-grid">
        <div class="metric-card">
          <span class="metric-card__label">Total Habitaciones</span>
          <span class="metric-card__value">{{ totalHabitaciones }}</span>
        </div>
        <div class="metric-card metric-card--success">
          <span class="metric-card__label">Disponibles</span>
          <span class="metric-card__value">{{ habitacionesDisponibles }}</span>
        </div>
        <div class="metric-card metric-card--navy">
          <span class="metric-card__label">Ocupadas</span>
          <span class="metric-card__value">{{ habitacionesOcupadas }}</span>
        </div>
        <div class="metric-card metric-card--warning">
          <span class="metric-card__label">Mantenimiento</span>
          <span class="metric-card__value">{{ habitacionesMantenimiento }}</span>
        </div>
      </div>

      <nav class="nav-pills">
        <button class="nav-pill" :class="{ 'is-active': currentAdminView === 'monitor' }" type="button" @click="showMonitor()">Monitor de Habitaciones</button>
        <button class="nav-pill" :class="{ 'is-active': currentAdminView === 'config' }" type="button" @click="showConfig()">Configuración del Sistema</button>
        <button class="nav-pill" :class="{ 'is-active': currentAdminView === 'pagos' }" type="button" @click="showPagos()">Auditoría de Pagos</button>
        <button class="nav-pill" :class="{ 'is-active': currentAdminView === 'empleados' }" type="button" @click="showEmpleados()">Gestión de Empleados</button>
      </nav>

      <div v-if="currentAdminView === 'monitor'" class="card">
        <h3 class="card__title">Monitor de Habitaciones</h3>
        <ul class="room-list">
          <li v-for="room in rooms" :key="room.ID_Habitacion" class="room-row">
            <div class="room-row__info">
              <strong>Hab {{ room.numero }}</strong>
              <span class="room-row__meta">Tipo: {{ room.tipo || 'N/A' }} · Precio: {{ room.precio_noche || '-' }}</span>
            </div>
            <span class="status-badge" :class="`status-badge--${room.estado}`">
              <span class="status-badge__dot"></span>{{ room.estado }}
            </span>
          </li>
        </ul>
      </div>

      <div v-else-if="currentAdminView === 'config'" class="card">
        <h3 class="card__title">Configuración del Sistema</h3>
        <form class="form-grid" @submit.prevent="saveConfig">
          <div class="form-group">
            <label for="hotel-name">Nombre del Hotel</label>
            <input id="hotel-name" type="text" v-model="config.nombre_hotel" />
          </div>
          <div class="form-group">
            <label for="checkin-time">Hora de Check-in</label>
            <input id="checkin-time" type="text" v-model="config.hora_checkin" />
          </div>
          <div class="form-group">
            <label for="checkout-time">Hora de Check-out</label>
            <input id="checkout-time" type="text" v-model="config.hora_checkout" />
          </div>
          <button class="btn-gold form-grid__submit" type="submit">Guardar Cambios</button>
        </form>
      </div>

      <div v-else-if="currentAdminView === 'pagos'" class="card">
        <h3 class="card__title">Auditoría de Pagos</h3>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Habitación</th>
              <th>Monto</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pago in pagos" :key="pago.ID_Boleta">
              <td>{{ pago.ID_Boleta }}</td>
              <td>{{ pago.numero_habitacion }}</td>
              <td>{{ pago.monto }}</td>
              <td>{{ pago.estado }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="currentAdminView === 'empleados'" class="card">
        <h3 class="card__title">Gestión de Empleados</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="empleado in empleados" :key="empleado.id || empleado.ID || empleado.ID_Usuario">
              <td>{{ empleado.nombre || empleado.name || empleado.full_name || 'N/A' }}</td>
              <td>{{ empleado.correo || empleado.email || empleado.email_address || 'N/A' }}</td>
              <td>{{ empleado.rol || empleado.role || empleado.user_type || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Recepcionista -->
    <section v-else-if="rolActivo === 'recepcionista'" class="panel">
      <h2 class="panel__title">Centro de Control Operativo</h2>

      <!-- Registro de Nuevo Huésped -->
      <div class="card card--accent">
        <h3 class="card__title card__title--accent">Registro de Nuevo Huésped (Check-In Presencial)</h3>

        <div v-if="generatedAccessCode" class="success-banner">
          <h4 class="success-banner__title">¡Registro exitoso!</h4>
          <p class="success-banner__text">Código de acceso para el huésped:</p>
          <strong class="success-banner__code">{{ generatedAccessCode }}</strong>
          <button class="btn-gold success-banner__dismiss" @click="generatedAccessCode = null">Entendido</button>
        </div>

        <form class="checkin-form" @submit.prevent="submitCheckIn">
          <div class="form-group">
            <label>DNI / Documento de Identidad <span class="required">*</span></label>
            <input type="text" v-model="checkinForm.dni" required placeholder="Ej: 12345678" />
          </div>

          <div class="form-group">
            <label>Nombre Completo del Huésped <span class="required">*</span></label>
            <input type="text" v-model="checkinForm.nombreCompleto" required placeholder="Nombres y Apellidos" />
          </div>

          <div class="form-group">
            <label>Teléfono / Celular <span class="required">*</span></label>
            <input type="text" v-model="checkinForm.telefono" required placeholder="Ej: 987654321" />
          </div>

          <div class="form-group">
            <label>Correo Electrónico</label>
            <input type="email" v-model="checkinForm.correo" placeholder="ejemplo@correo.com" />
          </div>

          <div class="form-group">
            <label>Habitación a Asignar <span class="required">*</span></label>
            <select v-model="checkinForm.idHabitacion" required>
              <option value="" disabled>Seleccione una habitación...</option>
              <option v-for="room in rooms.filter(r => String(r.estado || '').toLowerCase() === 'disponible')" :key="room.ID_Habitacion" :value="room.ID_Habitacion">
                Hab {{ room.numero }} ({{ room.tipo || 'N/A' }} - S/. {{ room.precio_noche }})
              </option>
            </select>
          </div>

          <div class="checkin-form__submit">
            <button type="submit" class="btn-navy">
              🔑 Registrar Estadía y Generar Código de Acceso
            </button>
          </div>
        </form>
      </div>

      <div class="card">
        <h3 class="card__title">Gestión de Habitaciones</h3>
        <ul class="room-list">
          <li v-for="room in rooms" :key="room.ID_Habitacion" class="room-row">
            <div class="room-row__info">
              <strong>Hab {{ room.numero }}</strong>
              <span class="room-row__meta">Tipo: {{ room.tipo || 'N/A' }} — Precio: {{ room.precio_noche || '-' }}</span>
            </div>
            <div class="room-row__actions">
              <button class="btn-gold btn-sm" @click="registerCheckOut(room)" v-if="room.estado === 'ocupada'">Registrar Check-Out</button>
              <span class="status-badge status-badge--mantenimiento" v-else-if="room.estado === 'mantenimiento'">
                <span class="status-badge__dot"></span>En Limpieza
              </span>
              <span class="status-badge status-badge--disponible" v-else-if="room.estado === 'disponible'">
                <span class="status-badge__dot"></span>Disponible
              </span>
            </div>
          </li>
        </ul>
      </div>

      <div class="card">
        <h3 class="card__title">Gestión de Notas de Servicio (Tickets de Huésped)</h3>

        <div v-if="tickets.length === 0" class="empty-state">
          <span class="empty-state__icon">📭</span>
          <p>No hay solicitudes de servicio pendientes en este momento.</p>
        </div>

        <ul v-else class="ticket-list">
          <li v-for="t in tickets" :key="t.id" class="ticket-row">
            <div class="ticket-row__info">
              <strong>{{ t.title }}</strong> — <span class="ticket-row__guest">{{ t.guest }}</span>

              <div v-if="t.type === 'parking'" class="parking-block">
                <select v-model="t.parking_number" class="parking-block__select">
                  <option value="" disabled>Seleccione cochera...</option>
                  <option v-for="p in availableParkings" :key="p.ID_Parking" :value="String(p.numero)">
                    Cochera #{{ p.numero }}
                  </option>
                </select>
                <div v-if="availableParkings.length === 0" class="parking-block__warning">
                  ⚠️ No hay cocheras disponibles.
                </div>
                <div class="parking-block__rate">💡 Tarifa Fija Automática: S/. 20.00</div>
              </div>
            </div>

            <div class="ticket-row__actions">
              <button class="btn-success btn-sm" @click="validateTicket(t.id)" :disabled="t.type === 'parking' && !t.parking_number">Validar</button>
              <button class="btn-navy btn-sm" @click="markDelivered(t.id)">Marcar Entregado</button>
              <button class="btn-danger btn-sm" @click="cancelTicket(t.id)">Cancelar</button>
            </div>
          </li>
        </ul>
      </div>
    </section>

    <!-- Personal de Limpieza -->
    <section v-else-if="rolActivo === 'personal_limpieza'" class="panel">
      <h2 class="panel__title">Personal de Limpieza</h2>
      <p class="info-text">Nota: Las habitaciones pasan a estado 'Sucia' automáticamente tras cada Check-out.</p>

      <nav class="tabs">
        <button :class="['tab-btn', limpiezaTab === 'pending' ? 'is-active' : '']" @click="limpiezaTab = 'pending'">Habitaciones por Atender</button>
        <button :class="['tab-btn', limpiezaTab === 'all' ? 'is-active' : '']" @click="limpiezaTab = 'all'">Todas las Habitaciones</button>
      </nav>

      <div class="card" v-if="limpiezaTab === 'pending'">
        <h3 class="card__title">Habitaciones por Atender</h3>
        <ul class="room-list">
          <li v-for="room in pendingRooms" :key="room.ID_Habitacion" class="room-row">
            <div class="room-row__info">
              <strong>Hab {{ room.numero }}</strong>
              <span class="status-badge" :class="`status-badge--${room.estado}`">
                <span class="status-badge__dot"></span>{{ room.estado }}
              </span>
            </div>
            <button class="btn-gold btn-sm" @click="markAsClean(room)">Marcar como Limpia/Lista</button>
          </li>
        </ul>
      </div>

      <div class="card" v-else>
        <h3 class="card__title">Todas las Habitaciones</h3>
        <ul class="room-list">
          <li v-for="room in rooms" :key="room.ID_Habitacion" class="room-row">
            <div class="room-row__info">
              <strong>Hab {{ room.numero }}</strong>
              <span class="room-row__meta">Tipo: {{ room.tipo || 'N/A' }} · Precio: {{ room.precio_noche || '-' }}</span>
            </div>
            <div class="room-row__actions">
              <span class="status-badge" :class="`status-badge--${room.estado}`">
                <span class="status-badge__dot"></span>{{ room.estado }}
              </span>
              <button class="btn-gold btn-sm" @click="markAsClean(room)" v-if="['sucia', 'mantenimiento'].includes(String(room.estado || '').toLowerCase())">Marcar como Limpia/Lista</button>
              <button class="btn-ghost btn-sm" @click="reportDirty(room)" v-if="String(room.estado || '').toLowerCase() !== 'sucia'">Reportar como Sucia</button>
            </div>
          </li>
        </ul>
      </div>
    </section>

    <!-- Huésped -->
    <section v-else-if="rolActivo === 'huesped'" class="panel">
      <h2 class="panel__title">Bienvenido a tu Estancia</h2>

      <!-- Información de habitación -->
      <div class="guest-hero">
        <div class="guest-hero__room">
          <span class="guest-hero__label">Tu Habitación</span>
          <span class="guest-hero__number">{{ estadia.numero_habitacion }}</span>
          <span class="guest-hero__type">{{ estadia.tipo_habitacion }}</span>
        </div>
        <div class="guest-hero__dates">
          <div>
            <span class="guest-hero__label">Check-in</span>
            <span class="guest-hero__date">{{ estadia.fecha_entrada }}</span>
          </div>
          <div>
            <span class="guest-hero__label">Check-out</span>
            <span class="guest-hero__date">{{ estadia.fecha_salida }}</span>
          </div>
        </div>
      </div>

      <!-- Resumen de cuenta -->
      <div class="card">
        <h3 class="card__title">Resumen de Cuenta</h3>
        <div class="account-grid">
          <div class="account-tile account-tile--success">
            <span class="account-tile__label">Alojamiento</span>
            <span class="account-tile__value">S/. {{ (estadia.monto_total * 0.7).toFixed(2) }}</span>
          </div>
          <div class="account-tile account-tile--warning">
            <span class="account-tile__label">Servicios Adicionales</span>
            <span class="account-tile__value">S/. {{ (estadia.costo_parking).toFixed(2) }}</span>
          </div>
          <div class="account-tile account-tile--danger">
            <span class="account-tile__label">Total Acumulado</span>
            <span class="account-tile__value">S/. {{ estadia.monto_total.toFixed(2) }}</span>
          </div>
        </div>
        <div class="account-footnote">
          <strong>Estado de Boleta:</strong> {{ estadia.estado_boleta }} — El pago será procesado en recepción al momento del check-out.
        </div>
      </div>

      <!-- Estacionamiento -->
      <div class="card">
        <h3 class="card__title">🚗 Servicio de Estacionamiento</h3>

        <div v-if="estadia.cochera_asignada === 'Ninguna' || estadia.cochera_asignada === ''" class="parking-empty">
          <p>No tienes cochera asignada. Solicita un espacio de estacionamiento para tu vehículo.</p>
          <button class="btn-gold" @click="requestParking()">Solicitar Espacio de Cochera</button>
        </div>

        <div v-else class="parking-assigned">
          <div>
            <span class="parking-assigned__label">Cochera Asignada</span>
            <span class="parking-assigned__value">{{ estadia.cochera_asignada }}</span>
          </div>
          <div>
            <span class="parking-assigned__label">Costo Adicional</span>
            <span class="parking-assigned__value">S/. {{ Number(estadia.costo_parking).toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Solicitudes Express -->
      <div class="card">
        <h3 class="card__title">⚡ Solicitudes Express</h3>
        <p class="info-text">Haz clic en cualquiera de estos botones para realizar una solicitud inmediata.</p>

        <div class="express-grid">
          <button class="express-btn express-btn--blue" @click="requestTowels()">🛁 Pedir Toallas Extras</button>
          <button class="express-btn express-btn--green" @click="requestRoomService()">🍽️ Servicio al Cuarto</button>
        </div>
      </div>
    </section>

    <!-- Fallback -->
    <section v-else class="panel">
      <div class="card">
        <h2 class="panel__title">Acceso no autorizado</h2>
        <p>No tiene permiso para ver este panel.</p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getHabitaciones, actualizarEstadoHabitacion, getEmpleados, getPagos, getConfiguracion, actualizarConfiguracion, getEstadiaHuesped, getPerfilHuesped, getServicios, createServiceNote, getNotasServicio, actualizarNotaServicio, getReservas, actualizarEstadoReserva, getHuesped, createHuesped, createReserva, createCodigoAcceso, getParkings } from '../services/api'

const router = useRouter()
const accessToken = ref(null)
const rolActivo = ref('')
const rolDisplay = computed(() => {
  const roleMap = {
    administrador: 'Administrador',
    recepcionista: 'Recepcionista',
    personal_limpieza: 'Personal de Limpieza',
    huesped: 'Huésped'
  }
  return roleMap[rolActivo.value] || 'Desconocido'
})

const currentAdminView = ref('monitor')

const rooms = ref([])
const empleados = ref([])
const pagos = ref([])
const config = ref({ nombre_hotel: '', hora_checkin: '', hora_checkout: '' })
const estadia = ref({
  ID_Reserva: null,
  numero_habitacion: null,
  tipo_habitacion: null,
  fecha_entrada: null,
  fecha_salida: null,
  monto_total: 0,
  estado_boleta: 'Sin facturar',
  cochera_asignada: 'Ninguna',
  costo_parking: 0
})

const servicios = ref([])
const limpiezaTab = ref('pending')

const pendingRooms = computed(() => {
  return rooms.value.filter(r => ['sucia', 'mantenimiento'].includes(String(r.estado || '').toLowerCase()))
})

const totalHabitaciones = computed(() => rooms.value.length)
const habitacionesDisponibles = computed(() => rooms.value.filter(r => String(r.estado || '').toLowerCase() === 'disponible').length)
const habitacionesOcupadas = computed(() => rooms.value.filter(r => String(r.estado || '').toLowerCase() === 'ocupada').length)
const habitacionesMantenimiento = computed(() => rooms.value.filter(r => String(r.estado || '').toLowerCase() === 'mantenimiento').length)

const tickets = ref([])
const availableParkings = ref([])

const checkinForm = reactive({
  dni: '',
  nombreCompleto: '',
  correo: '',
  telefono: '',
  idHabitacion: ''
})
const generatedAccessCode = ref(null)

async function loadAvailableParkings() {
  try {
    const data = await getParkings()
    availableParkings.value = (Array.isArray(data) ? data : [])
      .filter(p => String(p.estado || '').toLowerCase() === 'disponible')
  } catch (err) {
    console.error('Error cargando parkings:', err)
  }
}

async function loadTickets() {
  loadAvailableParkings()
  try {
    const data = await getNotasServicio()
    tickets.value = (Array.isArray(data) ? data : [])
      .filter(t => t.estado === 'pendiente')
      .map(t => {
        const esParking = t.concepto === 'Solicitud de Cochera' || 
                          t.concepto === 'cochera' ||
                          t.concepto === 'parking' ||
                          (t.concepto && t.concepto.toLowerCase().includes('cochera'))
        return {
          id: t.ID_Nota,
          title: t.concepto || 'Servicio Especial',
          guest: `Reserva #${t.ID_Reserva}`,
          validated: t.estado !== 'pendiente',
          delivered: t.estado === 'entregado' || t.estado === 'completado',
          type: esParking ? 'parking' : 'servicio',
          parking_number: '',
          parking_cost: 20.00,
          ID_Reserva: t.ID_Reserva,
          ID_Servicio: t.ID_Servicio
        }
      })
  } catch (err) {
    console.error('Error cargando notas de servicio:', err)
  }
}

onMounted(() => {
  accessToken.value = localStorage.getItem('access_token')
  const userType = localStorage.getItem('user_type')
  if (!accessToken.value) {
    router.replace('/')
    return
  }
  
  if (userType === 'huesped') {
    rolActivo.value = 'huesped'
    loadEstadiaHuesped()
    loadServicios()
  } else if (userType === 'administrador' || userType === 'recepcionista' || userType === 'personal_limpieza') {
    rolActivo.value = userType
    if (userType === 'personal_limpieza' || userType === 'recepcionista' || userType === 'administrador') {
      loadRooms()
      if (userType === 'recepcionista' || userType === 'administrador') {
        loadTickets()
        loadAvailableParkings()
      }
    }
  } else {
    router.replace('/')
  }
})

async function loadRooms() {
  try {
    const data = await getHabitaciones()
    console.log('Datos de habitaciones desde la API:', data)
    rooms.value = Array.isArray(data)
      ? data.map(item => ({
          ID_Habitacion: item.ID_Habitacion,
          numero: item.numero,
          estado: item.estado,
          tipo: item.tipo,
          precio_noche: item.precio_noche,
        }))
      : []
  } catch (err) {
    console.error('Error cargando habitaciones:', err)
    alert('No se pudieron cargar las habitaciones. Revise la conexión.')
  }
}

async function loadEmpleados() {
  try {
    const data = await getEmpleados()
    empleados.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('Error cargando empleados:', err)
    alert('No se pudieron cargar los empleados.')
  }
}

async function loadPagos() {
  try {
    const data = await getPagos()
    pagos.value = Array.isArray(data) ? data : []
  } catch (err) {
    console.error('Error cargando pagos:', err)
    alert('No se pudieron cargar los pagos.')
  }
}

async function loadConfig() {
  try {
    const data = await getConfiguracion()
    if (data) {
      config.value = {
        nombre_hotel: data.nombre_hotel || data.hotel_name || '',
        hora_checkin: data.hora_checkin || data.checkin_time || '',
        hora_checkout: data.hora_checkout || data.checkout_time || '',
      }
    }
  } catch (err) {
    console.error('Error cargando configuración:', err)
    alert('No se pudo cargar la configuración.')
  }
}

async function saveConfig() {
  try {
    const resp = await actualizarConfiguracion(config.value)
    config.value = {
      nombre_hotel: resp.nombre_hotel || resp.hotel_name || config.value.nombre_hotel,
      hora_checkin: resp.hora_checkin || resp.checkin_time || config.value.hora_checkin,
      hora_checkout: resp.hora_checkout || resp.checkout_time || config.value.hora_checkout,
    }
    alert('Cambios guardados con éxito')
  } catch (err) {
    console.error('Error guardando configuración:', err)
    alert('No se pudo guardar la configuración.')
  }
}

function showMonitor() {
  currentAdminView.value = 'monitor'
}

async function showConfig() {
  currentAdminView.value = 'config'
  await loadConfig()
}

async function showPagos() {
  currentAdminView.value = 'pagos'
  await loadPagos()
}

async function showEmpleados() {
  currentAdminView.value = 'empleados'
  await loadEmpleados()
}

function logout() {
  localStorage.clear()
  router.replace('/')
}

// Recepcionista: check-in presencial / check-out
async function submitCheckIn() {
  if (!checkinForm.dni || !checkinForm.nombreCompleto || !checkinForm.telefono || !checkinForm.idHabitacion) {
    alert('⚠️ Por favor complete todos los campos obligatorios.')
    return
  }

  try {
    // 1. Obtener o crear huésped
    let huesped = await getHuesped(checkinForm.dni)
    if (!huesped) {
      const parts = checkinForm.nombreCompleto.trim().split(/\s+/)
      const nombre = parts[0] || 'Invitado'
      const apellido = parts.slice(1).join(' ') || 'N/A'
      
      huesped = await createHuesped({
        DNI: checkinForm.dni,
        nombre: nombre,
        apellido: apellido,
        correo: checkinForm.correo || null,
        telefono: checkinForm.telefono,
        estado: 'activo'
      })
    }

    // 2. Crear reserva
    const selectedRoom = rooms.value.find(r => r.ID_Habitacion === Number(checkinForm.idHabitacion))
    if (!selectedRoom) {
      alert('❌ La habitación seleccionada no es válida.')
      return
    }

    const entryDate = new Date()
    const exitDate = new Date()
    // Se establece una fecha de salida por defecto de +1 día para cumplir con las validaciones de base de datos.
    // El cobro real será calculado en tiempo real con fecha actual.
    exitDate.setDate(exitDate.getDate() + 1)

    const totalCost = Number(selectedRoom.precio_noche || 0)

    const payloadReserva = {
      Huesped_DNI: huesped.DNI,
      ID_Habitacion: selectedRoom.ID_Habitacion,
      fecha_entrada: entryDate.toISOString().split('T')[0],
      fecha_salida: exitDate.toISOString().split('T')[0],
      precio_total: totalCost,
      estado: 'confirmada'
    }

    const nuevaReserva = await createReserva(payloadReserva)

    // 3. Generar y crear código de acceso
    let generatedCode = ''
    let codeSuccess = false
    let retries = 3
    while (!codeSuccess && retries > 0) {
      generatedCode = String(Math.floor(1000 + Math.random() * 9000))
      try {
        await createCodigoAcceso({
          DNI: huesped.DNI,
          valor: generatedCode,
          activo: true
        })
        codeSuccess = true
      } catch (err) {
        retries--
        if (retries === 0) {
          throw new Error('No se pudo generar un código de acceso único. Inténtelo de nuevo.')
        }
      }
    }

    // 4. Mostrar éxito y código generado
    generatedAccessCode.value = generatedCode

    // 5. Limpiar formulario
    checkinForm.dni = ''
    checkinForm.nombreCompleto = ''
    checkinForm.correo = ''
    checkinForm.telefono = ''
    checkinForm.idHabitacion = ''

    // 6. Refrescar habitaciones
    await loadRooms()
  } catch (err) {
    console.error('Error durante el check-in presencial:', err)
    alert('❌ Ocurrió un error al procesar el Check-In: ' + err.message)
  }
}

async function registerCheckOut(room) {
  if (!room || !room.ID_Habitacion) return
  try {
    // 1. Buscar la reserva de esa habitación (probar con 'confirmada' primero, que es el estado del check-in)
    let reservaActiva = null
    
    // Intentar con estado 'confirmada' (estado real del check-in)
    try {
      const reservasConfirmadas = await getReservas('confirmada')
      reservaActiva = (Array.isArray(reservasConfirmadas) ? reservasConfirmadas : [])
        .find(r => r.ID_Habitacion === room.ID_Habitacion)
    } catch (e) {
      console.warn('No se encontraron reservas confirmadas:', e)
    }

    // Si no se encontró, intentar buscando todas las reservas pendientes
    if (!reservaActiva) {
      try {
        const reservasPendientes = await getReservas('pendiente')
        reservaActiva = (Array.isArray(reservasPendientes) ? reservasPendientes : [])
          .find(r => r.ID_Habitacion === room.ID_Habitacion)
      } catch (e) {
        console.warn('No se encontraron reservas pendientes:', e)
      }
    }
    
    if (!reservaActiva) {
      alert('⚠️ No se encontró una reserva activa para esta habitación.')
      return
    }

    // 2. Actualizar estado de reserva a 'terminada' (genera boleta y desactiva código en backend)
    const respReserva = await actualizarEstadoReserva(reservaActiva.ID_Reserva, 'terminada')
    console.log('Reserva actualizada a terminada:', respReserva)

    // 3. Marcar habitación en mantenimiento
    const resp = await actualizarEstadoHabitacion(room.ID_Habitacion, 'mantenimiento')
    room.estado = (resp && resp.estado) || 'mantenimiento'

    // 4. Refrescar listado de habitaciones
    await loadRooms()

    alert('✅ Check-Out registrado exitosamente. Boleta generada automáticamente.')
  } catch (err) {
    console.error('Error registrando check-out:', err)
    alert('❌ No se pudo registrar el check-out: ' + err.message)
  }
}

// Tickets
async function validateTicket(ticketId) {
  const t = tickets.value.find(x => x.id === ticketId)
  if (!t) return

  try {
    const payload = {
      estado: 'completado',
      cochera_asignada: t.type === 'parking' ? t.parking_number : undefined,
      costo_parking: t.type === 'parking' ? 20.00 : undefined
    }
    await actualizarNotaServicio(ticketId, payload)
    alert('✅ Ticket validado y completado con éxito.')
    // Desaparece inmediatamente de la lista activa en el frontend
    tickets.value = tickets.value.filter(x => x.id !== ticketId)
    loadAvailableParkings()
  } catch (err) {
    console.error('Error al validar ticket:', err)
    alert('❌ No se pudo validar el ticket: ' + err.message)
  }
}

async function markDelivered(ticketId) {
  try {
    await actualizarNotaServicio(ticketId, { estado: 'completado' })
    alert('✅ Solicitud marcada como entregada/completada con éxito.')
    // Desaparece inmediatamente de la lista activa
    tickets.value = tickets.value.filter(x => x.id !== ticketId)
  } catch (err) {
    console.error('Error al completar ticket:', err)
    alert('❌ No se pudo completar el ticket.')
  }
}

async function cancelTicket(ticketId) {
  const t = tickets.value.find(x => x.id === ticketId)
  if (!t) return

  const motivo = window.prompt('Ingrese obligatoriamente el motivo de la cancelación:')
  if (motivo === null) return // Clic en Cancelar del prompt

  if (!motivo.trim()) {
    alert('⚠️ El motivo de cancelación es obligatorio.')
    return
  }

  try {
    await actualizarNotaServicio(ticketId, {
      estado: 'cancelado',
      motivo_cancelacion: motivo.trim()
    })
    alert('✅ Solicitud cancelada con éxito.')
    // Desaparece inmediatamente de la lista activa
    tickets.value = tickets.value.filter(x => x.id !== ticketId)
  } catch (err) {
    console.error('Error al cancelar ticket:', err)
    alert('❌ No se pudo cancelar la solicitud.')
  }
}

// Limpieza
async function markAsClean(room) {
  if (!room || !room.ID_Habitacion) return
  try {
    const resp = await actualizarEstadoHabitacion(room.ID_Habitacion, 'disponible')
    room.estado = (resp && resp.estado) || 'disponible'
  } catch (err) {
    console.error('Error actualizando estado:', err)
    alert('No se pudo actualizar el estado de la habitación.')
  }
}

async function reportDirty(room) {
  if (!room || !room.ID_Habitacion) return
  try {
    const resp = await actualizarEstadoHabitacion(room.ID_Habitacion, 'mantenimiento')
    room.estado = (resp && resp.estado) || 'mantenimiento'
  } catch (err) {
    console.error('Error reportando habitación como mantenimiento:', err)
    alert('No se pudo marcar la habitación como mantenimiento.')
  }
}

// Huésped: cargar información de estadía
async function loadEstadiaHuesped() {
  try {
    // Intentar obtener la estadía actual del huésped con getEstadiaHuesped()
    // Este endpoint debe buscar sin restricción de estado (activa, terminada, etc)
    let data = await getEstadiaHuesped()
    console.log('Datos de estadía desde getEstadiaHuesped:', data)

    // Si falla y hay ID_Reserva en localStorage, intentar con getPerfilHuesped
    if (!data && localStorage.getItem('id_reserva')) {
      try {
        data = await getPerfilHuesped(localStorage.getItem('id_reserva'))
        console.log('Datos de estadía desde getPerfilHuesped:', data)
      } catch (err) {
        console.warn('Error con getPerfilHuesped:', err)
        throw err
      }
    }

    estadia.value = {
      ID_Reserva: data.ID_Reserva || null,
      numero_habitacion: data.numero_habitacion || 'N/A',
      tipo_habitacion: data.tipo_habitacion || 'N/A',
      fecha_entrada: data.fecha_entrada ? new Date(data.fecha_entrada).toLocaleDateString() : 'N/A',
      fecha_salida: data.fecha_salida ? new Date(data.fecha_salida).toLocaleDateString() : 'N/A',
      monto_total: data.monto_total || 0,
      estado_boleta: data.estado_boleta || 'Sin facturar',
      cochera_asignada: data.cochera_asignada || 'Ninguna',
      costo_parking: data.costo_parking || 0
    }

    // Guardar ID_Reserva en localStorage para futuras cargas
    if (estadia.value.ID_Reserva) {
      localStorage.setItem('id_reserva', estadia.value.ID_Reserva)
    }

    console.log('Estadia cargada exitosamente:', estadia.value)
  } catch (err) {
    console.error('Error cargando información de estadía:', err)
    alert('No se pudo cargar la información de tu habitación.')
  }
}

// Huésped: solicitar servicio
function requestService() {
  alert('✓ Servicio solicitado con éxito, se cargará a tu habitación')
}

// Huésped: cargar servicios disponibles
async function loadServicios() {
  try {
    const data = await getServicios()
    servicios.value = Array.isArray(data) ? data : []
    console.log('Servicios disponibles:', servicios.value)
  } catch (err) {
    console.error('Error cargando servicios:', err)
  }
}

// Huésped: solicitar toallas extras
async function requestTowels() {
  if (!estadia.value.ID_Reserva) {
    alert('Error: No se pudo identificar tu reserva.')
    return
  }
  try {
    // Buscar el servicio "Toallas Extras"
    const toallasServicio = servicios.value.find(s => s.nombre.toLowerCase().includes('toalla'))
    if (!toallasServicio) {
      alert('El servicio de Toallas Extras no está disponible en este momento.')
      return
    }
    await createServiceNote(estadia.value.ID_Reserva, toallasServicio.ID_Servicio)
    alert('✓ Solicitud de Toallas Extras enviada. Se entregarán en breve.')
  } catch (err) {
    console.error('Error solicitando toallas:', err)
    alert('No se pudo registrar la solicitud de toallas.')
  }
}

// Huésped: solicitar servicio al cuarto
async function requestRoomService() {
  if (!estadia.value.ID_Reserva) {
    alert('Error: No se pudo identificar tu reserva.')
    return
  }
  try {
    // Buscar el servicio "Servicio al Cuarto"
    const roomServicio = servicios.value.find(s => s.nombre.toLowerCase().includes('cuarto') || s.nombre.toLowerCase().includes('alimentos'))
    if (!roomServicio) {
      alert('El servicio al Cuarto no está disponible en este momento.')
      return
    }
    await createServiceNote(estadia.value.ID_Reserva, roomServicio.ID_Servicio)
    alert('✓ Solicitud de Servicio al Cuarto enviada. Pronto te atenderemos.')
  } catch (err) {
    console.error('Error solicitando servicio al cuarto:', err)
    alert('No se pudo registrar la solicitud de servicio.')
  }
}

// Huésped: solicitar cochera (crea una Nota de Servicio)
async function requestParking() {
  if (!estadia.value.ID_Reserva) {
    alert('Error: No se pudo identificar tu reserva.')
    return
  }
  try {
    // Buscar el servicio "Cochera" o "Parking"
    const parkingServicio = servicios.value.find(s => s.nombre.toLowerCase().includes('cochera') || s.nombre.toLowerCase().includes('parking'))
    if (!parkingServicio) {
      alert('El servicio de Cochera no está disponible en este momento.')
      return
    }
    await createServiceNote(estadia.value.ID_Reserva, parkingServicio.ID_Servicio)
    alert('✓ Solicitud de Cochera enviada. El recepcionista te asignará un espacio en breve.')
  } catch (err) {
    console.error('Error solicitando cochera:', err)
    alert('No se pudo registrar la solicitud de cochera.')
  }
}
</script>

<script>
// Simple global filter for currency formatting in this SFC
export default {
  filters: {
    currency(value) {
      if (typeof value !== 'number') return value
      return value.toLocaleString('es-ES', { style: 'currency', currency: 'EUR' })
    }
  }
}
</script>

<style scoped>
/* ===== Topbar ===== */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.1rem 1.75rem;
  background: var(--white);
  border-bottom: 1px solid var(--cream-dark);
}
.topbar__title {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--navy);
}
.topbar__right { display: flex; gap: 1rem; align-items: center; }
.role-badge {
  background: var(--cream);
  color: var(--navy-mid);
  border: 1px solid var(--cream-dark);
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
}

/* ===== Layout ===== */
.page { padding: 1.5rem; display: grid; gap: 1.25rem; background: var(--cream); min-height: 100vh; }
.panel { display: flex; flex-direction: column; gap: 1.25rem; }
.panel__title { font-family: var(--font-display); font-size: 1.5rem; color: var(--navy); }

/* ===== Cards ===== */
.card {
  background: var(--white);
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
}
.card--accent { border-left: 4px solid var(--gold); }
.card__title { font-size: 1.1rem; margin-bottom: 1rem; color: var(--navy); }
.card__title--accent { color: var(--navy-mid); }

/* ===== Métricas (admin) ===== */
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
.metric-card {
  background: var(--white);
  border: 1px solid var(--cream-dark);
  border-left: 4px solid var(--slate);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.metric-card--success { border-left-color: var(--success); }
.metric-card--navy { border-left-color: var(--navy); }
.metric-card--warning { border-left-color: var(--warning); }
.metric-card__label { font-size: 0.78rem; color: var(--slate); text-transform: uppercase; letter-spacing: 0.04em; }
.metric-card__value { font-family: var(--font-display); font-size: 1.9rem; color: var(--navy); }

/* ===== Nav pills / tabs ===== */
.nav-pills, .tabs { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.nav-pill, .tab-btn {
  background: var(--white);
  border: 1px solid var(--cream-dark);
  color: var(--navy-mid);
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.15s ease;
}
.nav-pill:hover, .tab-btn:hover { border-color: var(--gold); color: var(--navy); }
.nav-pill.is-active, .tab-btn.is-active {
  background: var(--navy);
  border-color: var(--navy);
  color: var(--white);
}

/* ===== Listas de habitaciones ===== */
.room-list, .ticket-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; }
.room-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--cream-dark);
}
.room-row:last-child { border-bottom: none; }
.room-row__info { display: flex; flex-direction: column; gap: 0.2rem; }
.room-row__meta { color: var(--slate); font-size: 0.82rem; }
.room-row__actions { display: flex; gap: 0.6rem; align-items: center; }

/* ===== Status badges ===== */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: capitalize;
  background: var(--cream);
  color: var(--navy-mid);
}
.status-badge__dot { width: 7px; height: 7px; border-radius: 50%; background: var(--slate); }
.status-badge--disponible { background: rgba(62, 158, 111, 0.12); color: var(--success); }
.status-badge--disponible .status-badge__dot { background: var(--success); }
.status-badge--ocupada { background: rgba(30, 58, 95, 0.10); color: var(--navy-mid); }
.status-badge--ocupada .status-badge__dot { background: var(--navy-mid); }
.status-badge--mantenimiento, .status-badge--sucia { background: rgba(232, 150, 58, 0.14); color: var(--warning); }
.status-badge--mantenimiento .status-badge__dot, .status-badge--sucia .status-badge__dot { background: var(--warning); }

/* ===== Tablas ===== */
.table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.table th {
  background: var(--cream);
  color: var(--navy-mid);
  font-weight: 600;
  padding: 0.8rem;
  text-align: left;
  border-bottom: 2px solid var(--cream-dark);
}
.table td {
  padding: 0.75rem 0.8rem;
  border-bottom: 1px solid var(--cream-dark);
}
.table tbody tr:hover { background: rgba(255, 255, 255, 0.5); }

/* ===== Forms ===== */
.form-grid { display: grid; gap: 1rem; }
.form-grid__submit { justify-self: flex-start; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--navy-mid);
}
.form-group input, .form-group select, .form-group textarea {
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-sm);
  padding: 0.65rem 0.8rem;
  font-family: inherit;
  font-size: 0.95rem;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  outline: none;
  border-color: var(--navy);
  box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.1);
}

/* ===== Buttons ===== */
.btn-navy, .btn-gold, .btn-success, .btn-danger, .btn-ghost, .btn-ghost-danger, .btn-sm {
  border: none;
  border-radius: var(--radius-sm);
  padding: 0.65rem 1.2rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-navy { background: var(--navy); color: var(--white); }
.btn-navy:hover { background: var(--navy-dark); }
.btn-gold { background: var(--gold); color: var(--navy); }
.btn-gold:hover { background: var(--gold-dark); }
.btn-success { background: var(--success); color: var(--white); }
.btn-success:hover { background: var(--success-dark); }
.btn-danger { background: var(--danger); color: var(--white); }
.btn-danger:hover { background: var(--danger-dark); }
.btn-ghost { background: var(--cream); color: var(--navy-mid); border: 1px solid var(--cream-dark); }
.btn-ghost:hover { background: var(--white); }
.btn-ghost-danger { background: transparent; color: var(--danger); border: none; font-weight: 600; }
.btn-ghost-danger:hover { color: var(--danger-dark); text-decoration: underline; }
.btn-sm { padding: 0.4rem 0.8rem; font-size: 0.8rem; }

/* ===== Success Banner ===== */
.success-banner {
  background: rgba(62, 158, 111, 0.12);
  border-left: 4px solid var(--success);
  border-radius: var(--radius-sm);
  padding: 1rem;
  margin-bottom: 1rem;
}
.success-banner__title { color: var(--success); font-weight: 700; margin-bottom: 0.5rem; }
.success-banner__text { color: var(--navy-mid); font-size: 0.9rem; margin-bottom: 0.5rem; }
.success-banner__code {
  display: block;
  background: var(--white);
  border: 2px solid var(--success);
  border-radius: var(--radius-sm);
  padding: 0.8rem;
  text-align: center;
  font-family: monospace;
  font-size: 1.3rem;
  color: var(--navy);
  margin-bottom: 1rem;
}
.success-banner__dismiss { align-self: flex-start; }

/* ===== Check-in Form ===== */
.checkin-form { display: grid; gap: 1rem; }
.checkin-form__submit { display: flex; justify-content: center; }

/* ===== Parking Block ===== */
.parking-block { background: var(--cream); border-radius: var(--radius-sm); padding: 0.75rem; margin-top: 0.5rem; }
.parking-block__select {
  width: 100%;
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-sm);
  padding: 0.5rem;
  margin-bottom: 0.5rem;
}
.parking-block__warning { color: var(--warning); font-size: 0.85rem; margin-bottom: 0.5rem; }
.parking-block__rate { color: var(--navy-mid); font-size: 0.85rem; font-weight: 600; }

/* ===== Ticket Row ===== */
.ticket-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid var(--cream-dark);
}
.ticket-row:last-child { border-bottom: none; }
.ticket-row__info { flex: 1; }
.ticket-row__guest { color: var(--slate); font-size: 0.9rem; }
.ticket-row__actions { display: flex; gap: 0.5rem; }

/* ===== Guest Hero ===== */
.guest-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-dark) 100%);
  border-radius: var(--radius-md);
  color: var(--white);
  margin-bottom: 1.5rem;
}
.guest-hero__room, .guest-hero__dates { display: flex; flex-direction: column; gap: 0.5rem; }
.guest-hero__label { font-size: 0.85rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.04em; }
.guest-hero__number { font-family: var(--font-display); font-size: 2.5rem; font-weight: 700; }
.guest-hero__type { font-size: 1rem; opacity: 0.95; }
.guest-hero__date { font-size: 1.1rem; font-weight: 600; }

/* ===== Account Grid ===== */
.account-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
.account-tile {
  background: var(--cream);
  border-radius: var(--radius-sm);
  padding: 1rem;
  border-left: 4px solid var(--slate);
}
.account-tile--success { border-left-color: var(--success); background: rgba(62, 158, 111, 0.08); }
.account-tile--warning { border-left-color: var(--warning); background: rgba(232, 150, 58, 0.08); }
.account-tile--danger { border-left-color: var(--danger); background: rgba(220, 53, 69, 0.08); }
.account-tile__label { display: block; font-size: 0.8rem; color: var(--slate); text-transform: uppercase; margin-bottom: 0.35rem; }
.account-tile__value { display: block; font-family: var(--font-display); font-size: 1.5rem; color: var(--navy); font-weight: 700; }
.account-footnote { font-size: 0.9rem; color: var(--slate); margin-top: 1rem; }

/* ===== Parking Sections ===== */
.parking-empty { text-align: center; padding: 1.5rem; }
.parking-empty p { color: var(--slate); margin-bottom: 1rem; }
.parking-assigned { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; padding: 1rem; background: var(--cream); border-radius: var(--radius-sm); }
.parking-assigned__label { display: block; font-size: 0.85rem; color: var(--slate); text-transform: uppercase; margin-bottom: 0.35rem; }
.parking-assigned__value { display: block; font-size: 1.2rem; color: var(--navy); font-weight: 700; }

/* ===== Express Grid ===== */
.express-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.express-btn {
  background: var(--white);
  border: 2px solid var(--cream-dark);
  border-radius: var(--radius-md);
  padding: 1.2rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: center;
}
.express-btn:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.express-btn--blue { border-color: var(--navy); color: var(--navy); }
.express-btn--blue:hover { background: rgba(30, 58, 95, 0.1); }
.express-btn--green { border-color: var(--success); color: var(--success); }
.express-btn--green:hover { background: rgba(62, 158, 111, 0.1); }

/* ===== Empty State ===== */
.empty-state { text-align: center; padding: 2rem; }
.empty-state__icon { font-size: 3rem; display: block; margin-bottom: 1rem; }
.empty-state p { color: var(--slate); }

/* ===== Info Text ===== */
.info-text { color: var(--slate); font-size: 0.9rem; margin-bottom: 1rem; }

/* ===== Required Indicator ===== */
.required { color: var(--danger); }
</style>