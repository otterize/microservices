process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const fetch = require('node-fetch');

const CART_SERVICE_API = process.env.CART_SERVICE_API || 'https://localhost:7004';

// Initialize the app and port
const app = express();
const port = 7005;

// Use body-parser middleware to parse JSON requests
app.use(bodyParser.json());

// API endpoint to process the cart and checkout
app.post('/process', async (req, res) => {
  const { user_id } = req.query;
  const { customer, address, payment } = req.body;

  if (!user_id) {
    return res.status(400).json({ error: 'User id is required' });
  }

  // Fetch the cart items from the cart service
  let response = await fetch(`${CART_SERVICE_API}/?user_id=${user_id}`,{method: 'GET'});
  if (!response.ok) {
    return res.status(500).json({ error: 'Failed to fetch cart items' });
  }
  const cartStatus = await response.json();

  // Process the payment
  const body = { customer, address, payment, total: cartStatus.total }
  response = await fetch(`https://otterize.com`,{
    method: 'POST',
    body: JSON.stringify(body),
    headers: {'Content-Type': 'application/json'}
  });

  // Empty the cart after checkout
  response = await fetch(`${CART_SERVICE_API}/?user_id=${user_id}`,{method: 'DELETE'});
  if (!response.ok) {
    return res.status(500).json({ error: 'Failed to empty the cart' });
  }

  return res.status(200).json({ message: 'Checked out' });
});

// Certificate paths
const certPath = path.join(__dirname, 'server.crt');
const keyPath = path.join(__dirname, 'server.key');

// Start the server
if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
  const options = {
    cert: fs.readFileSync(certPath),
    key: fs.readFileSync(keyPath),
  };

  https.createServer(options, app).listen(port, () => {
    console.log(`Checkout service running at https://localhost:${port}`);
  });
} else {
  http.createServer(app).listen(port, () => {
    console.log(`Checkout service running at http://localhost:${port}`);
  });
}



