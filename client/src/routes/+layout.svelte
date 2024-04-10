<script>
	import '../app.pcss';
	import Nav from '$lib/components/Nav.svelte';
	import Footer from '$lib/components/Footer.svelte';
</script>

<div>
	<Nav />

	<slot />
	<Footer />
</div>
