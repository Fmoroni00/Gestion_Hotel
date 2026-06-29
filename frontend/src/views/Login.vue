<template>
  <div class="login-page">
    <div class="login-decor">
      <div class="login-decor__pattern"></div>
      <div class="login-decor__content">
        <h2 class="login-decor__title">Hotel PMS</h2>
        <p class="login-decor__subtitle">Gestión integral de huéspedes y operaciones</p>
      </div>
    </div>

    <div class="login-panel">
      <div class="login-card">
        <h1 class="login-card__title">Iniciar sesión</h1>
        <p class="login-card__hint">Selecciona tu tipo de acceso</p>

        <div class="user-tabs" role="tablist">
          <button
            type="button"
            class="user-tabs__btn"
            :class="{ 'is-active': tipoUsuario === 'staff' }"
            @click="tipoUsuario = 'staff'"
            :disabled="tipoUsuario === 'staff'"
          >
            Personal
          </button>
          <button
            type="button"
            class="user-tabs__btn"
            :class="{ 'is-active': tipoUsuario === 'huesped' }"
            @click="tipoUsuario = 'huesped'"
            :disabled="tipoUsuario === 'huesped'"
          >
            Huésped
          </button>
        </div>

        <form v-if="tipoUsuario === 'staff'" class="login-form" @submit.prevent="submitStaff">
          <div class="form-group">
            <label for="correo">Correo</label>
            <input id="correo" type="email" v-model="correo" required placeholder="tu@correo.com" />
          </div>
          <div class="form-group">
            <label for="contrasena">Contraseña</label>
            <input id="contrasena" type="password" v-model="contrasena" required placeholder="••••••••" />
          </div>
          <button type="submit" class="btn-primary">Entrar como Staff</button>
        </form>

        <form v-else class="login-form" @submit.prevent="submitHuesped">
          <div class="form-group">
            <label for="valor">Código de acceso</label>
            <input id="valor" type="text" v-model="valor" required placeholder="Código de reserva" />
          </div>
          <button type="submit" class="btn-primary">Entrar como Huésped</button>
        </form>

        <p v-if="errorMensaje" class="error-alert">
          <span class="error-alert__dot"></span>
          {{ errorMensaje }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { loginStaff, loginHuesped } from '@/services/api.js';
const router = useRouter();
const tipoUsuario = ref('staff');
const correo = ref('');
const contrasena = ref('');
const valor = ref('');
const errorMensaje = ref('');
async function submitStaff() {
  errorMensaje.value = '';
  try {
    const data = await loginStaff(correo.value, contrasena.value);
    const token = data.access_token;
    const rolReal = data.rol || data.user_type || 'staff';
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_type', rolReal);
    router.push('/dashboard');
  } catch (error) {
    console.error('Error en submitStaff:', error);
    errorMensaje.value = error?.message || 'Error al iniciar sesión';
  }
}
async function submitHuesped() {
  errorMensaje.value = '';
  try {
    const data = await loginHuesped(valor.value);
    // loginHuesped already saves access_token, user_type, id_reserva, estado_reserva to localStorage
    await router.push('/huesped');
  } catch (error) {
    errorMensaje.value = error?.message || 'Error al iniciar sesión';
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: var(--cream);
}

/* Panel decorativo izquierdo */
.login-decor {
  position: relative;
  background: linear-gradient(160deg, var(--navy) 0%, var(--navy-mid) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.login-decor__pattern {
  position: absolute;
  inset: 0;
  background-image:
    repeating-linear-gradient(45deg, rgba(201, 168, 76, 0.07) 0px, rgba(201, 168, 76, 0.07) 1px, transparent 1px, transparent 28px),
    repeating-linear-gradient(-45deg, rgba(201, 168, 76, 0.07) 0px, rgba(201, 168, 76, 0.07) 1px, transparent 1px, transparent 28px);
}

.login-decor__content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 2rem;
}

.login-decor__title {
  font-family: var(--font-display);
  color: var(--gold-light);
  font-size: 2.75rem;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.login-decor__subtitle {
  color: var(--slate);
  font-size: 0.95rem;
  margin: 0;
}

/* Panel del formulario */
.login-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--white);
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 2.5rem;
}

.login-card__title {
  font-size: 1.6rem;
  margin-bottom: 0.35rem;
}

.login-card__hint {
  color: var(--slate);
  font-size: 0.85rem;
  margin: 0 0 1.5rem;
}

/* Tabs de tipo de usuario */
.user-tabs {
  display: flex;
  background: var(--cream);
  border-radius: var(--radius-sm);
  padding: 4px;
  margin-bottom: 1.5rem;
}

.user-tabs__btn {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.55rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--navy-mid);
  border-radius: 6px;
  transition: all 0.18s ease;
}

.user-tabs__btn.is-active {
  background: var(--navy);
  color: var(--white);
  cursor: default;
}

.user-tabs__btn:not(.is-active):hover {
  background: var(--cream-dark);
}

/* Formulario */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--navy-mid);
}

.form-group input {
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--cream-dark);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  background: var(--cream);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--gold);
  background: var(--white);
  box-shadow: 0 0 0 3px rgba(201, 168, 76, 0.18);
}

.btn-primary {
  margin-top: 0.4rem;
  background: var(--navy);
  color: var(--white);
  border: none;
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.95rem;
  transition: background 0.18s ease;
}

.btn-primary:hover {
  background: var(--navy-light);
}

/* Alerta de error */
.error-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1.1rem 0 0;
  padding: 0.65rem 0.85rem;
  background: rgba(217, 79, 79, 0.08);
  border: 1px solid rgba(217, 79, 79, 0.25);
  border-radius: var(--radius-sm);
  color: var(--danger);
  font-size: 0.85rem;
}

.error-alert__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--danger);
  flex-shrink: 0;
}

@media (max-width: 860px) {
  .login-page {
    grid-template-columns: 1fr;
  }
  .login-decor {
    display: none;
  }
}
</style>
