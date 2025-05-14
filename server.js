const express = require('express');
const mongoose = require('mongoose');
const User = require('./models/User');
const path = require('path');
const app = express();

// MongoDB connection - add database name 'maasaraswati'
mongoose.connect('mongodb://localhost:27017/maasaraswati')
.then(() => {
    console.log('✅ MongoDB connected successfully');
    console.log('📍 Database: maasaraswati');
})
.catch((err) => {
    console.error('❌ MongoDB connection error:', err.message);
    process.exit(1);
});

// CORS middleware for Live Server
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    
    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        res.sendStatus(200);
    } else {
        next();
    }
});

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('auth'));

// Signup endpoint
app.post('/api/signup', async (req, res) => {
    try {
        console.log('📝 Signup request received:', req.body);
        
        const { email, password, confirmPassword, firstName, lastName } = req.body;
        
        if (password !== confirmPassword) {
            return res.status(400).json({ error: 'Passwords do not match' });
        }
        
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ error: 'User already exists' });
        }
        
        const user = new User({
            email,
            password,
            name: `${firstName} ${lastName}`
        });
        
        await user.save();
        console.log('✅ User created:', email);
        
        res.json({ message: 'Account created successfully', redirect: '/login.html' });
    } catch (error) {
        console.error('❌ Signup error:', error);
        res.status(500).json({ error: 'Server error: ' + error.message });
    }
});

// Login endpoint
app.post('/api/login', async (req, res) => {
    try {
        console.log('🔐 Login request for:', req.body.email);
        
        const { email, password } = req.body;
        
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        
        const isValid = await user.comparePassword(password);
        if (!isValid) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        
        console.log('✅ Login successful:', email);
        res.json({ message: 'Login successful', redirect: '/dashboard.html' });
    } catch (error) {
        console.error('❌ Login error:', error);
        res.status(500).json({ error: 'Server error' });
    }
});

// Get all users
app.get('/api/users', async (req, res) => {
    try {
        const users = await User.find({}, { password: 0 });
        console.log('📋 Found users:', users.length);
        res.json(users);
    } catch (error) {
        res.status(500).json({ error: 'Server error' });
    }
});

// Serve main interface at root (after login)
app.get('/', (req, res) => {
    // Replace 'main-interface.html' with your actual main website file
    res.sendFile(path.join(__dirname, 'index.html')); // or main-interface.html
});

// Login page route
app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'auth', 'login.html'));
});

// Start server
app.listen(3000, () => {
    console.log('🚀 Server running on http://localhost:3000');
    console.log('🔗 MongoDB: mongodb://localhost:27017/maasaraswati');
}); 