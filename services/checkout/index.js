process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const fetch = require('node-fetch');

const CART_SERVICE_API = process.env.NEWSLETTER_SERVICE_API || 'https://localhost:7003';

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
  const response = await fetch(`${CART_SERVICE_API}/?user_id=${user_id}`,{method: 'GET'});
  console.log(response);

  // try {
  //   // Create a new subscriber in the database
  //   await Subscriber.create({ email });
  //   return res.status(201).json({ message: 'Subscribed successfully' });
  // } catch (error) {
  //   if (error.name === 'SequelizeUniqueConstraintError') {
  //     return res.status(201).json({ message: 'Subscribed successfully' });
  //   }
  //   return res.status(500).json({ error: 'Failed to subscribe' });
  // }
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



