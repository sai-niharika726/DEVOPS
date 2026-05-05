const express = require('express');
const app = express();
const path = require('path');

app.set('view engine', 'ejs');
app.use(express.static('public'));

// Mock Data for the store
const gallery = [
  { id: 1, title: 'Mountains Silence', price: 450, img: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=400&q=80' },
  { id: 2, title: 'Urban Echo', price: 600, img: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=400&q=80' },
  { id: 3, title: 'Oceanick Blue', price: 550, img: 'https://images.unsplash.com/photo-1505118380757-91f5f45d8da8?auto=format&fit=crop&w=400&q=80' },
  { id: 4, title: 'Forest Path', price: 500, img: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=400&q=80' }
];

app.get('/', (req, res) => {
  res.render('index', { gallery });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Store running on http://localhost:${PORT}`));
