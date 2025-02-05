<script lang="ts">
  import { goto } from '$app/navigation'
  import { auth } from '$contexts/AuthContext';
  
  let email = ''
  let password = ''
  let confirmPassword = ''
  let error = ''
  let loading = false

  // Error messages
  let emailError = '';
  let passwordError = '';

    async function handleSubmit() {
      loading = true;
      error = '';
      emailError = '';
      passwordError = '';
  
    emailError = '';
    passwordError = '';

    // Form validation
    if (!email) {
        emailError = 'Email is required';
    } else if (!/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/.test(email)) {
        emailError = 'Invalid email format';
    }

    if (!password || password.length < 8) {
        passwordError = 'Password is required';
        if(password.length < 8){
          passwordError = 'Password must be at least 8 characters';
        }
    } else if (password !== confirmPassword) {
      passwordError = 'Passwords do not match';
    }

    if (emailError || passwordError) {
        loading = false;
        return;
    }

    try {
      const success = await $auth.signup(email, password);
      if(success){
        goto('/login');
      }
      else{
        error = $auth.error;
      }
    } catch (err) {
        error = 'An error occurred';
    } finally {
        loading = false;
    }
    

  }


</script>

<div class="form-container">
  <div class="form-wrapper">
    <h1>Sign Up</h1>
    {#if error}
      <div class="error">{error}</div>
    {/if}
    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" bind:value={email} required placeholder="example@email.com" class:input-error={emailError} />
        {#if emailError}
          <div class="error">{emailError}</div>
        {/if}
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" bind:value={password} required class:input-error={passwordError} />
      </div>
      <div class="form-group">
        <label for="confirm-password">Confirm Password</label>
        <input type="password" id="confirm-password" bind:value={confirmPassword} required class:input-error={passwordError} />
        {#if passwordError}
          <div class="error">{passwordError}</div>
        {/if}
      </div>
      <button type="submit" disabled={loading}>
        {#if loading}Loading...{:else}Register{/if}
      </button>
      <p>
        Already have an account?
        <a href="/login">Login</a>
      </p>
    </form>
  </div>
</div>

<style>
  .form-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f0f0f0;
  }

  .form-wrapper {
    background-color: #fff;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    width: 400px;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.25rem;
  }

  input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  .input-error{
    border-color: red;
  }
  .error {
    color: red;
    margin-bottom: 1rem;
  }
  button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  button:disabled {
    background-color: #ccc;
    cursor: default;
  }
  a {
    color: blue;
  }
</style>
