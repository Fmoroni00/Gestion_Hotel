<template>
  <div class="huesped-page">
    <!-- Header -->
    <header class="ph-header">
      <h1 class="ph-header__title">Hotel PMS · Portal del Huésped</h1>
      <button class="btn-ghost-light" @click="logout">🚪 Cerrar Sesión</button>
    </header>

    <!-- Estado de Carga -->
    <div v-if="cargando" class="state-screen">
      <p>⏳ Cargando tus datos del hotel...</p>
    </div>

    <!-- Estado de Error -->
    <div v-else-if="errorMsg" class="state-screen">
      <div class="error-card">
        <p class="error-card__title">❌ Error</p>
        <p class="error-card__text">{{ errorMsg }}</p>
        <button class="btn-navy" @click="logout">Volver al Login</button>
      </div>
    </div>

    <!-- Contenido Principal -->
    <div v-else class="main-content">
      <h2 class="main-content__title">Bienvenido a tu Estancia</h2>

      <!-- TARJETA 1: RESUMEN DE CUENTA -->
      <div class="card">
        <h3 class="card-title">💰 Resumen de Cuenta</h3>
        <div class="summary-grid">
          <div class="summary-box summary-box--success">
            <div class="summary-label">Alojamiento</div>
            <div class="summary-value summary-value--success">S/. {{ (datosHuesped.monto_hospedaje || 0).toFixed(2) }}</div>
          </div>
          <div class="summary-box summary-box--warning">
            <div class="summary-label">Servicios Adicionales</div>
            <div class="summary-value summary-value--warning">S/. {{ (datosHuesped.monto_servicios || 0).toFixed(2) }}</div>
          </div>
          <div class="summary-box summary-box--danger">
            <div class="summary-label">Total Acumulado</div>
            <div class="summary-value summary-value--danger">S/. {{ (datosHuesped.monto_total || 0).toFixed(2) }}</div>
          </div>
        </div>
        <div class="info-note">
          <p>ℹ️ El pago de tu factura será procesado en recepción al momento del check-out.</p>
        </div>
        <div v-if="estadiaFinalizada" class="invoice-action">
          <button class="btn-success btn-large" @click="descargarFactura()">📥 Descargar Factura / Boleta</button>
        </div>
      </div>

      <div v-if="estadiaFinalizada" class="card card--danger">
        <h3 class="card-title card-title--danger">🔒 Estancia Finalizada</h3>
        <p class="finished-text">Esta estadía ha finalizado. Los servicios están cerrados.</p>
      </div>

      <template v-else>
      <!-- TARJETA 2: CONTROL DE ESTACIONAMIENTO -->
      <div class="card">
        <h3 class="card-title">🚗 Control de Estacionamiento</h3>
        <div class="parking-section">
          <button
            class="btn-navy btn-large btn-full"
            @click="solicitarCochera()"
            :disabled="cocheraBotonDesactivado"
          >
            {{ cocheraBotonTexto }}
          </button>
        </div>
        <p class="card-info">Si ya tienes asignada una cochera, el número aparecerá aquí.</p>
      </div>

      <!-- TARJETA 3: SOLICITUDES DE SERVICIO -->
      <div class="card">
        <h3 class="card-title">⚡ Solicitudes de Servicio</h3>
        <p class="card-subtitle">Haz clic en cualquier servicio para solicitarlo inmediatamente</p>

        <div v-if="servicios.length === 0" class="empty-state">
          <p>📭 No hay servicios disponibles en este momento.</p>
        </div>

        <div v-else class="servicios-grid">
          <button
            v-for="servicio in servicios"
            :key="servicio.ID_Servicio"
            class="servicio-btn"
            @click="solicitarServicio(servicio)"
          >
            <div class="servicio-nombre">{{ servicio.nombre }}</div>
            <div class="servicio-precio">S/. {{ servicio.precio_unitario.toFixed(2) }}</div>
            <div class="servicio-accion">Solicitar →</div>
          </button>
        </div>
      </div>
      </template>

      <!-- CONSUMOS REALIZADOS -->
      <div v-if="datosHuesped.consumos && datosHuesped.consumos.length" class="card">
        <h3 class="card-title">📋 Consumos Registrados</h3>
        <div class="consumos-table">
          <div class="table-header">
            <div class="col-fecha">Fecha</div>
            <div class="col-servicio">Servicio</div>
            <div class="col-cantidad">Cantidad</div>
            <div class="col-subtotal">Subtotal</div>
          </div>
          <div v-for="consumo in datosHuesped.consumos" :key="consumo.ID_Consumo" class="table-row">
            <div class="col-fecha" data-label="Fecha: ">{{ formatearFecha(consumo.fecha) }}</div>
            <div class="col-servicio" data-label="Servicio: ">Servicio #{{ consumo.ID_Servicio }}</div>
            <div class="col-cantidad" data-label="Cantidad: ">{{ consumo.cantidad }}</div>
            <div class="col-subtotal" data-label="Subtotal: ">S/. {{ consumo.subtotal.toFixed(2) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getPerfilHuesped, getServiciosDisponibles, createServiceNote } from '@/services/api.js';

const router = useRouter();
const datosHuesped = ref({
  ID_Reserva: null,
  monto_hospedaje: 0,
  monto_servicios: 0,
  monto_total: 0,
  consumos: [],
  estado_reserva: '',
  estado_boleta: ''
});
const servicios = ref([]);
const cargando = ref(true);
const errorMsg = ref('');
const cocheraBotonTexto = ref('Solicitar Espacio de Cochera');
const cocheraBotonDesactivado = ref(false);

const estadiaFinalizada = computed(() => {
  return datosHuesped.value.estado_reserva === 'finalizada' || 
         datosHuesped.value.estado_reserva === 'cancelada' || 
         datosHuesped.value.estado_boleta === 'pagada';
});

async function cargarPerfil() {
  const idReserva = localStorage.getItem('id_reserva') || '1';

  if (!idReserva) {
    errorMsg.value = 'No se encontró el identificador de reserva. Inicia sesión nuevamente.';
    cargando.value = false;
    return;
  }

  try {
    const data = await getPerfilHuesped(idReserva);
    datosHuesped.value = {
      ID_Reserva: data.ID_Reserva || data.id_reserva || parseInt(idReserva),
      monto_hospedaje: data.monto_hospedaje || 0,
      monto_servicios: data.monto_servicios || 0,
      monto_total: data.monto_total || 0,
      consumos: data.consumos || [],
      estado_reserva: data.estado_reserva || '',
      estado_boleta: data.estado_boleta || ''
    };
  } catch (error) {
    errorMsg.value = error?.message || 'No se pudieron cargar los datos del huésped.';
  } finally {
    cargando.value = false;
  }
}

async function cargarServicios() {
  try {
    const data = await getServiciosDisponibles();
    servicios.value = Array.isArray(data) ? data : [];
    console.log('Servicios disponibles cargados:', servicios.value);
  } catch (error) {
    console.error('Error cargando servicios:', error);
    servicios.value = [];
  }
}

async function solicitarServicio(servicio) {
  if (!datosHuesped.value.ID_Reserva) {
    alert('⚠️ Error: No se pudo identificar tu reserva.');
    return;
  }

  try {
    await createServiceNote(datosHuesped.value.ID_Reserva, servicio.ID_Servicio);
    alert(`✅ Solicitud de "${servicio.nombre}" enviada. Pronto te atenderemos.`);
  } catch (error) {
    console.error('Error solicitando servicio:', error);
    alert(`❌ No se pudo registrar la solicitud de "${servicio.nombre}".`);
  }
}

async function solicitarCochera() {
  if (!datosHuesped.value.ID_Reserva) {
    alert('⚠️ Error: No se pudo identificar tu reserva.');
    return;
  }

  cocheraBotonDesactivado.value = true;
  cocheraBotonTexto.value = 'Enviando solicitud...';

  try {
    // Crear directamente la Nota de Servicio sin validación de ID_Servicio inexistente
    await createServiceNote(datosHuesped.value.ID_Reserva, null, {
      concepto: 'Solicitud de Cochera',
      descripcion: 'Solicitud de Cochera'
    });
    
    cocheraBotonTexto.value = 'Solicitud Enviada (En espera de asignación)';
    alert('✅ Solicitud de Cochera enviada directamente a recepción en tiempo real. El recepcionista te asignará un espacio en breve.');
  } catch (error) {
    console.error('Error solicitando cochera:', error);
    alert('❌ No se pudo registrar la solicitud de cochera.');
    cocheraBotonDesactivado.value = false;
    cocheraBotonTexto.value = 'Solicitar Espacio de Cochera';
  }
}

function formatearFecha(fecha) {
  if (!fecha) return '-';
  return new Date(fecha).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function descargarFactura() {
  const facturaHTML = `
    <html>
      <head>
        <title>Factura de Estadía - Hotel PMS</title>
        <style>
          body { font-family: 'Inter', sans-serif; padding: 40px; color: #1f2937; }
          .header { text-align: center; border-bottom: 2px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 30px; }
          .header h1 { margin: 0; color: #4f46e5; }
          .details { display: flex; justify-content: space-between; margin-bottom: 30px; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
          th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
          th { background-color: #f9fafb; font-weight: 600; }
          .total { text-align: right; font-size: 1.5rem; font-weight: bold; color: #111827; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>Hotel PMS</h1>
          <p>Factura Corporativa - Comprobante de Pago</p>
        </div>
        <div class="details">
          <div>
            <p><strong>Reserva #:</strong> ${datosHuesped.value.ID_Reserva}</p>
            <p><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</p>
          </div>
          <div style="text-align: right;">
            <p><strong>Estado:</strong> ${datosHuesped.value.estado_boleta ? datosHuesped.value.estado_boleta.toUpperCase() : 'GENERADA'}</p>
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Descripción</th>
              <th style="text-align: right;">Monto</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Servicio de Alojamiento</td>
              <td style="text-align: right;">S/. ${datosHuesped.value.monto_hospedaje.toFixed(2)}</td>
            </tr>
            <tr>
              <td>Servicios Adicionales (Consumos y Parking)</td>
              <td style="text-align: right;">S/. ${datosHuesped.value.monto_servicios.toFixed(2)}</td>
            </tr>
          </tbody>
        </table>
        <div class="total">
          Gran Total: S/. ${datosHuesped.value.monto_total.toFixed(2)}
        </div>
        <div style="margin-top: 50px; text-align: center; color: #6b7280; font-size: 0.9rem;">
          <p>Gracias por su preferencia.</p>
          <p>Hotel PMS - Todos los derechos reservados</p>
        </div>
      </body>
    </html>
  `;
  const printWindow = window.open('', '_blank');
  printWindow.document.write(facturaHTML);
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
  }, 250);
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_type');
  localStorage.removeItem('id_reserva');
  router.push('/');
}

