import { PartsProvider } from '../vendors/PartsProvider.js';
import { HttpPartsProvider } from '../vendors/http/HttpPartsProvider.js';
import { MockPartsProvider } from '../vendors/mock/MockPartsProvider.js';

function createProvider(): PartsProvider {
	const mode = (process.env.PROVIDER || 'mock').toLowerCase();
	if (mode === 'http') {
		return new HttpPartsProvider();
	}
	return new MockPartsProvider();
}

const provider = createProvider();

export async function getPartsByArticle(article: string) {
	return provider.searchByArticle(article);
}