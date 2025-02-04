<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  let email = '';
  let error = '';
  let loading = false;
  let emailError = '';

  async function handleSubmit() {
    loading = true;
    error = '';
    emailError = '';

    // Simple form validation
    if (!email) {
        emailError = 'Email is required';
    } else if (!/^[w-.]+@([w-]+.)+[w-]{2,4}$/.test(email)) {
        emailError = 'Invalid email format';
    }
    if(emailError){
      loading = false;
      return
    }

    try {
      const response = await fetch('/api/auth/password-reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        
      } else {
        const data = await response.json();
        error = data.detail || 'password reset failed';
        if(Array.isArray(data.detail)){
            error = data.detail[0].msg;
        }
      }
    } catch (err) {
      error = 'An error occurred';
    } finally {
      loading = false;
    }
  }


</script>

<div class="container">
  <h1>Password reset</h1>
  {#if error}<div class="error">{error}</div>{/if}
  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="email">Email:</label>
      <input type="email" id="email" bind:value={email} required />
      {#if emailError}<div class="error">{emailError}</div>{/if}
    </div>
   
    <button type="submit" disabled={loading}>Send reset password link</button>
  </form>
</div>

<style>

</style>
