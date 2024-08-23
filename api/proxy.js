const fetch = require('node-fetch');

export default async function handler(req, res) {
    const { method, body, query } = req;

    const targetUrl = `http://152.42.208.53/`;

    const response = await fetch(targetUrl, {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...req.headers,
        },
        body: method === 'GET' ? undefined : JSON.stringify(body),
    });

    const data = await response.json();

    res.status(response.status).json(data);
}
