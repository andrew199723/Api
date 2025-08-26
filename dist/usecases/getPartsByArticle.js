import { HttpPartsProvider } from '../vendors/http/HttpPartsProvider.js';
import { MockPartsProvider } from '../vendors/mock/MockPartsProvider.js';
function createProvider() {
    const mode = (process.env.PROVIDER || 'mock').toLowerCase();
    if (mode === 'http') {
        return new HttpPartsProvider();
    }
    return new MockPartsProvider();
}
const provider = createProvider();
export async function getPartsByArticle(article) {
    return provider.searchByArticle(article);
}
//# sourceMappingURL=getPartsByArticle.js.map