onMounted(() => {
  cargarPerfil();
  cargarServicios();
});
</script>

<style scoped>
* { box-sizing: border-box; }

.huesped-page {
  min-height: 100vh;
  background: var(--cream);
}

/* Header */
.ph-header {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);
  color: var(--white);
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-md);
}
.ph-header__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--white);
}
.btn-ghost-light {
  padding: 0.65rem 1.3rem;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: var(--white);
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.92rem;
  transition: all 0.2s ease;
}
.btn-ghost-light:hover { background: rgba(255, 255, 255, 0.22); }

/* Estados */
.state-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  color: var(--slate);
  font-size: 1.05rem;
}
.error-card {
  background: var(--white);
  padding: 2rem;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  max-width: 460px;
  text-align: center;
}
.error-card__title { color: var(--danger); font-weight: 600; margin-bottom: 1rem; }
.error-card__text { color: var(--slate); margin-bottom: 1.5rem; }

/* Contenido */
.main-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
}
.main-content__title {
  font-family: var(--font-display);
  color: var(--navy);
  margin-bottom: 1.75rem;
}

/* Cards */
.card {
  background: var(--white);
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-md);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}
.card--danger { border-color: rgba(217, 79, 79, 0.3); background: rgba(217, 79, 79, 0.04); }
.card-title {
  margin: 0 0 1.25rem 0;
  font-family: var(--font-display);
  color: var(--navy);
  font-size: 1.25rem;
}
.card-title--danger { color: var(--danger); }
.card-subtitle { color: var(--slate); margin: 0 0 1.25rem 0; font-size: 0.92rem; }
.card-info {
  color: var(--slate);
  margin-top: 1rem;
  font-size: 0.88rem;
  padding: 0.75rem;
  background: var(--cream);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--navy-light);
}
.finished-text { color: var(--danger); font-size: 1.05rem; font-weight: 600; margin: 0; }

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}
.summary-box {
  padding: 1.25rem;
  border-radius: var(--radius-sm);
  background: var(--cream);
  border-left: 4px solid var(--slate);
}
.summary-box--success { border-left-color: var(--success); background: rgba(62, 158, 111, 0.07); }
.summary-box--warning { border-left-color: var(--warning); background: rgba(232, 150, 58, 0.07); }
.summary-box--danger { border-left-color: var(--danger); background: rgba(217, 79, 79, 0.07); }
.summary-label {
  font-size: 0.8rem;
  color: var(--slate);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.6rem;
  font-weight: 600;
}
.summary-value { font-family: var(--font-display); font-size: 1.85rem; font-weight: 600; }
.summary-value--success { color: var(--success); }
.summary-value--warning { color: var(--warning); }
.summary-value--danger { color: var(--danger); }

