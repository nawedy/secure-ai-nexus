<script lang="ts">
    import { onMount, onDestroy } from 'svelte'
    import { auth } from '$lib/stores/auth'

    let ws: WebSocket
    let systemStats: any = {
        cpu_usage: 0,
        memory_usage: 0,
        active_users: 0
    }

    let messages: string[] = []
    let connectionStatus = 'disconnected'

    function setupWebSocket() {
        const user = $auth
        if (!user) return

        ws = new WebSocket(`ws://localhost:8000/api/monitoring/ws/${user.id}`)

        ws.onopen = () => {
            connectionStatus = 'connected'
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                systemStats = data
            } catch (e) {
                messages = [...messages, event.data]
            }
        }

        ws.onclose = () => {
            connectionStatus = 'disconnected'
            setTimeout(setupWebSocket, 5000) // Attempt to reconnect
        }
    }

    onMount(() => {
        setupWebSocket()
    })

    onDestroy(() => {
        if (ws) ws.close()
    })
</script>

<div class="dashboard">
    <div class="status-bar">
        <div class="connection-status {connectionStatus}">
            {connectionStatus}
        </div>
    </div>

    <div class="stats-panel">
        <h2>System Statistics</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <h3>CPU Usage</h3>
                <p>{systemStats.cpu_usage}%</p>
            </div>
            <div class="stat-item">
                <h3>Memory Usage</h3>
                <p>{systemStats.memory_usage}%</p>
            </div>
            <div class="stat-item">
                <h3>Active Users</h3>
                <p>{systemStats.active_users}</p>
            </div>
        </div>
    </div>

    <div class="messages-panel">
        <h2>System Messages</h2>
        <div class="messages">
            {#each messages as message}
                <div class="message">{message}</div>
            {/each}
        </div>
    </div>
</div>

<style>
    .dashboard {
        padding: 1rem;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    .stat-item {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .connection-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
    }

    .connection-status.connected {
        background: #4CAF50;
        color: white;
    }

    .connection-status.disconnected {
        background: #f44336;
        color: white;
    }
</style>
