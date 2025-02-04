<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  let error = '';

  onMount(async () => {
    // Check if the user is authenticated
    const token = document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1];

    if (!token) {
      goto('/login');
      return;
    }

    try{
        const response = await fetch('/api/monitoring', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        }
        });

        if (response.ok) {
        const data = await response.json();
        // Handle the data 
        } else {
        goto('/login');
        }

    } catch(err){
        goto('/login');
    }


  });


function logout() {
  document.cookie = `token=; path=/; max-age=0`;
  goto('/login')
}
</script>

<div class="container">
  <h1>Dashboard</h1>
  {#if error}<div class="error">{error}</div>{/if}
  <p>Welcome to the dashboard!</p>
  <button on:click={logout}>Logout</button>
</div>

<style>

</style>
