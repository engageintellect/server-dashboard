<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	type EndpointKey =
		| 'hostname'
		| 'os'
		| 'uptime'
		| 'memoryUsed'
		| 'memoryAvailable'
		| 'cpuUsage'
		| 'diskUsage'
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
		const interval = setInterval(fetchDataForAllKeys, 5000); // Fetch every 5 seconds
		return () => clearInterval(interval); // Cleanup on component destroy
	});
</script>

<div class="mx-auto max-w-5xl">
	<div class="flex w-full flex-col gap-2 overflow-hidden p-2 sm:p-5">
		<div class="flex w-full flex-row gap-2 sm:flex-row">
			<div class="card flex-1 bg-base-300">
				<div class="card-body h-full p-5">
					<div>Host:</div>
					<div class="flex-1 text-3xl font-extrabold">
						{data.hostname}
					</div>
				</div>
			</div>

			<div class="card flex-1 bg-base-300">
				<div class="card-body h-full p-5">
					<div>OS:</div>
					<div class="flex-1 text-sm font-extrabold sm:text-2xl">
						{data.os}
					</div>
				</div>
			</div>

			<div class="card flex-1 bg-base-300">
				<div class="card-body h-full p-5">
					<div>Uptime:</div>
					<div class="flex-1 text-sm font-extrabold sm:text-2xl">
						{data.uptime}
					</div>
				</div>
			</div>
		</div>

		<div class="flex flex-col gap-2 sm:flex-row">
			<div class="flex w-full gap-2">
				<div class="card w-full flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Memory Used:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{data.memoryUsed}
						</div>
					</div>
				</div>

				<div class="card w-full flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Memory Available:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{data.memoryAvailable}
						</div>
					</div>
				</div>
			</div>

			<div class="flex w-full gap-2">
				<div class="card w-full flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>CPU Usage:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{data.cpuUsage}
						</div>
					</div>
				</div>

				<div class="card w-full flex-1 bg-base-300">
					<div class="card-body h-full p-5">
						<div>Disk Usage:</div>
						<div class="flex-1 text-3xl font-extrabold">
							{data.diskUsage}
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="flex flex-col gap-2 sm:flex-row">
			<div class="card flex-1 bg-base-300">
				<div class="card-body h-full p-5">
					<div>Network Usage:</div>
					<div class="flex-1 text-3xl font-extrabold">
						{data.networkUsage}
					</div>
				</div>
			</div>

			<div class="card flex-1 bg-base-300">
				<div class="card-body h-full p-5">
					<div>Network Latency:</div>
					<div class="flex-1 text-3xl font-extrabold">
						{data.networkLatency}
					</div>
				</div>
			</div>

			<div class="card flex-1 bg-base-300">
				<div class="card-body h-full p-5">
					<div>Open Ports:</div>
					{#if data.networkPorts}
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
				{#if data.runningServices}
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
