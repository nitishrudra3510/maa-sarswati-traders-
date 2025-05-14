const express = require('express');
const bcrypt = require('bcryptjs');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('auth'));

// Mock user database (replace with real database)
const users = [];

// Create default admin user on startup
const createDefaultUser = async () => {
    const hashedPassword = await bcrypt.hash('admin123', 10);
    users.push({
        email: 'admin@maasaraswati.com',
        password: hashedPassword,
        firstName: 'Admin',
        lastName: 'User'
    });
};
createDefaultUser();

app.post('/api/signup', async (req, res) => {
    const { email, password, confirmPassword, firstName, lastName } = req.body;
    
    // Check if passwords match
    if (password !== confirmPassword) {
        return res.status(400).json({ error: 'Passwords do not match' });
    }
    
    // Check if user already exists
    if (users.find(u => u.email === email)) {
        return res.status(400).json({ error: 'User already exists' });
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Add user to database
    users.push({
        email,
        password: hashedPassword,
        firstName,
        lastName
    });
    
    res.json({ message: 'Account created successfully', redirect: '/login.html' });
});

app.post('/api/login', async (req, res) => {
    const { email, password } = req.body;
    
    const user = users.find(u => u.email === email);
    if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    res.json({ message: 'Login successful', redirect: '/dashboard.html' });
});

// Route to serve login page at root
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'auth', 'login.html'));
});

app.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
    console.log('Default admin login: admin@maasaraswati.com / admin123');
}); 