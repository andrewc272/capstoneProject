require('dotenv').config();

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { OpenAI } = require('openai');


const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static('public'));

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

io.on('connection', (socket) => {
  console.log('A user connected');

  socket.on('chat message', async (msg) => {
    io.emit('chat message', msg);

    const trimmedMsg = msg.trim();

    if (trimmedMsg.startsWith('@bot')) {
    const prompt = trimmedMsg.replace(/@bot/i, '').trim();

    try {
      const response = await openai.chat.completions.create({
        model: 'gpt-4o',
        messages: [{role: 'user', content: prompt}],
      });

      const aiReply = `🤖 Bot: ${response.choices[0].message.content}`;
      io.emit('chat message', aiReply);
    } catch (err) {
      console.error('Error communicating with OpenAI:', err.message);
      io.emit('chat message', '🤖 Bot: Sorry, I am having trouble responding right now.');
    }
    }
  });


  socket.on('disconnect', () => {
    console.log('User disconnected');
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
