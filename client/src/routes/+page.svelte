<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { slide } from 'svelte/transition';

	let ws: WebSocket;

	type EndpointKey =
		| 'hostname'
		| 'os'
		| 'uptime'
		| 'memoryUsed'
		| 'memoryAvailable'
		| 'cpuUsage'
		| 'diskUsage'
		| 'updates'
		| 'networkUsage'
		| 'networkLatency'
		| 'networkPorts'
		| 'runningServices';

	const endpoints: Record<EndpointKey, string> = {
		hostname: '/api/hostname',
		os: '/api/os',
		uptime: '/api/uptime',
		memoryUsed: '/api/memory/used',
		memoryAvailable: '/api/memory/available',
		cpuUsage: '/api/cpu/usage',
		diskUsage: '/api/disk/usage',
		updates: '/api/updates',
		networkUsage: '/api/network/usage',
		networkLatency: '/api/network/latency',
		networkPorts: '/api/network/ports',
		runningServices: '/api/services/running'
	};

	let data: Record<EndpointKey, any> = {
		hostname: null,
		os: null,
		uptime: null,
		memoryUsed: null,
		memoryAvailable: null,
		cpuUsage: null,
		diskUsage: null,
		updates: null,
		networkUsage: null,
		networkLatency: null,
		networkPorts: null,
		runningServices: null
	};

	const fetchData = async (key: EndpointKey) => {
		const res = await fetch(endpoints[key]);
		data[key] = await res.json();
	};

	const fetchDataForAllKeys = () => {
		Object.keys(endpoints).forEach((key) => fetchData(key as EndpointKey));
	};

	onMount(() => {
		fetchDataForAllKeys(); // Initial fetch

		// Establish WebSocket connection after 5 seconds
		setTimeout(() => {
			ws = new WebSocket(`ws://45.56.88.245:6767/api/ws`);
			ws.onmessage = (event) => {
				const newData = JSON.parse(event.data);
				Object.keys(newData).forEach((key) => {
					data[key as keyof typeof data] = newData[key as keyof typeof newData];
				});
			};

			ws.onerror = (error) => {
				console.error('WebSocket error:', error);
			};

			ws.onclose = () => {
				console.log('WebSocket connection closed');
			};
		}, 5000); // 5-second delay
	});

	onDestroy(() => {
		if (ws) {
			ws.close();
		}
	});
</script>

{#if data.hostname === null}
	<div class="mx-auto min-h-screen max-w-5xl p-2 sm:p-5">
		<div role="alert" class="alert shadow-lg">
			<div class="loading loading-spinner loading-lg scale-125"></div>
			<div>
				<h3 class="text-2xl font-bold">Loading Server Data...</h3>
				<div class="text-sm">Establishing WebSocket connection to server.</div>
				<div class="animate-pulse pt-5 text-sm">This may take a few seconds...</div>
			</div>
		</div>
	</div>
{:else}
	<div class="mx-auto max-w-5xl">
		<div class="flex w-full flex-col gap-2 overflow-hidden p-2 sm:p-5">
			<div class="flex w-full flex-row gap-2 sm:flex-row">
				<div class="card flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Host:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.hostname === null}
								<div class="loading loading-spinner loading-md"></div>
							{:else}
								{data.hostname}
							{/if}
						</div>
					</div>
				</div>

				<div class="card flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>OS:</div>
						<div class="flex-1 text-sm font-extrabold sm:text-2xl">
							{#if data.os === null}
								<div class="loading loading-spinner loading-md"></div>
							{:else}
								{data.os}
							{/if}
						</div>
					</div>
				</div>

				<div class="card flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Uptime:</div>
						<div class="flex-1 text-sm font-extrabold sm:text-2xl">
							{#if data.uptime === null}
								<div class="loading loading-spinner loading-md"></div>
							{:else}
								{data.uptime}
							{/if}
						</div>
					</div>
				</div>
			</div>

			<div class="flex flex-col gap-2 sm:my-5 sm:flex-row">
				<div class="flex w-full gap-2">
					<div class="card w-full flex-1 bg-primary text-primary-content">
						<div class="card-body h-full p-5">
							<div>Memory Used:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.memoryUsed === null}
									<div class="animate-pulse text-lg">Calculating Memory...</div>
								{:else}
									{data.memoryUsed}
								{/if}
							</div>
						</div>
					</div>

					<div class="card w-full flex-1 bg-primary text-primary-content">
						<div class="card-body h-full p-5">
							<div>Memory Available:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.memoryAvailable === null}
									<div class="animate-pulse text-lg">Calculating Memory...</div>
								{:else}
									{data.memoryAvailable}
								{/if}
							</div>
						</div>
					</div>
				</div>

				<div class="flex w-full gap-2">
					<div class="card w-full flex-1 bg-primary text-primary-content">
						<div class="card-body h-full p-5">
							<div>CPU Usage:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.cpuUsage === null}
									<div class="animate-pulse text-lg">Calculating CPU usage...</div>
								{:else}
									{data.cpuUsage}
								{/if}
							</div>
						</div>
					</div>

					<div class="card w-full flex-1 bg-primary text-primary-content">
						<div class="card-body h-full p-5">
							<div>Disk Usage:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.diskUsage === null}
									<div class="animate-pulse text-lg">Calculating disk usage...</div>
								{:else}
									{data.diskUsage}
								{/if}
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="flex flex-col gap-2 sm:flex-row">
				<div class="card flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Available Updates:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.updates === null}
								<div class="animate-pulse sm:text-lg">Calculating available updates...</div>
							{:else}
								{data.updates}
							{/if}
						</div>
					</div>
				</div>

				<!-- <div class="card flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Network Usage:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.networkUsage === null}
								<div class="animate-pulse text-lg">Calculating network usage...</div>
							{:else}
								{data.networkUsage}
							{/if}
						</div>
					</div>
				</div> -->

				<div class="card flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Network Latency:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.networkLatency === null}
								<div class="flex items-center gap-2">
									<div class="animate-pulse sm:text-lg">
										Pinging endpoints and averaging speed...
									</div>
								</div>
							{:else}
								{data.networkLatency}
							{/if}
						</div>
					</div>
				</div>

				<div class="card flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Open Ports:</div>
						{#if data.networkPorts === null}
							<div class="loading loading-spinner loading-md"></div>
						{:else}
							<div class="flex flex-1 flex-col">
								{#each data.networkPorts as port}
									<div class="font-extrabold sm:text-xl">{port}</div>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			</div>

			<div class="card flex-1 bg-base-300">
				<div class="card-body h-full p-5">
					<div>Running Services:</div>
					{#if data.runningServices == null}
						<div class="loading loading-spinner loading-md"></div>
					{:else}
						<div class="grid grid-cols-1 sm:grid-cols-2">
							{#each data.runningServices as service}
								<div class="text-lg font-thin">{service}</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
