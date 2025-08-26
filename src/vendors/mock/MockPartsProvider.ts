import { PartsProvider, PartItem } from '../PartsProvider.js';

const MOCK_DB: PartItem[] = [
	{ article: '123-ABC', name: 'Фильтр масляный', brand: 'Bosch', price: 12.5, currency: 'USD', inStock: true },
	{ article: '456-DEF', name: 'Свеча зажигания', brand: 'NGK', price: 8.9, currency: 'USD', inStock: true },
	{ article: 'ABC-789', name: 'Тормозные колодки', brand: 'ATE', price: 35.0, currency: 'USD', inStock: false },
];

export class MockPartsProvider implements PartsProvider {
	async searchByArticle(article: string) {
		const needle = article.toLowerCase();
		const items = MOCK_DB.filter(p => p.article.toLowerCase().includes(needle));
		return { items, source: 'mock' };
	}
}