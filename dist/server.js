import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { partsRouter } from './transport/http/parts.router.js';
dotenv.config();
const app = express();
const port = Number(process.env.PORT || 3000);
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));
app.use('/api/parts', partsRouter);
// serve static frontend
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.join(__dirname, '..', 'public');
app.use(express.static(publicDir));
app.get('/', (_req, res) => {
    res.sendFile(path.join(publicDir, 'index.html'));
});
app.use((err, _req, res, _next) => {
    console.error(err);
    res.status(500).json({ error: 'Internal Server Error' });
});
app.listen(port, () => {
    console.log(`Server listening on http://localhost:${port}`);
});
//# sourceMappingURL=server.js.map