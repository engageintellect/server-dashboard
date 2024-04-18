<script lang="ts">
	import { server_loads } from './../../.svelte-kit/generated/client/app.js';
	import { PUBLIC_WEB_SOCKET_URL } from '$env/static/public';
	import { onMount, onDestroy } from 'svelte';
	import { slide, fade } from 'svelte/transition';
	import Icon from '@iconify/svelte';
	import robotImage from '$lib/assets/images/robot14-nobg.png';

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
		| 'packageCount'
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
		packageCount: '/api/package-count',
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
		packageCount: null,
		runningProcesses: null,
		updates: null,
		updatablePackages: [],
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
		console.log('UPTIME', data.uptime);

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
		}, 0); // 5-second delay
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

	function convertFloatToPercentage(floatNumber: number): string {
		return `${(floatNumber * 100).toFixed(2)}`;
	}
</script>

<svelte:head>
	<title>Server Dashboard</title>
</svelte:head>

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
						<div class="flex-1 text-3xl font-extrabold sm:text-5xl">
							{#if data.hostname === null}
								<div class="loading loading-spinner loading-md"></div>
							{:else}
								<div class="flex items-center gap-2">
									<div class="avatar online hidden lg:flex">
										<div class="bg-primary w-16 rounded-full">
											<img src={robotImage} alt="avatar" />
										</div>
									</div>

									<div>
										{data.hostname}
									</div>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>OS:</div>
						<div class="flex-1 text-sm font-extrabold sm:text-2xl">
							{#if data.os === null}
								<div class="animate-pulse text-base sm:text-lg">Calculating OS...</div>
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
								<div class="animate-pulse text-base sm:text-lg">Calculating Uptime...</div>
							{:else}
								<ul>
									{#each data.uptime as timeChunk}
										<li>
											{timeChunk}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
					</div>
				</div>
			</div>

			<div class="flex flex-col gap-2 sm:my-5 md:flex-row">
				<div class="flex w-full gap-2">
					<div class="card bg-primary text-primary-content w-full flex-1">
						<div class="card-body h-full p-5">
							<div class="flex items-center gap-2">
								<Icon icon="bi-memory" class="h-5 w-5" />
								<div>RAM Usage:</div>
							</div>
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
							<div class="flex items-center gap-2">
								<Icon icon="bi-memory" class="h-5 w-5" />
								<div>RAM Free:</div>
							</div>

							<div class="flex-1 text-3xl font-extrabold">
								{#if data.memoryAvailable === null}
									<div class="animate m:text-lg text-base">Calculating Memory...</div>
								{:else}
									<div class="flex items-end gap-1">
										<div>
											{data.memoryAvailable}
										</div>
										<div class="">GB</div>
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>

				<div class="flex w-full gap-2">
					<div class="card bg-primary text-primary-content w-full flex-1">
						<div class="card-body h-full p-5">
							<div class="flex items-center gap-2">
								<Icon icon="bi-cpu" class="h-5 w-5" />
								<div>CPU Usage</div>
							</div>

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
							<div class="flex items-center gap-2">
								<Icon icon="ph-hard-drives" class="h-5 w-5" />
								<div>Disk Usage</div>
							</div>

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
						<div>Installed Packages</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.packageCount === null}
								<div class="animate-pulse text-base sm:text-lg">Fetching package count...</div>
							{:else}
								<div class="flex h-full flex-col justify-between gap-2">
									<div class="pb-2 text-5xl">
										{data.packageCount}
									</div>
								</div>
							{/if}
						</div>

						<div>Available Updates:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{#if data.updates === null}
								<div class="animate-pulse text-base sm:text-lg">
									Checking for available updates...
								</div>
							{:else}
								<div class="flex h-full flex-col justify-between gap-2">
									<div class="pb-2 text-5xl">
										{data.updates}
									</div>

									{#if data.updates > 0 && data.updatablePackages.length > 0}
										<div class="bg-primary text-primary-content collapse-arrow collapse">
											<input
												transition:fade={{ delay: 0, duration: 500 }}
												type="checkbox"
												id="collapseCheckbox"
												class="toggle w-full"
												bind:checked={showUpdates}
											/>
											<div class="collapse-title text-lg font-medium">
												<label for="collapseCheckbox w-full">
													{#if showUpdates}
														<div class="flex items-center gap-2">
															<Icon
																icon={data.updates > 1 ? 'tabler-packages' : 'tabler-package'}
																class="h-7 w-7"
															/>

															<div>Hide Packages</div>
														</div>
													{:else}
														<div class="flex items-center gap-2">
															<Icon icon="tabler-package" class="h-7 w-7" />
															<div>Show Packages</div>
														</div>
													{/if}
												</label>
											</div>
											{#if showUpdates}
												<div class="collapse-content">
													<div transition:slide={{ delay: 0, duration: 100 }} class="text-sm">
														<ul class="">
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
												</div>
											{/if}
										</div>
									{/if}
								</div>
							{/if}
						</div>
					</div>
				</div>

				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>System Load:</div>

						<div>
							{#if data.systemLoad}
								<div class="flex flex-col gap-2">
									<div class="flex w-full justify-between">
										<div class="flex items-center gap-2">
											<div>CPU Cores:</div>
											<div class="badge badge-primary text-xl">{data.systemLoad.cpucore}</div>
										</div>
										<!-- <div class="">{data.systemLoad.cpucore}</div> -->
									</div>

									<div>
										<div class="flex w-full justify-between">
											<div class="">Min 1</div>
											<div class="">
												{convertFloatToPercentage(data.systemLoad.min1)}%
											</div>
										</div>

										{#if data.systemLoad.min1 > 0}
											{#if data.systemLoad.min1 > 1}
												<progress
													class="progress progress-error w-full"
													value={convertFloatToPercentage(data.systemLoad.min1)}
													max="100"
												/>
											{:else}
												<progress
													class="progress progress-primary w-full"
													value={convertFloatToPercentage(data.systemLoad.min1)}
													max="100"
												/>
											{/if}
										{:else}
											<progress class="progress w-full"></progress>
										{/if}
									</div>

									<div>
										<div class="flex w-full justify-between">
											<div class="">Min 5</div>
											<div class="">
												{convertFloatToPercentage(data.systemLoad.min5)}%
											</div>
										</div>

										{#if data.systemLoad.min5 > 0}
											{#if data.systemLoad.min5 > 1}
												<progress
													class="progress progress-error w-full"
													value={convertFloatToPercentage(data.systemLoad.min5)}
													max="100"
												/>
											{:else}
												<progress
													class="progress progress-primary w-full"
													value={convertFloatToPercentage(data.systemLoad.min5)}
													max="100"
												/>
											{/if}
										{:else}
											<progress class="progress w-full"></progress>
										{/if}
									</div>

									<div>
										<div class="flex w-full justify-between">
											<div class="">Min 15</div>
											<div class="">
												{convertFloatToPercentage(data.systemLoad.min15)}%
											</div>
										</div>

										{#if data.systemLoad.min15 > 0}
											{#if data.systemLoad.min15 > 1}
												<progress
													class="progress progress-error w-full"
													value={convertFloatToPercentage(data.systemLoad.min15)}
													max="100"
												/>
											{:else}
												<progress
													class="progress progress-primary w-full"
													value={convertFloatToPercentage(data.systemLoad.min15)}
													max="100"
												/>
											{/if}
										{:else}
											<progress class="progress w-full"></progress>
										{/if}
									</div>
								</div>
							{:else}
								<div class="animate-pulse text-lg">Calculating network usage...</div>
							{/if}
						</div>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-1 gap-2 md:grid-cols-3">
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
								<div class="text-3xl sm:text-5xl">
									{data.networkLatency}
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
										<div class="text-base font-thin lowercase">Sent:</div>

										<div class="flex items-center gap-2">
											<div class="text-primary-content bg-primary rounded-full text-4xl">
												<svg
													xmlns="http://www.w3.org/2000/svg"
													width="1.5rem"
													height="1.5rem"
													viewBox="0 0 24 24"
													{...$$props}
													><path
														fill="currentColor"
														d="M11 18V9.825L7.4 13.4L6 12l6-6l6 6l-1.4 1.4L13 9.825V18h-2Z"
													/></svg
												>
											</div>

											<div>
												{data.networkUsage.sent} MB
											</div>
										</div>
									</div>

									<div>
										<div class="text-base font-thin lowercase">Received:</div>

										<div class="flex items-center gap-2">
											<div class="text-primary-content bg-primary rounded-full text-4xl">
												<svg
													xmlns="http://www.w3.org/2000/svg"
													width="1.5rem"
													height="1.5rem"
													viewBox="0 0 24 24"
													{...$$props}
													><path
														fill="currentColor"
														d="m12 18l-6-6l1.4-1.4l3.6 3.575V6h2v8.175l3.6-3.575L18 12l-6 6Z"
													/></svg
												>
											</div>
											<div>
												{data.networkUsage.received} MB
											</div>
										</div>
									</div>
								</div>
							{/if}
						</div>
					</div>
				</div>

				<div class="card bg-base-300 flex-1">
					<div class="card-body h-full p-5">
						<div>Open Ports:</div>
						{#if data.networkPorts === null}
							<div class="animate-pulse text-lg">Averaging ping speed...</div>
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
						<!-- <div class="loading loading-spinner loading-md"></div> -->
						<div class="animate-pulse text-lg">Fetching running processes...</div>
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
						<table class=" w-full table-auto">
							<thead>
								<tr>
									<th class="text-left text-base">Name</th>
									<th class="text-left text-base">User</th>
									<th class="text-left text-base">Mem</th>
								</tr>
							</thead>
							<tbody>
								{#each data.runningProcesses.filter((process: { memory_percent: number; }) => process.memory_percent > 0).sort((a:any, b:any) => b.memory_percent - a.memory_percent) as process}
									<tr>
										<td class="text-base font-thin">{process.name}</td>
										<td class="text-base font-thin">{process.username}</td>
										<td class="text-base font-thin">{process.memory_percent.toFixed(2)}%</td>
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
