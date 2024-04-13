import { SERVER_ENDPOINT } from '$env/static/private';
import type { RequestHandler } from './$types';

// This assumes you have some method of validating the password
const isPasswordCorrect = (password: string) => {
    const systemPassword = 'hi';  // Replace with actual password check
    return password === systemPassword;
};

export const GET: RequestHandler = async ({ request }) => {
    const requestBody = await request.json();
    if (isPasswordCorrect(requestBody.password)) {
        const res = await fetch(`${SERVER_ENDPOINT}/api/update-system/`);
        const data = await res.json();
        if (!res.ok) {
            return new Response(JSON.stringify({ message: 'Failed to initiate system upgrade' }), {
                status: res.status,
                headers: { 'content-type': 'application/json' }
            });
        } else {
            return new Response(JSON.stringify(data), {
                headers: { 'content-type': 'application/json' }
            });
        }
    } else {
        return new Response(JSON.stringify({ message: 'Invalid password' }), {
            status: 401,
            headers: { 'content-type': 'application/json' }
        });
    }
};