.info-note {
  background: rgba(42, 79, 127, 0.06);
  border-left: 4px solid var(--navy-light);
  padding: 0.9rem 1rem;
  border-radius: var(--radius-sm);
  color: var(--navy-mid);
  font-size: 0.9rem;
}
.info-note p { margin: 0; }

.invoice-action { margin-top: 1.5rem; text-align: center; }

/* Parking */
.parking-section { display: flex; flex-direction: column; gap: 1rem; }

/* Servicios */
.servicios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.25rem;
}
.servicio-btn {
  padding: 1.4rem;
  background: var(--white);
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  box-shadow: var(--shadow-sm);
}
.servicio-btn:hover {
  border-color: var(--gold);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}
.servicio-nombre { font-size: 1.05rem; font-weight: 600; color: var(--navy); margin-bottom: 0.4rem; }
.servicio-precio { font-family: var(--font-display); font-size: 1.4rem; color: var(--gold); margin-bottom: 0.85rem; }
.servicio-accion { font-size: 0.85rem; color: var(--navy-mid); opacity: 0.75; transition: all 0.2s; }
.servicio-btn:hover .servicio-accion { opacity: 1; color: var(--gold); transform: translateX(4px); }

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--slate);
  background: var(--cream);
  border: 1px dashed var(--cream-dark);
  border-radius: var(--radius-md);
}

