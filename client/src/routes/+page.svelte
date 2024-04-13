<script lang="ts">
	import { server_loads } from './../../.svelte-kit/generated/client/app.js';
	import { PUBLIC_WEB_SOCKET_URL } from '$env/static/public';
	import { onMount, onDestroy } from 'svelte';
	import { slide, fade } from 'svelte/transition';
	import Icon from '@iconify/svelte';

	let ws: WebSocket;

	type EndpointKey =
		| 'hostname'
		| 'os'
		| 'uptime'
		| 'memoryUsed'
		| 'memoryAvailable'
		| 'cpuUsage'
		| 'diskUsage'
		| 'systemLoad'
		| 'runningProcesses'
		| 'updates'
		| 'updatablePackages'
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
		systemLoad: '/api/load',
		runningProcesses: '/api/processes',
		updates: '/api/updates',
		updatablePackages: '/api/updatable-packages',
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
		systemLoad: null,
		runningProcesses: null,
		updates: null,
		updatablePackages: null,
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
			ws = new WebSocket(PUBLIC_WEB_SOCKET_URL);
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

	let showUpdates = false;

	const handleShowUpdates = () => {
		showUpdates = !showUpdates;
	};

	let upgradeCredentials: any;
	const handleSystemUpgrade = async () => {
		upgradeCredentials = prompt('Enter your password to upgrade the system');
		if (upgradeCredentials) {
			const res = await fetch('/api/update-system', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ password: upgradeCredentials })
			});

			if (res.ok) {
				alert('System upgrade initiated successfully');
			} else {
				alert('Failed to initiate system upgrade');
			}
		}
	};
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
				<div class="card bg-base-300 flex-1">
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

				<div class="card bg-base-300 flex-1">
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

				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>Uptime:</div>
						<div class="flex-1 text-sm font-extrabold sm:text-lg">
							{#if data.uptime === null}
								<div class="loading loading-spinner loading-md"></div>
							{:else}
								{data.uptime}
							{/if}
						</div>
					</div>
				</div>
			</div>

			<div class="flex flex-col gap-2 sm:my-5 md:flex-row">
				<div class="flex w-full gap-2">
					<div class="card bg-primary text-primary-content w-full flex-1">
						<div class="card-body h-full p-5">
							<div>Memory Used:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.memoryUsed === null}
									<div class="animate-pulse text-base sm:text-lg">Calculating Memory...</div>
								{:else}
									{data.memoryUsed}%
								{/if}
							</div>
						</div>
					</div>

					<div class="card bg-primary text-primary-content w-full flex-1">
						<div class="card-body h-full p-5">
							<div>Memory Available:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.memoryAvailable === null}
									<div class="animate m:text-lg text-base">Calculating Memory...</div>
								{:else}
									<div class="flex items-end gap-0">
										<div>
											{data.memoryAvailable}
										</div>
										<div class="text-sm">GB</div>
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>

				<div class="flex w-full gap-2">
					<div class="card bg-primary text-primary-content w-full flex-1">
						<div class="card-body h-full p-5">
							<div>CPU Usage:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.cpuUsage === null}
									<div class="animate-pulse text-base sm:text-lg">Calculating CPU usage...</div>
								{:else}
									{data.cpuUsage}%
								{/if}
							</div>
						</div>
					</div>

					<div class="card bg-primary text-primary-content w-full flex-1">
						<div class="card-body h-full p-5">
							<div>Disk Usage:</div>
							<div class="flex-1 text-3xl font-extrabold">
								{#if data.diskUsage === null}
									<div class="animate-pulse text-base sm:text-lg">Calculating disk usage...</div>
								{:else}
									{data.diskUsage}%
								{/if}
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="flex flex-col gap-2 sm:grid sm:grid-cols-2">
				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>Available Updates:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.updates === null}
								<div class="animate-pulse text-base sm:text-lg">
									Calculating available updates...
								</div>
							{:else}
								<div class="flex h-full flex-col justify-between gap-2">
									<div class="pb-2 text-5xl">
										{data.updates}
									</div>

									{#if data.updates > 0}
										<button on:click={handleShowUpdates} class="btn btn-primary w-full">
											{#if showUpdates}
												<div class="flex items-center gap-2">
													<div>Hide Updates</div>
													<div>
														<Icon icon="bi-chevron-up" class="h-4 w-4" />
													</div>
												</div>
											{:else}
												<div class="flex items-center gap-2">
													<div>Show Updates</div>

													<div>
														<Icon icon="bi-chevron-down" class="h-4 w-4" />
													</div>
												</div>
											{/if}
										</button>

										{#if showUpdates}
											<div transition:slide={{ delay: 0, duration: 100 }} class="text-sm">
												<ul class="pt-2">
													{#each data.updatablePackages as pkg}
														<li class="flex items-start gap-2">
															<Icon icon="bi-dash-lg" class="h-4 w-4" />
															<div class="font-medium">
																{pkg}
															</div>
														</li>
													{/each}
												</ul>
											</div>
										{/if}
									{/if}
								</div>
							{/if}
						</div>
					</div>
				</div>

				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>Network Usage:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.networkUsage === null}
								<div class="animate-pulse text-lg">Calculating network usage...</div>
							{:else}
								<div class="flex flex-col gap-2 text-2xl">
									<div>
										<div class="text-base font-thin lowercase">Received:</div>
										{data.networkUsage.received} MB
									</div>

									<div>
										<div class="text-base font-thin lowercase">Sent:</div>
										{data.networkUsage.sent} MB
									</div>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>Network Latency:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.networkLatency === null}
								<div class="flex items-center gap-2">
									<div class="animate-pulse text-base sm:text-lg">
										Pinging endpoints and averaging speed...
									</div>
								</div>
							{:else}
								{data.networkLatency}
							{/if}
						</div>
					</div>
				</div>

				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>Open Ports:</div>
						{#if data.networkPorts === null}
							<div class="loading loading-spinner loading-md"></div>
						{:else}
							<div class="flex flex-1 flex-col">
								{#each data.networkPorts as port}
									<div class="text-base font-extrabold sm:text-xl">{port}</div>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			</div>

			<div class="card bg-base-300 flex-1">
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

			<div class="card bg-base-300 flex-1">
				<div class="card-body h-full p-5">
					<div>Running Processes:</div>
					{#if data.runningProcesses == null}
						<div class="loading loading-spinner loading-md"></div>
					{:else}
						<table class="w-full table-auto">
							<thead>
								<tr>
									<th class="text-left text-lg">Name</th>
									<th class="text-left text-lg">User</th>
									<th class="text-left text-lg">Mem</th>
								</tr>
							</thead>
							<tbody>
								{#each data.runningProcesses.filter((process: { memory_percent: number; }) => process.memory_percent > 0).sort((a:any, b:any) => b.memory_percent - a.memory_percent) as process}
									<tr>
										<td class="text-lg font-thin">{process.name}</td>
										<td class="text-lg font-thin">{process.username}</td>
										<td class="text-lg font-thin">{process.memory_percent.toFixed(2)}%</td>
									</tr>
								{/each}
							</tbody>
						</table>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
