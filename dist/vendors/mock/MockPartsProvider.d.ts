import type { PartsProvider, PartItem } from '../PartsProvider.js';
export declare class MockPartsProvider implements PartsProvider {
    searchByArticle(article: string): Promise<{
        items: PartItem[];
        source: string;
    }>;
}
//# sourceMappingURL=MockPartsProvider.d.ts.map