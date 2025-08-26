import axios from 'axios';
import { PartsProvider, PartItem } from '../PartsProvider.js';

export class HttpPartsProvider implements PartsProvider {
	private readonly baseUrl: string;
	private readonly apiKey?: string;

	constructor() {
		this.baseUrl = process.env.API_BASE_URL || '';
		this.apiKey = process.env.API_KEY;
		if (!this.baseUrl) {
			throw new Error('API_BASE_URL is required for http provider');
		}
	}

	async searchByArticle(article: string): Promise<{ items: PartItem[]; source: string }> {
		const url = new URL('/search', this.baseUrl);
		url.searchParams.set('article', article);
		if (this.apiKey) url.searchParams.set('api_key', this.apiKey);

		const response = await axios.get(url.toString(), { timeout: 10000 });
		// Expecting response data normalization. Adjust mapping as per actual API.
		const items: PartItem[] = (response.data?.items || response.data?.results || []).map((row: any) => ({
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