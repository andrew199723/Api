import axios from 'axios';
import type { PartsProvider, PartItem } from '../PartsProvider.js';

export class HttpPartsProvider implements PartsProvider {
	private readonly baseUrl: string;
	private readonly apiKey: string | undefined;

	constructor() {
		this.baseUrl = process.env.API_BASE_URL || '';
		this.apiKey = process.env.API_KEY || undefined;
		if (!this.baseUrl) {
			throw new Error('API_BASE_URL is required for http provider');
		}
	}

	async searchByArticle(article: string): Promise<{ items: PartItem[]; source: string }> {
		const url = new URL('/search', this.baseUrl);
		url.searchParams.set('article', article);
		if (this.apiKey) url.searchParams.set('api_key', this.apiKey);

		const response = await axios.get(url.toString(), { timeout: 10000 });
		const raw = (response.data?.items || response.data?.results || []) as any[];
		const items: PartItem[] = raw.map((row: any) => ({
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