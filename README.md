# create-svelte

## Description

A simple server dashboard that displays the CPU and memory usage of the server it is running on. The server is written in Python and the client is written in Svelte.

## Getting Started

### Running the server

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x main.py
./main.py
```

### Running the client

```bash
# create a new project in the current directory
cd client
pnpm i && pnpm run dev --host
```

## Building the client

To create a production version of your app:

```bash
pnpm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://kit.svelte.dev/docs/adapters) for your target environment.
