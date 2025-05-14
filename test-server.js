const express = require('express');
const bcrypt = require('bcryptjs');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static('auth'));

// In-memory users array (temporary)
const users = [];

app.post('/api/signup', async (req, res) => {
    const { email, password, confirmPassword, firstName, lastName } = req.body;
    
    if (password !== confirmPassword) {
        return res.status(400).json({ error: 'Passwords do not match' });
    }
    
    const hashedPassword = await bcrypt.hash(password, 10);
    users.push({
        email,
        password: hashedPassword,
        name: `${firstName} ${lastName}`,
        id: Date.now()
    });
    
    console.log('✅ User added:', email);
    console.log('📊 Total users:', users.length);
    
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

app.get('/api/users', (req, res) => {
    res.json(users.map(u => ({ email: u.email, name: u.name, id: u.id })));
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'auth', 'login.html'));
});

app.listen(3001, () => {
    console.log('🚀 Test server running on http://localhost:3001');
}); 