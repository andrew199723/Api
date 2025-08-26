export type PartItem = {
	article: string;
	name: string;
	brand?: string;
	price?: number;
	currency?: string;
	inStock?: boolean;
	url?: string;
	imageUrl?: string;
	[extra: string]: unknown;
};

export interface PartsProvider {
	searchByArticle(article: string): Promise<{ items: PartItem[]; source: string }>;
}