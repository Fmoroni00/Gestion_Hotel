<template>
  <div class="recepcion-page">
    <!-- Header -->
    <header class="rec-header">
      <div class="header-left">
        <h1 class="rec-header__title">🏨 Panel de Recepción</h1>
        <p class="rec-header__subtitle">Gestión de Reservas y Servicios</p>
      </div>
      <button class="btn-ghost-light" @click="logout">🚪 Cerrar Sesión</button>
    </header>

    <!-- Estado de Carga -->
    <div v-if="cargando" class="state-screen">
      <p>⏳ Cargando datos...</p>
    </div>

    <!-- Contenido Principal -->
    <div v-else class="main-content">
      <div class="content-grid">
        <!-- COLUMNA 1: RESERVAS ACTIVAS -->
        <div class="card">
          <h2 class="card-title">📋 Reservas Activas</h2>
          
          <div v-if="reservasActivas.length === 0" class="empty-state">
            <p>✅ No hay reservas activas en este momento.</p>
          </div>

          <div v-else class="reservas-list">
            <div 
              v-for="reserva in reservasActivas" 
              :key="reserva.ID_Reserva"
              class="reserva-item"
              :class="{ 'reserva-item--selected': reservaSeleccionada?.ID_Reserva === reserva.ID_Reserva }"
              @click="seleccionarReserva(reserva)"
            >
              <div class="reserva-header">
                <span class="reserva-numero">Reserva #{{ String(reserva.ID_Reserva).padStart(6, '0') }}</span>
                <span class="badge badge--info">{{ reserva.estado }}</span>
              </div>
              <div class="reserva-detalles">
                <p><strong>Huésped:</strong> {{ reserva.huesped_nombre || 'Sin nombre' }}</p>
                <p><strong>Habitación:</strong> {{ reserva.numero_habitacion }}</p>
                <p v-if="reserva.amenidades && reserva.amenidades.length"><strong>Amenidades:</strong> {{ reserva.amenidades.join(', ') }}</p>
                <p><strong>Cochera:</strong> {{ reserva.numero_cochera ? `#${reserva.numero_cochera}` : 'No asignada' }}</p>
                <p><strong>Entrada:</strong> {{ formatearFechaCorta(reserva.fecha_entrada) }}</p>
              </div>
              <div class="reserva-monto">
                <span class="label">Total acumulado:</span>
                <span class="amount">S/. {{ (reserva.monto_total || 0).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- COLUMNA 2: DETALLES DE RESERVA SELECCIONADA -->
        <div v-if="reservaSeleccionada" class="card card--highlight">
          <h2 class="card-title">👤 Detalles de Reserva</h2>

          <div class="details-section">
            <div class="detail-box">
              <label>Reserva Nº</label>
              <span class="value">{{ String(reservaSeleccionada.ID_Reserva).padStart(6, '0') }}</span>
            </div>
            <div class="detail-box">
              <label>Huésped</label>
              <span class="value">{{ reservaSeleccionada.huesped_nombre || 'Sin asignar' }}</span>
            </div>
            <div class="detail-box">
              <label>Habitación</label>
              <span class="value">{{ reservaSeleccionada.numero_habitacion }}</span>
            </div>
            <div v-if="reservaSeleccionada.amenidades && reservaSeleccionada.amenidades.length" class="detail-box">
              <label>Amenidades</label>
              <span class="value">{{ reservaSeleccionada.amenidades.join(', ') }}</span>
            </div>
            <div class="detail-box">
              <label>Cochera</label>
              <span class="value">{{ reservaSeleccionada.numero_cochera ? `#${reservaSeleccionada.numero_cochera}` : 'No asignada' }}</span>
            </div>
            <div class="detail-box">
              <label>Check-in</label>
              <span class="value">{{ formatearFecha(reservaSeleccionada.fecha_entrada) }}</span>
            </div>
            <div class="detail-box">
              <label>Check-out</label>
              <span class="value">{{ formatearFecha(reservaSeleccionada.fecha_salida) }}</span>
            </div>
            <div class="detail-box">
              <label>Estado</label>
              <span class="value badge" :class="`badge--${reservaSeleccionada.estado}`">{{ reservaSeleccionada.estado }}</span>
            </div>
          </div>

          <!-- RESUMEN DE COBRO -->
          <div class="card card--inner">
            <h3 class="card-title--small">💰 Resumen de Cobro</h3>
            <div class="summary-items">
              <div class="summary-item">
                <span class="label">Alojamiento</span>
                <span class="amount">S/. {{ (reservaSeleccionada.monto_hospedaje || 0).toFixed(2) }}</span>
              </div>
              <div class="summary-item">
                <span class="label">Servicios Adicionales</span>
                <span class="amount">S/. {{ (reservaSeleccionada.monto_servicios || 0).toFixed(2) }}</span>
              </div>
              <div class="summary-item summary-item--total">
                <span class="label">Subtotal</span>
                <span class="amount">S/. {{ ((reservaSeleccionada.monto_hospedaje || 0) + (reservaSeleccionada.monto_servicios || 0)).toFixed(2) }}</span>
              </div>
              <div class="summary-item summary-item--igv">
                <span class="label">IGV (18%)</span>
                <span class="amount">S/. {{ (((reservaSeleccionada.monto_hospedaje || 0) + (reservaSeleccionada.monto_servicios || 0)) * 0.18).toFixed(2) }}</span>
              </div>
              <div class="summary-item summary-item--grand-total">
                <span class="label">TOTAL A COBRAR</span>
                <span class="amount">S/. {{ (((reservaSeleccionada.monto_hospedaje || 0) + (reservaSeleccionada.monto_servicios || 0)) * 1.18).toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <!-- CONSUMOS REGISTRADOS -->
          <div class="card card--inner" v-if="consumosSeleccionados.length > 0">
            <h3 class="card-title--small">📦 Consumos Registrados</h3>
            <div class="consumos-table--compact">
              <div class="table-header">
                <div class="col-servicio">Servicio</div>
                <div class="col-cantidad">Cant.</div>
                <div class="col-precio">Precio Unit.</div>
                <div class="col-total">Total</div>
              </div>
              <div v-for="consumo in consumosSeleccionados" :key="consumo.ID_Consumo" class="table-row">
                <div class="col-servicio">{{ consumo.nombre_servicio }}</div>
                <div class="col-cantidad">{{ consumo.cantidad }}</div>
                <div class="col-precio">S/. {{ (consumo.precio_unitario || 0).toFixed(2) }}</div>
                <div class="col-total">S/. {{ (consumo.subtotal || 0).toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <!-- NOTAS DE SERVICIO PENDIENTES -->
          <div class="card card--inner" v-if="notasServicioSeleccionadas.length > 0">
            <h3 class="card-title--small">🎫 Solicitudes de Servicio Pendientes</h3>
            <div class="notas-servicio-list">
              <div v-for="nota in notasServicioSeleccionadas" :key="nota.ID_Nota" class="nota-item" :class="`nota-${nota.estado}`">
                <div class="nota-header">
                  <span class="nota-servicio">{{ nota.nombre_servicio || `Servicio #${nota.ID_Servicio}` }}</span>
                  <span class="badge" :class="`badge--${nota.estado}`">{{ nota.estado }}</span>
                </div>
                <div class="nota-detalles">
                  <p v-if="nota.descripcion_servicio" class="nota-desc">{{ nota.descripcion_servicio }}</p>
                  <p v-if="nota.tipo_servicio" class="nota-tipo">{{ nota.tipo_servicio }}</p>
                  <p class="nota-fecha">{{ formatearFecha(nota.fecha_hora) }}</p>
                </div>
                <div class="nota-acciones" v-if="nota.estado === 'pendiente'">
                  <button class="btn-mini btn-success" @click="marcarComoPendiente(nota)">✅ Procesar</button>
                  <button class="btn-mini btn-danger" @click="marcarComoCancelado(nota)">❌ Rechazar</button>
                </div>
              </div>
            </div>
          </div>

          <!-- ACCIONES -->
          <div class="actions-section">
            <button class="btn-navy btn-medium" @click="imprimirBoleta">
              🖨️ Imprimir Boleta
            </button>
            <button class="btn-success btn-medium" @click="registrarPago">
              ✅ Registrar Pago
            </button>
            <button class="btn-warning btn-medium" @click="agregarConsumo">
              ➕ Agregar Consumo
            </button>
          </div>
        </div>

        <!-- COLUMNA 3: SERVICIOS DISPONIBLES -->
        <div class="card">
          <h2 class="card-title">⚡ Servicios Disponibles</h2>

          <div v-if="servicios.length === 0" class="empty-state">
            <p>📭 No hay servicios registrados.</p>
          </div>

          <div v-else class="servicios-list">
            <div v-for="servicio in servicios" :key="servicio.ID_Servicio" class="servicio-item">
              <div class="servicio-header">
                <span class="servicio-nombre">{{ servicio.nombre }}</span>
                <span class="badge" :class="`badge--${servicio.estado}`">{{ servicio.estado }}</span>
              </div>
              <p class="servicio-tipo">{{ servicio.tipo }}</p>
              <p v-if="servicio.descripcion" class="servicio-desc">{{ servicio.descripcion }}</p>
              <div class="servicio-precio">
                S/. {{ (servicio.precio_unitario || 0).toFixed(2) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para agregar consumo -->
    <div v-if="mostrarModalConsumo" class="modal-overlay" @click="mostrarModalConsumo = false">
      <div class="modal" @click.stop>
        <h2 class="modal-title">➕ Agregar Consumo a Reserva</h2>
        
        <div class="form-group">
          <label>Servicio</label>
          <select v-model="nuevoConsumo.ID_Servicio" class="form-control">
            <option value="">-- Seleccionar Servicio --</option>
            <option v-for="servicio in servicios" :key="servicio.ID_Servicio" :value="servicio.ID_Servicio">
              {{ servicio.nombre }} (S/. {{ (servicio.precio_unitario || 0).toFixed(2) }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Cantidad</label>
          <input v-model.number="nuevoConsumo.cantidad" type="number" min="1" class="form-control" placeholder="1">
        </div>

        <div class="modal-actions">
          <button class="btn-ghost" @click="mostrarModalConsumo = false">Cancelar</button>
          <button class="btn-success" @click="guardarConsumo">Agregar Consumo</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getReservas, getServicios, getPerfilHuesped, createServiceNote, getNotasServicioPorReserva, actualizarNotaServicio } from '@/services/api.js';

const router = useRouter();
const reservasActivas = ref([]);
const servicios = ref([]);
const reservaSeleccionada = ref(null);
const cargando = ref(true);
const mostrarModalConsumo = ref(false);
const nuevoConsumo = ref({
  ID_Servicio: '',
  cantidad: 1
});

const consumosSeleccionados = computed(() => {
  if (!reservaSeleccionada.value) return [];
  return reservaSeleccionada.value.consumos || [];
});

const notasServicioSeleccionadas = computed(() => {
  if (!reservaSeleccionada.value) return [];
  return reservaSeleccionada.value.notas_servicio || [];
});

async function cargarDatos() {
  try {
    const selectedReservaId = reservaSeleccionada.value?.ID_Reserva;

    // Cargar reservas activas
    const reservasData = await getReservas('activa');
    reservasActivas.value = Array.isArray(reservasData) ? reservasData : [];

    reservasActivas.value = reservasActivas.value.map(reserva => ({
      ...reserva,
      amenidades: Array.isArray(reserva.amenidades) ? reserva.amenidades : [],
    }));

    // Cargar cada reserva con detalles completos
    for (let i = 0; i < reservasActivas.value.length; i++) {
      try {
        const detalles = await getPerfilHuesped(reservasActivas.value[i].ID_Reserva);
        reservasActivas.value[i].monto_hospedaje = detalles.monto_hospedaje;
        reservasActivas.value[i].monto_servicios = detalles.monto_servicios;
        reservasActivas.value[i].monto_total = detalles.monto_total;
        reservasActivas.value[i].consumos = detalles.consumos || [];
        reservasActivas.value[i].numero_cochera = detalles.numero_cochera || null;
        
        // Cargar notas de servicio
        const notas = await getNotasServicioPorReserva(reservasActivas.value[i].ID_Reserva);
        reservasActivas.value[i].notas_servicio = Array.isArray(notas) ? notas : [];
      } catch (err) {
        console.warn(`Error cargando detalles de reserva ${reservasActivas.value[i].ID_Reserva}:`, err);
      }
    }

    // Reasignar reserva seleccionada si estaba activa
    if (selectedReservaId) {
      const actualizada = reservasActivas.value.find(r => r.ID_Reserva === selectedReservaId);
      if (actualizada) {
        reservaSeleccionada.value = actualizada;
      }
    }

    // Cargar servicios disponibles
    const serviciosData = await getServicios();
    servicios.value = Array.isArray(serviciosData) ? serviciosData : [];

    console.log('Datos cargados:', { reservasActivas: reservasActivas.value, servicios: servicios.value });
  } catch (error) {
    console.error('Error cargando datos:', error);
  } finally {
    cargando.value = false;
  }
}

function seleccionarReserva(reserva) {
  reservaSeleccionada.value = reserva;
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

function formatearFechaCorta(fecha) {
  if (!fecha) return '-';
  return new Date(fecha).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric'
  });
}

function imprimirBoleta() {
  if (!reservaSeleccionada.value) {
    alert('⚠️ Selecciona una reserva primero.');
    return;
  }

  const IGV_RATE = 0.18;
  const monto_hospedaje = reservaSeleccionada.value.monto_hospedaje || 0;
  const monto_servicios = reservaSeleccionada.value.monto_servicios || 0;
  const subtotal = monto_hospedaje + monto_servicios;
  const igv = subtotal * IGV_RATE;
  const total = subtotal + igv;

  let consumosHTML = '';
  if (reservaSeleccionada.value.consumos && reservaSeleccionada.value.consumos.length > 0) {
    consumosHTML = `
      <h3 style="margin-top: 30px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px;">Detalle de Servicios Adicionales</h3>
      <table style="width: 100%; margin-bottom: 20px;">
        <thead>
          <tr style="background-color: #f9fafb;">
            <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">Descripción</th>
            <th style="padding: 12px; text-align: center; border: 1px solid #e5e7eb;">Cantidad</th>
            <th style="padding: 12px; text-align: right; border: 1px solid #e5e7eb;">Precio Unit.</th>
            <th style="padding: 12px; text-align: right; border: 1px solid #e5e7eb;">Subtotal</th>
          </tr>
        </thead>
        <tbody>
    `;

    reservaSeleccionada.value.consumos.forEach(consumo => {
      const nombreServicio = consumo.nombre_servicio || `Servicio #${consumo.ID_Servicio}`;
      const descripcion = consumo.descripcion_servicio || '';
      const detalles = descripcion ? `<br/><small style="color: #6b7280;">${descripcion}</small>` : '';
      consumosHTML += `
        <tr>
          <td style="padding: 12px; border: 1px solid #e5e7eb;">${nombreServicio}${detalles}</td>
          <td style="padding: 12px; border: 1px solid #e5e7eb; text-align: center;">${consumo.cantidad}</td>
          <td style="padding: 12px; border: 1px solid #e5e7eb; text-align: right;">S/. ${(consumo.precio_unitario || 0).toFixed(2)}</td>
          <td style="padding: 12px; border: 1px solid #e5e7eb; text-align: right;">S/. ${(consumo.subtotal || 0).toFixed(2)}</td>
        </tr>
      `;
    });

    consumosHTML += `
        </tbody>
      </table>
    `;
  }

  const facturaHTML = `
    <html>
      <head>
        <title>Boleta de Facturación - Hotel PMS</title>
        <meta charset="UTF-8">
        <style>
          body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 40px; color: #1f2937; background: #f9fafb; }
          .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
          .header { text-align: center; border-bottom: 3px solid #4f46e5; padding-bottom: 20px; margin-bottom: 30px; }
          .header h1 { margin: 0 0 5px 0; color: #4f46e5; font-size: 28px; }
          .header p { margin: 5px 0; color: #6b7280; font-size: 14px; }
          .details { display: flex; justify-content: space-between; margin-bottom: 30px; font-size: 14px; }
          .details p { margin: 8px 0; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
          th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
          th { background-color: #f3f4f6; font-weight: 600; color: #374151; }
          .summary-section { margin-top: 30px; display: flex; justify-content: flex-end; }
          .summary-box { width: 300px; }
          .summary-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }
          .summary-row.total { border-top: 2px solid #4f46e5; border-bottom: 2px solid #4f46e5; font-weight: bold; font-size: 16px; padding: 15px 0; }
          .summary-row.igv { color: #ea580c; }
          .label { font-weight: 500; color: #374151; }
          .amount { text-align: right; color: #1f2937; }
          .amount.igv { color: #ea580c; }
          .footer { margin-top: 50px; text-align: center; color: #6b7280; font-size: 12px; border-top: 1px solid #e5e7eb; padding-top: 20px; }
          .footer p { margin: 5px 0; }
          h3 { margin-top: 30px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; }
          small { color: #6b7280; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🏨 BOLETA DE FACTURACIÓN</h1>
            <p>Hotel PMS - Comprobante de Pago</p>
          </div>

          <div class="details">
            <div>
              <p><strong>Reserva Nº:</strong> ${String(reservaSeleccionada.value.ID_Reserva).padStart(6, '0')}</p>
              <p><strong>Huésped:</strong> ${reservaSeleccionada.value.huesped_nombre || 'Sin asignar'}</p>
              <p><strong>Habitación:</strong> ${reservaSeleccionada.value.numero_habitacion}</p>
            </div>
            <div style="text-align: right;">
              <p><strong>Fecha Emisión:</strong> ${new Date().toLocaleDateString('es-ES')}</p>
              <p><strong>Hora:</strong> ${new Date().toLocaleTimeString('es-ES')}</p>
              <p><strong>RUC Hotel:</strong> 20123456789</p>
            </div>
          </div>

          <table>
            <thead>
              <tr>
                <th>Concepto</th>
                <th style="text-align: right;">Monto</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Alojamiento</strong></td>
                <td style="text-align: right;"><strong>S/. ${monto_hospedaje.toFixed(2)}</strong></td>
              </tr>
            </tbody>
          </table>

          ${consumosHTML}

          <div class="summary-section">
            <div class="summary-box">
              <div class="summary-row">
                <span class="label">Subtotal:</span>
                <span class="amount">S/. ${subtotal.toFixed(2)}</span>
              </div>
              <div class="summary-row igv">
                <span class="label">IGV (18%):</span>
                <span class="amount igv">S/. ${igv.toFixed(2)}</span>
              </div>
              <div class="summary-row total">
                <span class="label">TOTAL A COBRAR:</span>
                <span class="amount">S/. ${total.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div class="footer">
            <p style="font-weight: bold; color: #1f2937;">Forma de Pago: Contado</p>
            <p>Gracias por su preferencia en nuestro hotel.</p>
            <p>Hotel PMS © 2024 - Todos los derechos reservados</p>
          </div>
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

function registrarPago() {
  if (!reservaSeleccionada.value) {
    alert('⚠️ Selecciona una reserva primero.');
    return;
  }
  alert(`✅ Pago registrado para Reserva #${String(reservaSeleccionada.value.ID_Reserva).padStart(6, '0')}`);
  // TODO: Implementar endpoint para registrar pago
}

function agregarConsumo() {
  if (!reservaSeleccionada.value) {
    alert('⚠️ Selecciona una reserva primero.');
    return;
  }
  mostrarModalConsumo.value = true;
}

async function guardarConsumo() {
  if (!nuevoConsumo.value.ID_Servicio || !reservaSeleccionada.value) {
    alert('⚠️ Selecciona un servicio.');
    return;
  }

  try {
    await createServiceNote(reservaSeleccionada.value.ID_Reserva, nuevoConsumo.value.ID_Servicio);
    alert('✅ Consumo agregado exitosamente.');
    mostrarModalConsumo.value = false;
    nuevoConsumo.value = { ID_Servicio: '', cantidad: 1 };
    // Recargar datos
    await cargarDatos();
  } catch (error) {
    alert(`❌ Error: ${error.message}`);
  }
}

async function marcarComoPendiente(nota) {
  try {
    await actualizarNotaServicio(nota.ID_Nota, { estado: 'entregado' });
    alert('✅ Servicio marcado como entregado.');
    // Recargar datos
    await cargarDatos();
    if (reservaSeleccionada.value) {
      const notas = await getNotasServicioPorReserva(reservaSeleccionada.value.ID_Reserva);
      reservaSeleccionada.value.notas_servicio = Array.isArray(notas) ? notas : [];
    }
  } catch (error) {
    alert(`❌ Error: ${error.message}`);
  }
}

async function marcarComoCancelado(nota) {
  const motivo = prompt('Ingresa el motivo de cancelación:');
  if (!motivo) return;
  
  try {
    await actualizarNotaServicio(nota.ID_Nota, { estado: 'cancelado', motivo_cancelacion: motivo });
    alert('✅ Servicio cancelado.');
    // Recargar datos
    await cargarDatos();
    if (reservaSeleccionada.value) {
      const notas = await getNotasServicioPorReserva(reservaSeleccionada.value.ID_Reserva);
      reservaSeleccionada.value.notas_servicio = Array.isArray(notas) ? notas : [];
    }
  } catch (error) {
    alert(`❌ Error: ${error.message}`);
  }
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_type');
  router.push('/');
}

onMounted(() => {
  cargarDatos();
});
</script>

<style scoped>
* { box-sizing: border-box; }

:root {
  --navy: #1e3a8a;
  --navy-mid: #3b82f6;
  --indigo: #4f46e5;
  --cream: #fef9f3;
  --white: #ffffff;
  --text-dark: #1f2937;
  --text-light: #6b7280;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --orange: #ea580c;
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recepcion-page {
  min-height: 100vh;
  background: var(--cream);
}

/* Header */
.rec-header {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);
  color: var(--white);
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-md);
}

.header-left h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.rec-header__subtitle {
  margin: 5px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.btn-ghost-light {
  background: rgba(255, 255, 255, 0.2);
  color: var(--white);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-ghost-light:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Main Content */
.main-content {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 1.5rem;
}

.state-screen {
  text-align: center;
  padding: 100px 20px;
  font-size: 18px;
  color: var(--text-light);
}

/* Card */
.card {
  background: var(--white);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
}

.card--inner {
  background: #f9fafb;
  margin-top: 1rem;
  padding: 1rem;
}

.card--highlight {
  border: 2px solid var(--indigo);
}

.card-title {
  margin: 0 0 1rem 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-dark);
}

.card-title--small {
  margin: 0 0 0.75rem 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-dark);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-light);
  font-size: 14px;
}

/* Reservas List */
.reservas-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reserva-item {
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.reserva-item:hover {
  background: #e5e7eb;
  border-color: var(--indigo);
}

.reserva-item--selected {
  background: var(--indigo);
  border-color: var(--indigo);
  color: var(--white);
}

.reserva-item--selected .reserva-numero,
.reserva-item--selected .badge,
.reserva-item--selected p,
.reserva-item--selected .label,
.reserva-item--selected .amount {
  color: var(--white);
}

.reserva-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.reserva-numero {
  font-weight: 600;
  font-size: 14px;
}

.badge {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 3px;
  font-weight: 500;
  text-transform: uppercase;
}

.badge--info {
  background: #dbeafe;
  color: #1e40af;
}

.badge--activa {
  background: #dcfce7;
  color: #166534;
}

.reserva-detalles p {
  margin: 3px 0;
  font-size: 12px;
}

.reserva-monto {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
  font-weight: 600;
}

/* Details Section */
.details-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.detail-box {
  display: flex;
  flex-direction: column;
}

.detail-box label {
  font-size: 12px;
  color: var(--text-light);
  font-weight: 500;
  text-transform: uppercase;
  margin-bottom: 3px;
}

.detail-box .value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-dark);
}

/* Summary Items */
.summary-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
}

.summary-item.summary-item--total {
  border-top: 2px solid #e5e7eb;
  font-weight: 600;
  padding-top: 1rem;
}

.summary-item.summary-item--igv {
  color: var(--orange);
  font-weight: 500;
}

.summary-item.summary-item--grand-total {
  background: #f0f9ff;
  border: 2px solid var(--indigo);
  padding: 1rem;
  margin-top: 0.5rem;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 700;
}

.summary-item .label {
  font-weight: 500;
}

.summary-item .amount {
  text-align: right;
  font-weight: 600;
}

/* Consumos Table */
.consumos-table--compact {
  font-size: 12px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 0.5rem;
  background: #f3f4f6;
  padding: 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 0.5rem;
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  align-items: center;
}

.col-servicio, .col-cantidad, .col-precio, .col-total {
  text-align: left;
}

.col-cantidad, .col-precio, .col-total {
  text-align: right;
}

/* Servicios List */
.servicios-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.servicio-item {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 0.75rem;
  font-size: 12px;
}

.servicio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.servicio-nombre {
  font-weight: 600;
  color: var(--text-dark);
}

.servicio-tipo {
  color: var(--text-light);
  font-size: 11px;
  text-transform: uppercase;
  margin: 3px 0;
}

.servicio-desc {
  color: var(--text-light);
  margin: 3px 0;
  font-size: 11px;
}

.servicio-precio {
  color: var(--success);
  font-weight: 600;
  margin-top: 0.5rem;
}

/* Actions Section */
.actions-section {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  justify-content: flex-end;
}

.btn-navy, .btn-success, .btn-warning {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-navy {
  background: var(--navy);
  color: var(--white);
}

.btn-navy:hover {
  background: var(--navy-mid);
}

.btn-success {
  background: var(--success);
  color: var(--white);
}

.btn-success:hover {
  background: #059669;
}

.btn-warning {
  background: var(--warning);
  color: var(--white);
}

.btn-warning:hover {
  background: #d97706;
}

.btn-medium {
  padding: 0.6rem 1rem;
  font-size: 12px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--white);
  border-radius: 8px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
}

.modal-title {
  margin: 0 0 1.5rem 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-dark);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-dark);
  text-transform: uppercase;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: var(--indigo);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-ghost {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: var(--text-dark);
  padding: 0.75rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.btn-ghost:hover {
  background: #e5e7eb;
}

/* NOTAS DE SERVICIO */
.notas-servicio-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nota-item {
  padding: 12px;
  border-left: 4px solid #3b82f6;
  background: #f0f9ff;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.nota-item.nota-pendiente {
  border-left-color: #f59e0b;
  background: #fef3c7;
}

.nota-item.nota-entregado {
  border-left-color: #10b981;
  background: #ecfdf5;
}

.nota-item.nota-cancelado {
  border-left-color: #ef4444;
  background: #fee2e2;
}

.nota-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.nota-servicio {
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge--pendiente {
  background: #fef08a;
  color: #92400e;
}

.badge--entregado {
  background: #d1fae5;
  color: #065f46;
}

.badge--cancelado {
  background: #fee2e2;
  color: #7f1d1d;
}

.nota-detalles {
  font-size: 13px;
  color: #4b5563;
  margin-bottom: 8px;
}

.nota-desc {
  margin: 4px 0;
  font-style: italic;
}

.nota-tipo {
  margin: 4px 0;
  color: #6b7280;
}

.nota-fecha {
  margin: 4px 0;
  font-size: 11px;
  color: #9ca3af;
}

.nota-acciones {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-mini {
  padding: 6px 12px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
}

.btn-mini.btn-success {
  background: #10b981;
  color: white;
}

.btn-mini.btn-success:hover {
  background: #059669;
  transform: translateY(-1px);
}

.btn-mini.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-mini.btn-danger:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

/* Responsive */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .details-section {
    grid-template-columns: 1fr;
  }

  .main-content {
    padding: 1rem;
  }

  .rec-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>