/* Consumos Table */
.consumos-table {
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.table-header {
  background: var(--cream);
  display: grid;
  grid-template-columns: 150px 1fr 100px 150px;
  gap: 1rem;
  padding: 0.9rem 1rem;
  font-weight: 600;
  color: var(--navy-mid);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.table-row {
  display: grid;
  grid-template-columns: 150px 1fr 100px 150px;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-bottom: 1px solid var(--cream-dark);
  align-items: center;
}
.table-row:last-child { border-bottom: none; }
.table-row:hover { background: rgba(201, 168, 76, 0.06); }
.col-fecha, .col-servicio, .col-cantidad, .col-subtotal { color: var(--navy-mid); font-size: 0.92rem; }
.col-subtotal { font-weight: 600; color: var(--success); }

/* Botones */
.btn-navy, .btn-success {
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.18s ease;
}
.btn-navy { background: var(--navy); color: var(--white); padding: 0.7rem 1.4rem; }
.btn-navy:hover { background: var(--navy-light); }
.btn-navy:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-success { background: var(--success); color: var(--white); padding: 0.7rem 1.4rem; }
.btn-success:hover { opacity: 0.9; }
.btn-large { padding: 0.95rem 1.8rem; font-size: 1.02rem; }
.btn-full { width: 100%; }

/* Responsive */
@media (max-width: 768px) {
  .ph-header { flex-direction: column; gap: 1rem; text-align: center; }
  .ph-header__title { font-size: 1.3rem; }
  .main-content { padding: 1rem; }
  .summary-grid { grid-template-columns: 1fr; }
  .servicios-grid { grid-template-columns: 1fr; }

  .table-header, .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  .col-fecha, .col-servicio, .col-cantidad, .col-subtotal {
    display: flex;
    justify-content: space-between;
  }
  .col-fecha::before { content: attr(data-label); font-weight: 700; }
  .col-servicio::before { content: attr(data-label); font-weight: 700; }
  .col-cantidad::before { content: attr(data-label); font-weight: 700; }
  .col-subtotal::before { content: attr(data-label); font-weight: 700; }
}
</style>
