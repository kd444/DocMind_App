"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchAnalysis } from "@/lib/api";

export default function AnalysisPage() {
    const [analysis, setAnalysis] = useState<any | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getAnalysis = async () => {
            try {
                const data = await fetchAnalysis();
                setAnalysis(data);
            } catch (err) {
                setError(
                    "An error occurred while fetching the analysis. Please try again later."
                );
                console.error("Fetch error:", err);
            } finally {
                setLoading(false);
            }
        };

        getAnalysis();
    }, []);

    const renderAnalysis = (analysis: any) => {
        try {
            const parsedAnalysis = analysis;

            return (
                <div className="space-y-6">
                    <h3 className="text-2xl font-semibold">Analysis Result</h3>
                    <p>
                        <strong>Filename:</strong> {parsedAnalysis.filename}
                    </p>

                    {/* Summaries Section */}
                    <div>
                        <h4 className="text-xl font-semibold mb-2">
                            Summaries
                        </h4>

                        {/* Custom BART Summary */}
                        <div className="mb-6">
                            <p className="font-semibold">
                                Custom BART Summary:
                            </p>
                            <div className="max-h-60 overflow-y-auto border p-4 rounded">
                                {parsedAnalysis.summary_bart}
                            </div>
                            <p className="mt-2">
                                <strong>Cosine Similarity (BART):</strong>{" "}
                                {parsedAnalysis.cosine_similarity_bart
                                    ? parsedAnalysis.cosine_similarity_bart.toFixed(
                                          4
                                      )
                                    : "Not Available"}
                            </p>
                        </div>

                        {/* T5 Summary */}
                        <div className="mb-6">
                            <p className="font-semibold">T5 Summary:</p>
                            <div className="max-h-60 overflow-y-auto border p-4 rounded">
                                {parsedAnalysis.summary_t5}
                            </div>
                            <p className="mt-2">
                                <strong>Cosine Similarity (T5):</strong>{" "}
                                {parsedAnalysis.cosine_similarity_t5
                                    ? parsedAnalysis.cosine_similarity_t5.toFixed(
                                          4
                                      )
                                    : "Not Available"}
                            </p>
                        </div>
                    </div>

                    {/* Statistics Section */}
                    <div>
                        <h4 className="text-xl font-semibold mb-2">
                            Statistics
                        </h4>
                        <p>
                            <strong>Word Count:</strong>{" "}
                            {parsedAnalysis.statistics.word_count}
                        </p>
                        <p>
                            <strong>Sentence Count:</strong>{" "}
                            {parsedAnalysis.statistics.sentence_count}
                        </p>
                        <p>
                            <strong>Compression Ratio (BART):</strong>{" "}
                            {parsedAnalysis.statistics.compression_ratio_bart
                                ? parsedAnalysis.statistics.compression_ratio_bart
                                      .toFixed(2)
                                      .replace(/^0\./, ".")
                                : "N/A"}
                        </p>
                        <p>
                            <strong>Compression Ratio (T5):</strong>{" "}
                            {parsedAnalysis.statistics.compression_ratio_t5
                                ? parsedAnalysis.statistics.compression_ratio_t5
                                      .toFixed(2)
                                      .replace(/^0\./, ".")
                                : "N/A"}
                        </p>
                    </div>
                </div>
            );
        } catch (error) {
            console.error("Error parsing analysis JSON:", error);
            return <p className="text-red-500">Error parsing analysis data.</p>;
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-6">Text Analysis</h1>
            <Card className="w-full">
                <CardHeader>
                    <CardTitle>Document Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <AnalysisSkeleton />
                    ) : error ? (
                        <p className="text-red-500">{error}</p>
                    ) : analysis ? (
                        renderAnalysis(analysis)
                    ) : (
                        <p className="text-gray-500">No analysis available.</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

function AnalysisSkeleton() {
    return (
        <div className="space-y-4">
            <div>
                <Skeleton className="h-4 w-1/4 mb-2" />
                <Skeleton className="h-4 w-3/4" />
            </div>
            <div>
                <Skeleton className="h-4 w-1/4 mb-2" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
            </div>
        </div>
    );
}
