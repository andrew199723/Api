import axios from 'axios';
export class HttpPartsProvider {
    baseUrl;
    apiKey;
    constructor() {
        this.baseUrl = process.env.API_BASE_URL || '';
        this.apiKey = process.env.API_KEY || undefined;
        if (!this.baseUrl) {
            throw new Error('API_BASE_URL is required for http provider');
        }
    }
    async searchByArticle(article) {
        const url = new URL('/search', this.baseUrl);
        url.searchParams.set('article', article);
        if (this.apiKey)
            url.searchParams.set('api_key', this.apiKey);
        const response = await axios.get(url.toString(), { timeout: 10000 });
        const raw = (response.data?.items || response.data?.results || []);
        const items = raw.map((row) => ({
            article: row.article || row.sku || row.partNumber || '',
            name: row.name || row.title || '',
            brand: row.brand || row.manufacturer,
            price: Number(row.price ?? row.cost ?? undefined),
            currency: row.currency || 'USD',
            inStock: Boolean(row.inStock ?? row.available ?? false),
            url: row.url,
            imageUrl: row.image || row.imageUrl,
            ...row
        }));
        return { items, source: 'http' };
    }
}
//# sourceMappingURL=HttpPartsProvider.js.map