import { Router } from 'express';
import { getPartsByArticle } from '../../usecases/getPartsByArticle.js';
export const partsRouter = Router();
partsRouter.get('/', async (req, res) => {
    const article = (req.query.article || '').trim();
    if (!article) {
        return res.status(400).json({ error: 'Missing query parameter: article' });
    }
    try {
        const result = await getPartsByArticle(article);
        res.json(result);
    }
    catch (error) {
        res.status(502).json({ error: error?.message || 'Failed to fetch parts' });
    }
});
//# sourceMappingURL=parts.router.js.map