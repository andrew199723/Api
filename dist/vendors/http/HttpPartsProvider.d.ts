import type { PartsProvider, PartItem } from '../PartsProvider.js';
export declare class HttpPartsProvider implements PartsProvider {
    private readonly baseUrl;
    private readonly apiKey;
    constructor();
    searchByArticle(article: string): Promise<{
        items: PartItem[];
        source: string;
    }>;
}
//# sourceMappingURL=HttpPartsProvider.d.ts.map