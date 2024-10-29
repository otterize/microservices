const fs = require('fs');
const http = require('http');
const https = require('https');
const path = require('path');
const express = require('express');
const fetch = require('node-fetch');
const bodyParser = require('body-parser');
const { Sequelize, DataTypes } = require('sequelize');

const DB_NAME = process.env.DB_NAME || 'otterside';
const DB_SERVICE_HOST = process.env.DB_SERVICE_HOST || 'localhost';
const DB_SERVICE_USER = process.env.DB_SERVICE_USER || 'postgres';
const DB_SERVICE_PASSWORD = process.env.DB_SERVICE_PASSWORD || 'password';


// Initialize the app and port
const app = express();
const port = 7003;

// Use body-parser middleware to parse JSON requests
app.use(bodyParser.json());

// Set up Sequelize to connect to PostgreSQL
const sequelize = new Sequelize(DB_NAME, DB_SERVICE_USER, DB_SERVICE_PASSWORD, {
  host: DB_SERVICE_HOST,
  port: 5432,
  dialect: 'postgres'
});

// Define the Subscriber model
const Subscriber = sequelize.define('Subscriber', {
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: {
      isEmail: true
    }
  }
}, {
  tableName: 'subscribers',
  timestamps: false
});

// Sync Sequelize with the database (creates table if it doesn't exist)
sequelize.sync().then(() => {
  console.log('Database synced');
});

// API endpoint to add a new email to the newsletter
app.post('/subscribe', async (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  console.log(`Subscribing ${email}`)

  try {
    // Create a new subscriber in the database
    await Subscriber.create({ email });

    // Mock sending email
    await fetch(`https://otterize.com`,{
      method: 'POST',
      body: JSON.stringify({ email }),
      headers: {'Content-Type': 'application/json'}
    });

    return res.status(201).json({ message: 'Subscribed successfully' });
  } catch (error) {
    if (error.name === 'SequelizeUniqueConstraintError') {
      return res.status(201).json({ message: 'Subscribed successfully' });
    }
    return res.status(500).json({ error: 'Failed to subscribe' });
  }
});

// Certificate paths
const certPath = path.join(__dirname, 'server.crt');
const keyPath = path.join(__dirname, 'server.key');
console.log(certPath);

// Start the server
if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
  const options = {
    cert: fs.readFileSync(certPath),
    key: fs.readFileSync(keyPath),
  };

  https.createServer(options, app).listen(port, () => {
    console.log(`Newsletter service running at https://localhost:${port}`);
  });
} else {
  http.createServer(app).listen(port, () => {
    console.log(`Newsletter service running at http://localhost:${port}`);
  });
}



