const fetch = require('node-fetch');

module.exports = async (req, res) => {
  const apiUrl = `http://152.42.208.53/api${req.url}`;
  
  try {
    const response = await fetch(apiUrl, {
      method: req.method,
      headers: {
        ...req.headers,
        host: '152.42.208.53', // Set the host header to the target API
      },
      body: req.method === 'POST' ? req.body : undefined,
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch data' });
  }
};
