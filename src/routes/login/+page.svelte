<script lang="ts">
  import { enhance } from '$app/forms'
  import { auth } from '$lib/stores/auth'

  let email = ''
  let password = ''
  let loading = false

  async function handleLogin() {
    loading = true
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await response.json()
      if (response.ok) {
        auth.set(data)
        goto('/dashboard')
      }
    } catch (error) {
      console.error('Login failed:', error)
    }
    loading = false
  }
</script>

<div class="login-container">
  <form on:submit|preventDefault={handleLogin}>
    <h1>Login</h1>
    <div class="form-group">
      <label for="email">Email</label>
      <input
        type="email"
        id="email"
        bind:value={email}
        required
      />
    </div>
    <div class="form-group">
      <label for="password">Password</label>
      <input
        type="password"
        id="password"
        bind:value={password}
        required
      />
    </div>
    <button type="submit" disabled={loading}>
      {loading ? 'Loading...' : 'Login'}
    </button>
  </form>
</div>
