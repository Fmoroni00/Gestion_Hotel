const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function _handleResponse(response) {
  const contentType = response.headers.get("Content-Type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    let errorMessage = "Error en la solicitud";
    
    if (data?.detail) {
      // Si FastAPI devuelve un arreglo de errores de validación (422), los unificamos
      if (Array.isArray(data.detail)) {
        errorMessage = data.detail.map(err => err.msg).join(", ");
      } else {
        errorMessage = data.detail;
      }
    } else if (data?.message) {
      errorMessage = data.message;
    } else if (response.statusText) {
      errorMessage = response.statusText;
    }
    
    throw new Error(errorMessage);
  }

  return data;
}

export async function loginStaff(correo, contrasena) {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login-staff`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify({ correo, contrasena }),
  });

  const data = await _handleResponse(response);
  
  if (data?.access_token) {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_type", data.rol || data.user_type);
  }
  
  return data;
}

export async function getPerfilHuesped(idReserva) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${BASE_URL}/api/v1/facturacion/reservas/${idReserva}/estado-cuenta`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  return await _handleResponse(response);
}

export async function loginHuesped(valor) {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login-huesped`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: JSON.stringify({ valor }),
  });

  const data = await _handleResponse(response);
  
  if (data?.access_token) {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_type", data.user_type);
    if (data.ID_Reserva) {
      localStorage.setItem("id_reserva", String(data.ID_Reserva));
    }
    if (data.estado_reserva) {
      localStorage.setItem("estado_reserva", data.estado_reserva);
    }
  }
  
  return data;
}

export async function getEstadiaHuesped() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/huespedes/estadia`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function getHabitaciones() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/habitaciones/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  return await _handleResponse(response)
}

export async function actualizarEstadoHabitacion(idHabitacion, estado) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/habitaciones/${idHabitacion}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ estado }),
  })

  return await _handleResponse(response)
}

export async function getEmpleados() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/usuarios`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function getPagos() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/boletas`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function getConfiguracion() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/configuracion`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function actualizarConfiguracion(config) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/configuracion`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(config),
  })
  return await _handleResponse(response)
}

export async function getServicios() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/servicios`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  return await _handleResponse(response)
}

export async function createServiceNote(idReserva, idServicio, extraData = {}) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/notas-servicio/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      ID_Reserva: idReserva,
      ID_Servicio: idServicio,
      estado: 'pendiente',
      ...extraData
    }),
  })
  return await _handleResponse(response)
}

export async function getNotasServicio() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/notas-servicio/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function getNotasServicioPorReserva(idReserva) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/notas-servicio/reserva/${idReserva}`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function actualizarNotaServicio(idNota, payload) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/notas-servicio/${idNota}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })
  return await _handleResponse(response)
}

export async function getServiciosDisponibles() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/servicios-disponibles`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function getParkings() {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/parking/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function getHuesped(dni) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/huespedes/${dni}`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  if (response.status === 404) {
    return null
  }
  return await _handleResponse(response)
}

export async function createHuesped(huesped) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/huespedes/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(huesped),
  })
  return await _handleResponse(response)
}

export async function createReserva(reserva) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/reservas/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(reserva),
  })
  return await _handleResponse(response)
}

export async function createCodigoAcceso(codigo) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/codigos-acceso/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(codigo),
  })
  return await _handleResponse(response)
}

// NUEVAS FUNCIONES: getReservas y actualizarEstadoReserva
export async function getReservas(estado = null) {
  const token = localStorage.getItem('access_token')
  const query = estado ? `?estado=${encodeURIComponent(estado)}&limit=100` : '?limit=100'
  const response = await fetch(`${BASE_URL}/api/v1/reservas/${query}`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}

export async function actualizarEstadoReserva(idReserva, estado) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`${BASE_URL}/api/v1/reservas/${idReserva}/estado?estado=${encodeURIComponent(estado)}`, {
    method: 'PUT',
    headers: {
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  return await _handleResponse(response)
}
